from owlready2 import default_world,onto_path, ObjectProperty, DataProperty, rdfs, Thing 
onto_path.append('./smile_ks_qa1/ontology_cache/')
import re, os, tqdm

from smile_ks_qa1.listener import SPARQLDict, Qa1Ner, Text, Trace, Ks, KSAR, Program, Organization, Phrase, Hypothesis, BeneficialStakeholder, Sentence
from smile_ks_qa1.utils import add_ks
from py2graphdb.config import config as CONFIG
from py2graphdb.utils.db_utils import resolve_nm_for_dict, PropertyList, _resolve_nm
from py2graphdb.ontology.namespaces import ic, geo, cids, org, time, schema, sch, activity, landuse_50872, owl
from py2graphdb.ontology.operators import *
from smile_base.utils import init_db
import itertools as itert
if not os.path.exists(CONFIG.LOG_DIR):
    os.makedirs(CONFIG.LOG_DIR)

def gen_ksar(hypothesis:Hypothesis, output, trace:Trace):
    input_klasses = [hypothesis.klass]
    for ks in Ks.search(props={smile.hasPyName:'Qa1Ner', smile.hasInputDataLevels:hypothesis.klass}):
        targets = list(set(ks.inputs).difference(input_klasses))
        matches = {}
        for ks_input in targets:
             res = SPARQLDict._process_path_request(start=sentence, end=ks_input, action='collect', direction='children', how='all', infer=True)
             if len(res)>0:
                 matches[ks_input] = [r['path'][-1] for r in res]
        if len(set(targets.keys())).intesection(matches) == len(targets.keys()):
            for inputs in itert.product(*matches.values()):
                ks_ar = KSAR()
                ks_ar.keep_db_in_synch = False
                ks_ar.ks = ks.id
                ks_ar.trace = trace.id
                ks_ar.cycle = 0
                for hypo in [hypothesis]+ [Hypothesis(id) for id in inputs]:
                    ks_ar.input_hypotheses = hypo.id
                    hypo.for_ks_ars = ks_ar.inst_id

                ks_ar.save()
                ks_ar.keep_db_in_synch = True
    return ks_ar


smile = default_world.get_ontology(CONFIG.NM)
with smile:
    init_db.init_db()
    add_ks.add_ks()
    init_db.load_owl('./ontology_cache/cids.ttl')

    description = "St.Mary's Church provides hot meals and addiction support to homeless youth. Their services are offered to those living in downtown Toronto. Family services are provided to homeless families. These include housing supports and family care. Only families living in the west side of the city are eligible."
    trace = Trace(keep_db_in_synch=True)

    sentence= Sentence.find_generate(content=description, trace_id=trace.id, index=0)
    sentence.save()
    phrase = Phrase.find_generate(content="St. Mary's Church", trace_id=trace.id,)
    phrase.save()
    sentence.phrases = phrase.id
    program = Program.find_generate(phrase_id=phrase.id, trace_id=trace.id)
    program.save()
    phrase.concepts = program.id



    ks_ar = gen_ksar(hypothesis=sentence, output=BeneficialStakeholder, trace=trace)
    ks_ar.ks_status=0
    ks_ar.save()

with smile:
    ks_ar = Qa1Ner.process_ks_ars(loop=False)
    ks_ar.load()
    outs = [Hypothesis(inst_id=hypo_id).cast_to_graph_type() for hypo_id in ks_ar.hypotheses]
    for out in outs:
        try:
            print(out, out.content)
            for concept_id in out.concepts:
                concept = Hypothesis(concept_id).cast_to_graph_type()
                print("\t", concept.certainty, concept.klass)
        except:
            pass