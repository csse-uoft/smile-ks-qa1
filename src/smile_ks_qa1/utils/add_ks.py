import re, os, tqdm
from owlready2 import default_world, onto_path, ObjectProperty, DataProperty, rdfs, Thing 
onto_path.append('./ontology_cache/')
from py2graphdb.config import config as CONFIG
smile = default_world.get_ontology(CONFIG.NM)
with smile:
    from smile_base.Model.controller.ks import Ks

def add_ks():
    ALL_KS_FORMATS = {}
    ALL_KS_FORMATS['QA-1 (Organization,Text)(Program)'] = ['Qa1Ner', False, ["Text", "Organization"], ["Program"]]
    ALL_KS_FORMATS['QA-1 (Organization,Sentence)(Program)'] = ['Qa1Ner', False, ["Sentence", "Organization"], ["Program"]]
    ALL_KS_FORMATS['QA-1 (Organization,Text)(BeneficialStakeholder)'] = ['Qa1Ner', False, ["Text", "Organization"], ["BeneficialStakeholder"]]
    ALL_KS_FORMATS['QA-1 (Organization,Sentence)(BeneficialStakeholder)'] = ['Qa1Ner', False, ["Sentence", "Organization"], ["BeneficialStakeholder"]]
    # Ks.ALL_KS_FORMATS['QA-1 (Organization)(Client)'] = ['Qa1Ner_Organization_Client', False, ["Text", "Sentence", "Organization"], ["Client"]]
    # Ks.ALL_KS_FORMATS['QA-1 (Organization)(BeneficialStakeholder)'] = ['Qa1Ner_Organization_BeneficialStakeholder', False, ["Text", "Sentence", "Organization"], ["BeneficialStakeholder"]]
    # Ks.ALL_KS_FORMATS['QA-1 (Organization)(Outcome)'] = ['Qa1Ner_Organization_Outcome', False, ["Text", "Sentence", "Organization"], ["Outcome"]]
    # Ks.ALL_KS_FORMATS['QA-1 (Organization)(CatchmentArea)'] = ['Qa1Ner_Organization_CatchmentArea', False, ["Text", "Sentence", "Organization"], ["CatchmentArea"]]


    ALL_KS_FORMATS['QA-1 (Program,Text)(Organization)'] = ['Qa1Ner', False, ["Text", "Program"], ["Organization"]]
    ALL_KS_FORMATS['QA-1 (Program,Sentence)(Organization)'] = ['Qa1Ner', False, ["Sentence", "Program"], ["Organization"]]
    ALL_KS_FORMATS['QA-1 (Program,Text)(BeneficialStakeholder)'] = ['Qa1Ner', False, ["Text", "Program"], ["BeneficialStakeholder"]]
    ALL_KS_FORMATS['QA-1 (Program,Sentence)(BeneficialStakeholder)'] = ['Qa1Ner', False, ["Sentence", "Program"], ["BeneficialStakeholder"]]
    # Ks.ALL_KS_FORMATS['QA-1 (Program)(Client)'] = ['Qa1Ner_Program_Client', False, ["Text", "Sentence", "Program"], ["Client"]]
    # Ks.ALL_KS_FORMATS['QA-1 (Program)(BeneficialStakeholder)'] = ['Qa1Ner_Program_BeneficialStakeholder', False, ["Text", "Sentence", "Program"], ["BeneficialStakeholder"]]
    # Ks.ALL_KS_FORMATS['QA-1 (Program)(Outcome)'] = ['Qa1Ner_Program_Outcome', False, ["Text", "Sentence", "Program"], ["Outcome"]]
    # Ks.ALL_KS_FORMATS['QA-1 (Program)(CatchmentArea)'] = ['Qa1Ner_Program_CatchmentArea', False, ["Text", "Sentence", "Program"], ["CatchmentArea"]]

    for ks_name, fields in ALL_KS_FORMATS.items():
        Ks.ALL_KS_FORMATS[ks_name] = fields
    for ks_name in ALL_KS_FORMATS.keys():
        Ks.initialize_ks(ks_name)

