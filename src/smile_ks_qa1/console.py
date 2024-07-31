from owlready2 import default_world,onto_path, ObjectProperty, DataProperty, rdfs, Thing 
onto_path.append('./smile_ks_qa1/ontology_cache/')
import re, os, tqdm

from smile_ks_qa1.listener import Qa1Ner, Text, Trace, Ks, KSAR, Program, Organization, Phrase, Hypothesis, BeneficialStakeholder, Sentence
from smile_ks_qa1.utils import add_ks
from py2graphdb.config import config as CONFIG
from py2graphdb.utils.db_utils import resolve_nm_for_dict, PropertyList, _resolve_nm
from py2graphdb.ontology.namespaces import ic, geo, cids, org, time, schema, sch, activity, landuse_50872, owl
from py2graphdb.ontology.operators import *
from smile_base.utils import init_db

if not os.path.exists(CONFIG.LOG_DIR):
    os.makedirs(CONFIG.LOG_DIR)

smile = default_world.get_ontology(CONFIG.NM)
