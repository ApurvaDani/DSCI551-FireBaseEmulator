import pandas as pd
import json
import re
import math

df = pd.read_csv('./data/apartment.csv')

json_data = []
array_key = {"additional_facilities", "facilities"}
count_inserted = 0
for index, row in df.iterrows():

    mini_json = {}
    for key, val in row.iteritems():
        if pd.isna(val):
            continue
        if key in array_key and ',' in str(val):
            val = val.split()
            new_val = {}
            for i in range(len(val)):
                val[i] = val[i].strip(',')  
                val[i] = re.sub(r'[\'\"]', " ", val[i]) 
                new_val[i] = val[i]
            val = new_val

        elif isinstance(val, str):
            val = re.sub(r'[\'\"]', " ", val) 
        
        if isinstance(key, str) and len(key) > 0 and val is not None and val != 'NaN':
            mini_json[key] = val
    
    if len(mini_json) > 0:
        new_json = {}
        new_json['_id'] = count_inserted
        new_json[count_inserted] = mini_json
        for key, val in mini_json.items():
            new_json[key] = val
        # mini_json['_id'] = count_inserted
        count_inserted += 1
        json_data.append(new_json)

with open("./data/apartment.json", "w") as outfile:
    json.dump(json_data, outfile)

fireBase = {}
with open("./data/apartmentFirebase.json", "w") as outfile:
    fireBase['apartments'] = json_data
    json.dump(fireBase, outfile)