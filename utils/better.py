from ast import literal_eval
from fileinput import filename
import os
import pandas as pd
import numpy as np
import json

class Reasoner (object):
    def __init__(self) -> None:
        super().__init__()
        self.diseaselist = ['abnormal', 'normal', 'lung opacity', 'atelectasis', 'pleural effusion', 'vascular congestion', 'pulmonary edema/hazy opacity',
                    'low lung volumes', 'pneumonia', 'endotracheal tube', 'enlarged cardiac silhouette', 'aspiration', 'linear/patchy atelectasis',
                    'vascular calcification', 'tortuous aorta', 'pleural/parenchymal scarring', 'consolidation', 'fluid overload/heart failure',
                    'mass/nodule (not otherwise specified)', 'copd/emphysema', 'hyperaeration', 'airspace opacity', 'lobar/segmental collapse',
                    'enlarged hilum', 'calcified nodule']
        self.organs = ["right lung", "right apical zone", "right upper lung zone", "right mid lung zone", 
                    "right lower lung zone", "right hilar structures", "right costophrenic angle", "left lung", "left apical zone",
                    "left upper lung zone", "left mid lung zone", "left lower lung zone", "left hilar structures", 
                    "left costophrenic angle", "mediastinum", "upper mediastinum", "cardiac silhouette", "trachea"]

        print("loading data ...")
        
        self.data = pd.read_csv('./DensenetModel.csv', sep='\t')

        # self.data = pd.read_csv('better.csv', sep='\t')
        self.data_size = len(self.data)
        print(self.data_size)
        print("Done loading data ...")
    

    def reasoner(self, row):
        #abnormal and any other condition
        att = row['objects']
        diseases = literal_eval(row['output'])
        normal = diseases.pop(1)
        if (normal == 1) and (1 in diseases):
            index_list = [i for i, x in enumerate(diseases) if x == 1]
            res_list = [self.diseaselist[i] for i in index_list]
            print ("Patient's {} cannot be normal and also have {} attributes: ".format(att, str(res_list)))

    '''
    The Conditional Probability of A (disease row) given B (disease Column)
    P(A|B) = P(AnB)/P(B)
    '''
    def findings(self):
        # filename = os.path.join(self.outputdir, 'findings_matrix.csv')
        filename = './adjacency.csv'
        error = 1e-9
        row = self.diseaselist
        column = self.diseaselist
        adj_matrix = []
        counts = []
        for ind, B in enumerate(row):
            print("Processing {} from row {}".format(B, str(ind)))
            rows = np.zeros([len(self.diseaselist)])
            c = []
            for inde, A in enumerate(column):
                # print("Processing {} from column {}".format(A, str(inde)))
                AnB_count = 0
                B_count = 0
                for index, row in self.data.iterrows():
                    output = literal_eval(row['output'])
                    # output = literal_eval(row['target'])
                    if output[ind] == 1:
                        B_count += 1
                    if (output[inde] == 1) and (output[ind] == 1):
                        AnB_count += 1
                
                p_anb = AnB_count/self.data_size
                p_b = B_count/self.data_size
                a_given_b = p_anb / (p_b + error)*100
                # if a_given_b > 0.4:
                #     a_given_b = 1
                # else:
                #     a_given_b = 0
                rows[inde] = round(a_given_b, 2)
                # percent = (AnB_count/(B_count + error))*100
                c.append((B_count,AnB_count))
                # c.append(round(percent, 2))
            adj_matrix.append(rows.tolist())
            counts.append(c)
            # print(rows)
            # print(c)
            if ind == 1:
                break

        # print(adj_matrix)
        # print(counts)
        df = pd.DataFrame(adj_matrix, columns=self.diseaselist)
        df.to_csv(filename, sep='\t', index=False)
        df2 = pd.DataFrame(counts, columns=self.diseaselist)
        print(df2)
        print(df)
        df2.to_csv('counts.csv', sep='\t', index=False)
        return df2
    
    def better(self):
        data = pd.read_csv('DensenetModel.csv', sep='\t')
        better = []
        for index, row in data.iterrows():
            if (row['output'] != row['target']):
                better.append(True)
            else:
                better.append(False)


        data['better'] = better
        print(data.head(5))

        df = data.loc[data['better'] == True]
        df = df.reset_index(drop=True)
        df.to_csv('better.csv', sep='\t', index=False)
    
    def anatomy(self):
        disease = {i:0 for i in self.diseaselist}
        anatomy = {j:disease.copy() for j in self.organs}
        
        print("counting anatomy error ...")
        for index, row in self.data.iterrows():
            output = literal_eval(row['output'])
            # for dis, val in zip(self.diseaselist, output):
            for ind, val in enumerate(output):
                if val:
                    dis = self.diseaselist[ind]
                    # print(row['objects'])
                    # print(dis)
                    anatomy[row['objects']][dis] += int(val)
                    if row['objects'] == 'cardiac silhouette' and dis == 'atelectasis':
                        print(row['image_id'])

                # if row['objects']=='cardiac silhouette' and dis == 'lung opacity':
                #     print(row['image_id'])
            # if index == 5:
            #     break
        # print(anatomy)
        print("done counting anatomy errors")
        
        print("saving file ...")
        filename = 'anatomy_target.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(anatomy, f, ensure_ascii=False, indent=4)
        print("done saving file ...")

if __name__=='__main__':
    patient = Reasoner()
    findings = patient.anatomy()
    # findings = patient.findings()
    # findings = patient.better()

        

