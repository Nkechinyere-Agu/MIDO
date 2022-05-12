from rdflib import BNode, Literal, Namespace, Graph
from rdflib.namespace import FOAF, XSD, RDF
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph, rdflib_to_networkx_digraph
# import networkx as nx
from random import shuffle
from ast import literal_eval
import os
import pandas as pd
import json

class PatientKG (object):
    def __init__(self) -> None:
        super().__init__()
        self.diseaselist = ['abnormal', 'normal', 'lung opacity', 'atelectasis', 'pleural effusion', 'vascular congestion', 'pulmonary edema/hazy opacity',
                    'low lung volumes', 'pneumonia', 'endotracheal tube', 'enlarged cardiac silhouette', 'aspiration', 'linear/patchy atelectasis',
                    'vascular calcification', 'tortuous aorta', 'pleural/parenchymal scarring', 'consolidation', 'fluid overload/heart failure',
                    'mass/nodule (not otherwise specified)', 'copd/emphysema', 'hyperaeration', 'airspace opacity', 'lobar/segmental collapse',
                    'enlarged hilum', 'calcified nodule']
        
    
    def newGraph(self, filename):
        AIDAS = Namespace('http://aidas.org/')

        mido = Namespace('https://bioportal.bioontology.org/ontologies/MIDO/')
        ddo = Namespace('http://purl.obolibrary.org/obo/DDO.owl#')
        radlex = Namespace('radlex.org/RID/RadLex.owl/')
        ncit = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
        symp = Namespace('http://purl.obolibrary.org/obo/symp.owl/')
        ogms = Namespace('http://purl.obolibrary.org/obo/OGMS_0000031/')
        prov = Namespace('https://www.w3.org/TR/prov-o/')
        doid = Namespace('http://purl.obolibrary.org/obo/doid#')
        
        filename = filename

        KGs = {}
        try:
            patient = pd.read_csv('patient.csv', sep='\t')
            patient[['output', 'target']].to_numpy()
        except FileNotFoundError:
            print('{} not in directory'.format(filename))
        else:
            g = Graph()
            # data = json.load(f)
        
            patientProfile = ddo['demographic']#BNode()
            # age = Literal(data['age_decile'], datatype=XSD['string'])
            imageID = Literal(patient['image_id'][0], datatype=XSD['string'])
            patientID = Literal(patient['image_id'][0], datatype=XSD['string'])
            # gender = Literal(data['gender'], datatype=XSD['string'])
            # StudyDateTime = Literal(data['StudyDateTime'], datatype=XSD['datetime'])

            g.add((patientID, RDF.type, ncit['Patient']))
            g.add((patientID, ddo['hasDemographics'], patientProfile))
            # g.add((patientProfile, CXRO['hasAge'], age))
            g.add((patientProfile, mido['hasID'], patientID))
            # g.add((patientProfile, CXRO['hasGender'], gender))
            g.add((patientID, ddo['hasLaboratoryTest'], ogms['LaboratoryTest']))
            g.add((ogms['LaboratoryTest'], ddo['hasReport'], radlex['Report']))
            g.add((radlex['Report'], mido['hasID'], imageID))
            # g.add((CXRO['cxrReport'], PROV['wasGeneratedAtTime'], StudyDateTime))

            # for attribute in data['attributes']:
            for index, row in patient.iterrows():
                att = row['objects'].replace(' ', '_')
                name = row['objects']
                g.add((patientID, mido['hasAttribute'], mido[att]))
                g.add((mido[att], RDF.type, mido['AnatomicalRegion']))

                patient = PatientKG()
                #create subgraph
                subG = patient.subGraph(row)
                #reason over sub graph
                patient.reasoner(row)
                KGs[name] = subG
                g += subG
                # print(subG.serialize())
            
            g.bind('ddo', ddo)
            g.bind('RadLex', radlex)
            g.bind('mido', mido)
            g.bind('ogms', ogms)
            g.bind('ncit', ncit)
            g.bind('prov', prov)

            KGs['full KG'] = g
        # g = g.serialize(format='turtle')
        # g = g.serialize()
        return g


    def subGraph(self, attribute):
        mido = Namespace('https://bioportal.bioontology.org/ontologies/MIDO/')
        ddo = Namespace('http://purl.obolibrary.org/obo/DDO.owl#')
        radlex = Namespace('radlex.org/RID/RadLex.owl/')
        ncit = Namespace('http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#')
        symp = Namespace('http://purl.obolibrary.org/obo/symp.owl/')
        ogms = Namespace('http://purl.obolibrary.org/obo/OGMS_0000031/')
        prov = Namespace('https://www.w3.org/TR/prov-o/')
        doid = Namespace('http://purl.obolibrary.org/obo/doid#')

        g = Graph()
        att = attribute['objects'].replace(' ', '_')
        positive = Literal('Positive', datatype=XSD['string'])
        negative = Literal('Negative', datatype=XSD['string'])
        # print(attribute['output'])
        att = literal_eval(attribute['output'])
        for index, disease in enumerate(att):
            # print(disease)
            if disease == 1:
                dis = self.diseaselist[index]
                dis = dis.replace(' ', '_')
                # find = disease.split('|')[0]
                g.add((radlex['Report'], mido['hasFinding'], mido[dis]))
                # g.add((CXRO[dis], RDF.type, CXRO[find]))
                g.add((mido[dis], prov['value'], positive))
                g.add((mido[dis], prov['wasAssociatedWith'], mido[att]))
            # elif disease == 0:
            #     dis = self.diseaselist[index]
            #     dis = dis.replace(' ', '_')
            #     # find = disease.split('|')[0]
            #     g.add((radlex['Report'], mido['hasFinding'], mido[dis]))
            #     # g.add((CXRO[dis], RDF.type, CXRO[find]))
            #     g.add((mido[dis], prov['value'], negative))
            #     g.add((mido[dis], prov['wasAssociatedWith'], mido[att]))
        return g
    
    def reasoner(self, row):
        #abnormal and any other condition
        att = row['objects']
        diseases = literal_eval(row['output'])
        normal = diseases.pop(1)
        if (normal == 1) and (1 in diseases):
            index_list = [i for i, x in enumerate(diseases) if x == 1]
            res_list = [self.diseaselist[i] for i in index_list]
            print ("Patient's {} cannot be normal and also have {} attributes: ".format(att, str(res_list)))

    def generateContext(self, rdfgraph):
        context = []
        for s,p,o in rdfgraph:
            sen = s.split('/')[-1].replace('_', ' ')
            sen += ' ' + p.split('/')[-1].replace('_', ' ').split('#')[-1]
            sen += ' ' + o.split('/')[-1].replace('_', ' ')
            context.append(sen)
        shuffle(context)
        return context

    def randomwalk(self, rdfgraph):
        G = rdflib_to_networkx_digraph(rdfgraph)
        all_paths = nx.all_pairs_shortest_path(G)
        # print(len(G))
        return all_paths

if __name__=='__main__':
    filename = '/Users/nneka/Downloads/3rd year phd/ISWC/Code/data/patient.csv'
    patient = PatientKG()
    g = patient.newGraph(filename)
    g.serialize(destination="patient.ttl")


