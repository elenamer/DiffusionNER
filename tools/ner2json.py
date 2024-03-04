import json

noise_types =['clean','noisy_mv','noisy_bond']
file_type = ["train", "dev", "test"]
wf_type = open(f"conll03_types.json","w")
types={"entities":{},"relations":{}}
#original_path = '/vol/home-vol2/ml/merdjane/ControlledNoiseNLPBenchmark/data/noisyCoNLL'
original_path='../data/noisyCoNLL'

ner_column_id = 1

for noisy_ty in noise_types:
    for ty in  file_type:
        if ty == 'test' and noisy_ty != 'clean':
            continue
        rf = open(f"{original_path}/conll_{noisy_ty}.{ty}")
        wf = open(f"conll03_{noisy_ty}_{ty}.json","w")
        
        datasets = []
        sample = {"tokens": [], "entities": [], "relations": []}
        idx = 0
        doc_id = 0
        start = end = None
        entity_type = None

        for line in rf:
            line = line.strip()
            if "DOCSTART" in line: # sep string
                doc_id += 1
                continue
            if line:
                last = idx
                fields = list(filter(lambda x:x,line.replace(' ','\t').split("\t")))
                sample["tokens"].append(fields[0])
                sample["orig_id"] = str(doc_id)
                if fields[ner_column_id].startswith("B-"):
                    if start!=None and end!=None and end == idx:
                        sample["entities"].append({"start":start,"end":end,"type":entity_type})
                    start = idx
                    end = idx + 1
                    entity_type = fields[ner_column_id][2:]
                    if entity_type not in types["entities"]:
                        types["entities"][entity_type]={"verbose": entity_type,"short": entity_type}
                if fields[ner_column_id].startswith("I-"):
                        end = end + 1
                if fields[ner_column_id]=="O" and start!=None:
                    sample["entities"].append({"start":start,"end":end,"type":entity_type})
                    start = end = entity_type = None
                idx += 1
            else:
                if start!=None:
                    sample["entities"].append({"start":start,"end":end,"type":entity_type})
                    
                idx = 0
                start = end = None
                entity_type = None
                if len(sample["tokens"]):
                    datasets.append(sample)
                
                sample = {"tokens": [], "entities": [], "relations": []}
        if len(sample["tokens"]):
            datasets.append(sample)    
        print(len(datasets))
        json.dump(datasets,wf)

print(len(types["entities"].keys()))
json.dump(types,wf_type)
