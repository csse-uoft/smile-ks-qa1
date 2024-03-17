from owlready2 import default_world,onto_path, ObjectProperty, DataProperty, rdfs, Thing 
onto_path.append('./smile_ks_qa1/ontology_cache/')
import re, os, tqdm

from src.smile_ks_qa1.qa1_ner_listener import Qa1Ner, Text, Trace, Ks, KSAR, Program, Organization, Phrase, Hypothesis, BeneficialStakeholder
from smile_ks_qa1.utils import add_ks
from py2graphdb.config import config as CONFIG
from py2graphdb.utils.db_utils import resolve_nm_for_dict, PropertyList, _resolve_nm
from py2graphdb.ontology.namespaces import ic, geo, cids, org, time, schema, sch, activity, landuse_50872, owl
from py2graphdb.ontology.operators import *
from smile_base.utils import init_db

if not os.path.exists(CONFIG.LOG_DIR):
    os.makedirs(CONFIG.LOG_DIR)

def gen_ksar(inputs:list, output, trace:Trace):
    input_klasses = [hypo.klass for hypo in inputs]
    ks = Ks.search(props={smile.hasPyName:'Qa1Ner', hasall(smile.hasInputDataLevels):input_klasses, smile.hasOutputDataLevels:output.klass}, how='first')[0]
    ks_ar = KSAR()
    ks_ar.keep_db_in_synch = False
    ks_ar.ks = ks.id
    ks_ar.trace = trace.id
    ks_ar.cycle = 0
    for hypo in inputs:
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
    # description = "St.Mary's Church is focused on raising well rounded and spiritually sound youths and teenagers, equipping them with what it takes to overcome the daily pressures of the society. They have separate meeting during our services."
    # entity = "client"
    # qa1 = QA1(description, entity)
    # qa1.update_given_ner(ent_type="outcome", givens={"well rounded and spiritually sound youths and teenagers": 0.5})
    # qa1.update_given_ner(ent_type="program_name", givens={"St.Mary's Church": 0.5})
    # print(qa1.given)
    # output_dic = qa1.run_qa(ner=True)

    description = "St.Mary's Church provides hot meals and addiction support to homeless youth. Their services are offered to those living in downtown Toronto. Family services are provided to homeless families. These include housing supports and family care. Only families living in the west side of the city are eligible."
    trace = Trace(keep_db_in_synch=True)

    text = Text.find_generate(content=description, trace_id=trace.id)
    text.save()
    phrase = Phrase.find_generate(content="St. Mary's Church", trace_id=trace.id,)
    phrase.save()
    program = Program.find_generate(phrase_id=phrase.id, trace_id=trace.id)
    program.save()
    ks_ar = gen_ksar(inputs=[text, program], output=BeneficialStakeholder, trace=trace)
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