import json
import pandas as pd
import numpy as np
import os
from json2rdf import PatientKG
import re


class createTables(object):
    def __init__(self) -> None:
        
        self.organs = ["right lung", "right apical zone", "right hilar structures", "right costophrenic angle", 
        "left lung", "left apical zone", "left hilar structures", "left costophrenic angle", "mediastinum", 
        "upper mediastinum", "cardiac silhouette", "trachea", " right hemidiaphragm", "left hemidiaphragm", 
        "right clavicle", "left clavicle,"]

        self.filename = './../data/VQA_RAD.json'
        self.splits = '/Users/nneka/Downloads/subset-3/splits/'
        self.rootdir = '/Users/nneka/Downloads/subset-3/test/'
        self.diseaselist = ['lung opacity', 'pleural effusion', 'atelectasis', 'enlarged cardiac silhouette',
        'pulmonary edema/hazy opacity', 'pneumothorax', 'consolidation', 'fluid overload/heart failure', 'pneumonia']


    def TransformerData(self):
        imageIDs = []
        labels = []
        prevImg = []
        studies = []
        
        for file in os.listdir(self.rootdir):
            if 'DS_Store' not in file:
                myfile = file + '_SceneGraph.json'
                filename = os.path.join(self.rootdir, file)
                try:
                    f = open(str(filename),) 
                except FileNotFoundError:
                    print('{} not in directory'.format(myfile))
                else:
                    data = json.load(f)
                    imageID = data['image_id']
                    prevImageID = data['image_id']
                    study_id = data['study_id']
                    attr = []
                    dis = []
                    for attribute in data['attributes']:
                        attr.append(attribute['bbox_name'])
                    for organs in self.organs:
                        row = np.zeros([len(self.diseaselist)])
                        if organs in attr:
                            for attribute in data['attributes']:
                                for diseases in attribute['attributes']:
                                    for disease in diseases:
                                        if disease.split('|')[2] in self.diseaselist:
                                            class_index = self.diseaselist.index(disease.split('|')[2])
                                            if disease.split('|')[1] == 'yes':
                                                row[class_index] = int(1)                            
                        dis.append(row)
                    y=np.array(dis)
                    print(y)
                    for relationship in data['relationships']:
                        prevImageID = relationship['object_id'].split('_')[0]
                labels.append(dis)
                imageIDs.append(imageID)
                prevImg.append(prevImageID)
                studies.append(study_id)
        df = pd.DataFrame(
                {
                    'StudyID': studies,
                    'ImageID': imageIDs,
                    'PrevImageID': prevImg,
                    'Disease': labels
                }
            )
        df.to_csv("../data/yes_no_table.csv", sep='\t', index=False)
        return df
    
    def yes_no_table(self):
        imageIDs = []
        labels = []
        
        for file in os.listdir(self.rootdir):
            if 'DS_Store' not in file:
                myfile = file + '_SceneGraph.json'
                filename = os.path.join(self.rootdir, file)
                try:
                    f = open(str(filename),) 
                except FileNotFoundError:
                    print('{} not in directory'.format(myfile))
                else:
                    data = json.load(f)
                    imageID = data['image_id']
                    row = np.zeros([len(self.diseaselist)])
                    for attribute in data['attributes']:
                        row = np.zeros([len(self.diseaselist)])
                        for diseases in attribute['attributes']:
                            for disease in diseases:
                                if disease.split('|')[2] in self.diseaselist:
                                    class_index = self.diseaselist.index(disease.split('|')[2])
                                    if disease.split('|')[1] == 'yes':
                                        row[class_index] = int(1)
                labels.append(row)
                imageIDs.append(imageID)
        df = pd.DataFrame(labels, columns = self.diseaselist)
        df['imageID'] = imageIDs
        df.to_csv("../data/yes_no_table.csv", sep='\t', index=False)
        return df

    def location_table(self):
        imageIDs = []
        labels = []
        
        for file in os.listdir(self.rootdir):
            if 'DS_Store' not in file:
                myfile = file + '_SceneGraph.json'
                filename = os.path.join(self.rootdir, file)
                try:
                    f = open(str(filename),) 
                except FileNotFoundError:
                    print('{} not in directory'.format(myfile))
                else:
                    data = json.load(f)
                    imageID = data['image_id']
                    for attribute in data['attributes']:
                        anatomy = attribute['bbox_name']

    def anatomyProb(self):
        anatomy = []
        hasdisease = []
        
        for file in os.listdir(self.rootdir):
            if 'DS_Store' not in file:
                myfile = file + '_SceneGraph.json'
                filename = os.path.join(self.rootdir, file)
                try:
                    f = open(str(filename),) 
                except FileNotFoundError:
                    print('{} not in directory'.format(myfile))
                else:
                    data = json.load(f)
                    imageID = data['image_id']
                    for attribute in data['attributes']:
                        name = attribute['object_id'].split('_')[-1]
                        for diseases in attribute['attributes']:
                            for disease in diseases:
                                if disease.split('|')[2] in self.diseaselist:
                                    if disease.split('|')[1] == 'yes':
                                        anatomy.append(name)
                                        hasdisease.append(disease.split('|')[2])
        df = pd.DataFrame(
                {
                    'anatomy': anatomy,
                    'disease': hasdisease
                }
            )
        grouped_df = df.groupby('anatomy')
        keys = []
        items = []
        for key, item in grouped_df:
            keys.append(key)
            items.append(list(set(item['disease'].tolist())))
        df2 = pd.DataFrame(
                {
                    'anatomy': keys,
                    'disease': items
                }
            )
        return df2


    def kg_to_text(self):
        imgID = []
        anatomies = []
        kgs = []
        text = []
        
        for file in os.listdir(self.rootdir):
            if 'DS_Store' not in file:
                myfile = file + '_SceneGraph.json'
                filename = os.path.join(self.rootdir, file)
                try:
                    f = open(str(filename),) 
                except FileNotFoundError:
                    print('{} not in directory'.format(myfile))
                else:
                    data = json.load(f)
                    imageID = data['image_id']
                    patient = PatientKG()
                    graph = patient.newGraph(filename)
                    
                    for attribute in data['attributes']:
                        anatomy = attribute['bbox_name']
                        phrases = attribute['phrases']
                        phrases2 = []
                        phrase2 = [re.findall(r'\w+', i.lower()) for i in phrases]
                        for phrase in phrase2:
                            phrases2.append(re.sub(' +', ' ', ' '.join(phrase).replace('_', '')))

                        subG = graph[anatomy]
                        context2 = patient.generateContext(subG)
                        context = '. '.join(context2)
                        phrasess = '. '.join(phrases2)
                        imgID.append(imageID)
                        anatomies.append(anatomy)
                        kgs.append(context)
                        text.append(phrasess)
                        
        df = pd.DataFrame(
                {
                    'ImageID': imgID,
                    'Anatomy': anatomies,
                    'KGs': kgs,
                    'phrases': text
                }
            )
        df.to_csv("../data/kg_to_text.csv", sep='\t', index=False)
        return df

tables = createTables()
data = tables.TransformerData()
print(data)
