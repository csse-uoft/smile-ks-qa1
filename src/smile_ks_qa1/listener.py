import re, os, tqdm, pprint
from owlready2 import default_world, onto_path, ObjectProperty, DataProperty, rdfs, Thing 
onto_path.append('./ontology_cache/')
from py2graphdb.config import config as CONFIG
smile = default_world.get_ontology(CONFIG.NM)
with smile:
    from py2graphdb.Models.graph_node import GraphNode, SPARQLDict
    from py2graphdb.utils.db_utils import resolve_nm_for_dict, PropertyList

    from smile_base.Model.knowledge_source.knowledge_source import KnowledgeSource
    from qawrapper.qa1 import QA1
    from smile_base.Model.data_level.cids.organization import Organization
    from smile_base.Model.data_level.cids.service import Service
    from smile_base.Model.data_level.cids.program import Program
    from smile_base.Model.data_level.cids.beneficial_stakeholder import BeneficialStakeholder
    from smile_base.Model.data_level.cids.outcome import Outcome
    # from smile_base.Model.data_level.CatchmentArea"         : 'catchment_area',

    from smile_base.Model.data_level.org_certainty import OrgCertainty
    from smile_base.Model.data_level.phrase import Phrase
    from smile_base.Model.data_level.text import Text
    from smile_base.Model.data_level.sentence import Sentence
    from smile_base.Model.data_level.hypothesis import Hypothesis
    from smile_base.Model.controller.ks import Ks
    from smile_base.Model.controller.ks_ar import KSAR
    from smile_base.Model.controller.trace import Trace
    from smile_ks_qa1.utils import add_ks

from py2graphdb.ontology.operators import *

# from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tokenize.punkt import PunktSentenceTokenizer
import time
from py2graphdb.utils.misc_lib import *

class Qa1Ner(KnowledgeSource):
    """
    A knowledge source class that processes QA1 Ner

    Attributes
    ----------
    description: str
        context description that will be the input of the model
    entity: str
        entity in interest
    qa1s: qa1.QA1
        qa1 use case module instance that keeps track of all qa flow
    output_dic: dict
        dictionary representation of the knowledge source outputs

    Methods
    -------
    set_input(description)
        set inputs to the model class, preparing to run the model
    get_outputs()
        run the model to get the formatted outputs

    """
    current_trace = None
    current_ks_ar = None

    MAPPINGS = {
        # Organization          : 'program_name',
        Program               : 'program_name',
        Service               : 'need_satisfier',
        # Client                : 'client',
        BeneficialStakeholder : 'client',
        # NeedSatisfier         : 'need_satisfier',
        Outcome               : 'outcome',
        # StakleholderOutcome   : 'stakeholder_outcome',
        # CatchmentArea         : 'catchment_area',
    }
    QA1.ENTITIES = list(set(MAPPINGS.values()))

    def __init__(self, hypothesis_ids, ks_ar, trace):
        fields = [v for v in Ks.ALL_KS_FORMATS.values() if v[0] == self.__class__.__name__][0]
        super().__init__(fields[1], fields[2], fields[3], trace, hypothesis_ids, ks_ar)

        self.description = None
        self.entity = None
        self.qa1s = None
        self.output_dic = {}
        # TODO: update below
        
    @classmethod
    def process_ks_ars(cls, loop=True):
        """
        A class method that processes all the ks_ars with py_name='Qa1Ner' and status=0.

        :param cls: The class itself (implicit parameter).
        :type cls: type
        :return: None
        """
        while True:
            # Hard coded to get the ks_ar with id=4           
            # Get the ks_ar with py_name='Qa1Ner' and status=0
            time.sleep(1)
            kss = Ks.search(props={smile.hasPyName:f"Qa1Ner"}, how='all')
            ks_ar = None
            for ks in kss:
                ks_ars = KSAR.search(props={smile.hasKS:ks.id, smile.hasKSARStatus:0}, how='first')
                if len(ks_ars) > 0:
                    ks_ar = ks_ars[0]
                    break
                    
            if ks_ar is None:
                continue

            print(f"Processing ks_ar with id: {ks_ar.id}")
            # Get the trace from the ks_ar
            trace = Trace(inst_id=ks_ar.trace)
            cls.current_trace = trace
            cls.current_ks_ar = ks_ar
            # Get the hypothesis ids from the ks_ar
            in_hypo_ids = ks_ar.input_hypotheses

            if len(in_hypo_ids) < 2 :
                raise(Exception(f"Bad Input Hypothesis Count {len(in_hypo_ids)}"))

            in_hypos = [Hypothesis(inst_id=hypo_id).cast_to_graph_type() for hypo_id in in_hypo_ids]
            content_hypo = None
            concept_hypo = None
            for in_hypo in in_hypos:
                if isinstance(in_hypo, (smile.Sentence, smile.Text)): #check if Phrase
                    content_hypo = in_hypo
                elif type(in_hypo) in cls.MAPPINGS.keys(): #check if Concept
                    concept_hypo = in_hypo
            if concept_hypo is None or content_hypo is None:
                raise(Exception(f"Bad Input Hypothesis Type {[type(in_hypo) for in_hypo in in_hypos]}"))
            
            
            # Construct an instance of the ks_object
            ks_object = cls(hypothesis_ids=in_hypo_ids, ks_ar=ks_ar, trace=trace)
            
            # Call ks_object.set_input() with the necessary parameters
            ks_ar.ks_status = 1
            output_klass = eval(ks.outputs[0])
            in_content = Phrase(concept_hypo.phrase).content
            ks_object.set_input(description=content_hypo.content, in_hypo=concept_hypo, in_content=in_content, output_klass=output_klass)

            ks_ar.ks_status = 2
            hypotheses = ks_object.get_outputs()
            ks_ar.keep_db_in_synch = False
            trace.keep_db_in_synch = False
            for hypo in hypotheses:
                ks_ar.hypotheses = hypo.id 
                trace.hypotheses = hypo.id
                if isinstance(hypo, (smile.Word, smile.Phrase)):
                    if isinstance(content_hypo, smile.Sentence):
                        hypo.sentence = content_hypo.id
                    elif isinstance(content_hypo, smile.Text):
                        hypo.text = content_hypo.id
                    if isinstance(hypo, smile.Phrase):
                        content_hypo.phrases = hypo.id
                    elif isinstance(hypo, smile.Word):
                        content_hypo.words = hypo.id
            ks_ar.save()
            trace.save()
            ks_ar.keep_db_in_synch = True
            trace.keep_db_in_synch = True

            LOG_FILE_TEMPLATE = CONFIG.LOG_DIR+'smile_trace_log.txt'
            filename = LOG_FILE_TEMPLATE.replace('.txt', f"_{trace.id}.txt")
            ks_ar.summary(filename=filename, method_info=ks_object.method_info)

            ks_ar.ks_status = 3
            cls.current_trace = None
            cls.current_ks_ar = None
            if not loop:
                return ks_ar
                
    def set_input(self, description:str, in_hypo, in_content, output_klass):
        """Run qa1 ner knowledge source with the given description (str).
        :param description: context description
        :return: updated qa1 object
        """
        input_klass = type(in_hypo)
        self.store_hypotheses = []
        self.qa1s = {}
        self.output_results = []
        self.description = description
        self.method_info = ''
        in_entity = self.MAPPINGS[input_klass]
        out_entity = self.MAPPINGS[output_klass]
        qa_instance = QA1(context=description, out_entity=out_entity)
        qa_instance.update_given_ner(in_entity=in_entity, givens={in_content:in_hypo.certainty})

        qa_res = qa_instance.run_qa()
        self.method_info += f"Input ID:\t{in_hypo.id.split('-')[0]}\n" + f"\tClass:\t{in_hypo.klass}\n" + f"\tInfo:\t{in_hypo.show()}\n"+f"\tCertainty:\t{round(in_hypo.certainty,5) if in_hypo.certainty == in_hypo.certainty else in_hypo.certainty}" + "\n"
        self.method_info += pprint.pformat(qa_instance.QAs) + "\n"
        self.output_results.append(qa_res)

        return self.output_results

    def get_outputs(self):
        """
        add newly created hypothese to database
        :return: all the hypotheses created from this ks
        """
        for res_dict in self.output_results:
            for out_entity,res_qa1 in res_dict.items():
                text = res_qa1["answer"]
                start = res_qa1["start"]
                end = res_qa1["end"]
                new_certainty = res_qa1["score"]
                if round(new_certainty,3) > 0:
                    phrase = Phrase.find_generate(
                        content=text, start=start, end=end,trace_id=self.trace.id, certainty=new_certainty)
                    phrase.from_ks_ars = self.ks_ar.id

                    klass = [k for k,v in self.MAPPINGS.items() if v == out_entity][0]
                    concept = klass.find_generate(phrase_id=phrase.id, trace_id=self.trace.id, certainty=new_certainty)
                    concept.from_ks_ars = self.ks_ar.id
                    phrase.concepts = concept.id

                    org_certainty = OrgCertainty.generate(hypothesis_id=concept.id, ks_ar_id = self.ks_ar.id, trace_id=self.trace.id, certainty=new_certainty)
                    self.ks_ar.org_certainties = org_certainty.id
                    concept.org_certainties = org_certainty.id

                    self.store_hypotheses.append(phrase)
                    self.store_hypotheses.append(concept)

        return self.store_hypotheses





if __name__ == '__main__':
    print('Qa1Ner script started')
    add_ks.add_ks(reload_db=False)
    print('Qa1Ner script ready')

    with smile:
        while True:
            try:
                Qa1Ner.process_ks_ars(loop=True)
            except KeyboardInterrupt:
                print('interrupted!')
                break
            except Exception as e:
                print(f"{type(e)}: {e}")
                if Qa1Ner.current_ks_ar is not None:
                    failed_ks_ar = Qa1Ner.current_ks_ar
                    org_status = failed_ks_ar.ks_status
                    failed_ks_ar.ks_status = -1
                    failed_ks_ar.save()
                    error_message = f"Failed KSAF(Qa1Ner, cycle={failed_ks_ar.cycle})): {failed_ks_ar} with ks_status={org_status}"
                    print(error_message)
                if Qa1Ner.current_trace is not None:
                    Qa1Ner.logger(trace_id=Qa1Ner.current_trace, text=error_message)
                pass
