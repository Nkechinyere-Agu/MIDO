import json

filename = '/Users/nneka/Downloads/3rd year phd/ISWC/semantics/label_to_UMLS_mapping.json'
diseaselist = ['abnormal', 'normal', 'lung opacity', 'atelectasis', 'pleural effusion', 'vascular congestion', 'pulmonary edema/hazy opacity',
                    'low lung volumes', 'pneumonia', 'endotracheal tube', 'enlarged cardiac silhouette', 'aspiration', 'linear/patchy atelectasis',
                    'vascular calcification', 'tortuous aorta', 'pleural/parenchymal scarring', 'consolidation', 'fluid overload/heart failure',
                    'mass/nodule (not otherwise specified)', 'copd/emphysema', 'hyperaeration', 'airspace opacity', 'lobar/segmental collapse',
                    'enlarged hilum', 'calcified nodule']

organs = ["right lung", "right apical zone", "right upper lung zone", "right mid lung zone", "aortic arch", "neck", "left hemidiaphragm", 'right cardiophrenic angle',
                    "right lower lung zone", "right hilar structures", "right costophrenic angle", "left lung", "left apical zone", 'left cardiophrenic angle',
                    "left upper lung zone", "left mid lung zone", "left lower lung zone", "left hilar structures", 'right hemidiaphragm', 'descending aorta',
                    "left costophrenic angle", "mediastinum", "upper mediastinum", "cardiac silhouette", "trachea", 'carina', 'left clavicle', 'right clavicle']


try:
    f = open(str(filename),) 
except FileNotFoundError:
    print('{} not Found'.format(filename))
else:
    data = json.load(f)
    # print(data.keys())
    d_data = {}
    a_data = {i:[] for i in organs}
    for att in data['possible_attribute_of']:
        if att in diseaselist:
            d_data[att] = data['possible_attribute_of'][att]
    for d in d_data:
        for val in d_data[d]:
            print(val)
            a_data[val].append(d)
    
    print("saving file ...")
    filename = 'rules.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(a_data, f, ensure_ascii=False, indent=4)
    print("done saving file ...")
    print(a_data)
    print(data.keys())
    print(data['possible_attribute_of']['lung opacity'])