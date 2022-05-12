import json
import pandas as pd
import numpy as np
import os
# from json2rdf import PatientKG
import re


class ViTData(object):
    def __init__(self) -> None:
        
        self.organs = ["right lung", "right apical zone", "right hilar structures", "right costophrenic angle", 
        "left lung", "left apical zone", "left hilar structures", "left costophrenic angle", "mediastinum", 
        "upper mediastinum", "cardiac silhouette", "trachea", " right hemidiaphragm", "left hemidiaphragm", 
        "right clavicle", "left clavicle,"]

        self.filename = './../data/VQA_RAD.json'
        self.splits = '/Users/nneka/Downloads/subset-3/splits/'
        self.rootdir = '/Users/nneka/Downloads/subset-3/test/'
        self.imageroot = '/home/agun/mimic/dataset/VG/data/'
        self.path = '/home/agun/mimic/dataset/VG/ViTdata'
        self.diseaselist = ['lung opacity', 'pleural effusion', 'atelectasis', 'enlarged cardiac silhouette',
        'pulmonary edema/hazy opacity', 'pneumothorax', 'consolidation', 'fluid overload/heart failure', 'pneumonia']

        # if not os.path.exists(self.path):
        #     # Create a new directory because it does not exist 
        #     os.makedirs(self.path)

    def ImageData(self):
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
                        dis.append(row.tolist())
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
        df.to_csv("./../data/yes_no_table.csv", sep='\t', index=False)
        return df
    

# tables = ViTData()
# data = tables.ImageData()
# print(data)

def text2json(filename):
    with open(filename) as fh:
        data = fh.read().replace('\n', '')
        result = re.search('FINDINGS:(.*)IMPRESSION', data)#.group(1)
        if result is not None:
            result = result.group(1)
            temp = re.sub(r'[^\w\s_]+', '', result).strip()
            output = temp.lower()
            lenght = len(output.split(' '))
            if lenght <= 200:
                print(lenght)
                return output
        else:
            result = re.search('IMPRESSION:(.*)', data)
            if result is not None:
                result = result.group(1)
                temp = re.sub(r'[^\w\s_]+', '', result).strip()
                output = temp.lower()
                lenght = len(output.split(' '))
                if lenght <= 200:
                    print(lenght)
                    return output
        # else:
    return None
        # return result

filename = '/Users/nneka/Downloads/MIMIC-CXR/p10/p10000032/s56699142.txt'
result = text2json(filename)
print(result)

# import glob
# import os
# import shutil

# def copy(src, dest):
#     for file_path in glob.glob(os.path.join(src, '**', '*.txt'), recursive=True):
#         new_path = os.path.join(dest, os.path.basename(file_path))
#         shutil.copy(file_path, new_path)

# src = '/Users/nneka/Downloads/MIMIC-CXR/'
# dest = '/Users/nneka/Downloads/MIMIC-CXR-Reports/'

# copy(src, dest)
