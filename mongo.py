from dataclasses import dataclass
import random
import string
import json
import difflib
import itertools
from bson import json_util
from pymongo import MongoClient
import re

class Mongo:

    def __init__(self, parsedQuery):
        self.parsedQuery = parsedQuery
        self.client = MongoClient()
        self.db = self.client['apartment']
        self.collection = self.db[self.parsedQuery['collection']]

    def get(self):
        ##print(self.parsedQuery)
        result = {}
        try:
            queryPath = self.parsedQuery['queryPath']
        except:
            result['status'] = False
            return result

        limit = None
        sortBy = None
        ascending = 1

        if len(queryPath) == 0 and 'orderBy' in self.parsedQuery:
            orderBy = self.parsedQuery['orderBy'].strip('"')
            if orderBy == "$key":
                indexFound = True
            
            else:
                all_indexes = self.collection.index_information()
                indexFound = False

                for index in all_indexes:
                    try:
                        if str(orderBy).strip() in str(index).strip():
                            indexFound = True
                            break
                    except:
                        pass
            
            if not indexFound:
                result['status'] = True
                result['doc'] = 'Index not set on ' + str(orderBy)
                return result
            
            if orderBy != "$key":
                sortBy = orderBy

        if 'limitToFirst' in self.parsedQuery:
            limit = int(self.parsedQuery['limitToFirst'].strip('"'))
        
        if 'limitToLast' in self.parsedQuery:
            limit = int(self.parsedQuery['limitToLast'].strip('"'))
            ascending = -1

        equalTo = None
        startAt = None
        endAt = None
        if 'equalTo' in self.parsedQuery:
            equalTo = self.parsedQuery['equalTo'].strip('"')
        if 'startAt' in self.parsedQuery:
            startAt = self.parsedQuery['startAt'].strip('"')
        if 'endAt' in self.parsedQuery:
            endAt = self.parsedQuery['endAt'].strip('"')

        
        # ##print('Sort', orderBy)
        finalOutput = []
        if len(queryPath) == 0:
            if sortBy and limit:
                docCursor = self.collection.find().sort(sortBy, ascending).limit(limit)
            elif sortBy:
                docCursor = self.collection.find().sort(sortBy, ascending)
            else:
                docCursor = self.collection.find()

            for doc in docCursor:
                docID = doc["_id"]
                if sortBy == "$key":
                    temp = doc[str(docID)]
                    temp.sort()
                    doc[str(docID)] = temp
                
                if equalTo is not None:
                    temp = doc[str(docID)]
                    try:
                        if temp[orderBy] != equalTo:
                            continue
                    except:
                        continue
                if startAt is not None:
                    temp = doc[str(docID)]
                    try:
                        if str(temp[orderBy]) < str(startAt):
                            continue
                    except:
                        continue

                if endAt is not None:
                    temp = doc[str(docID)]
                    try:
                        if str(temp[orderBy]) > str(endAt):
                            continue
                    except:
                        continue
                finalOutput.append(doc[str(docID)])
            jsonDoc = json_util.dumps(docCursor)
            result['status'] = True
            result['doc'] = finalOutput
            return result

        
        try:
            id = int(queryPath[0])
        except:
            result['status'] = False
            return result
        
        
        doc = self.collection.find_one({'_id': id})

        if not doc:
            result['status'] = False
            return result   
        doc = doc[str(id)]
        queryPath.pop(0)
        for attribute in queryPath:
            
            if isinstance(doc, dict) and attribute not in doc:
                result['status'] = False
                return result     
            
            if isinstance(doc, list):
                try:
                    attribute = int(attribute)
                except:
                    result['status'] = False
                    return result  

            doc = doc[attribute]
        
        sortByKey = False
        if 'orderBy' in self.parsedQuery:
            orderBy =  self.parsedQuery['orderBy'].strip('"')
            ##print('ORRR', orderBy)
            if orderBy == "$key":
                ##print("HEREEEEEEE")
                sortByKey = True
            if sortByKey:
                doc = dict(sorted(doc.items()))
                if 'limitToFirst' in self.parsedQuery:
                    limit = int(self.parsedQuery['limitToFirst'].strip('"'))
                    doc = dict(itertools.islice(doc.items(), limit))
                elif 'limitToLast' in self.parsedQuery:
                    limit = int(self.parsedQuery['limitToLast'].strip('"'))
                    doc = dict(list(doc.items())[-limit:])


        result['status'] = True
        result['doc'] = doc
        ##print('DOCCCCC', doc)
        return result

    def put(self):

        result = {}
        try:
            queryPath = self.parsedQuery['queryPath']
        except:
            result['status'] = False
            return result

        if len(queryPath) == 0:
            ##print("Here")
            try:
                data = self.parsedQuery['data']
                temp = data.copy()
                new_data = {}
                
                if "_id" not in data:
                    new_data["_id"] = 0
                    new_data["0"] = temp
                else:
                    new_data["_id"] = temp["_id"]
                    del temp["_id"]
                
                new_data[str(new_data["_id"])] = temp

                self.collection.delete_many({})
                self.collection.insert_one(new_data) 
                result['status'] = True
                result['doc'] = new_data
            except:
                result['status'] = False

            return result  

        try:
            id = int(queryPath[0])
        except:
            result['status'] = False
            return result

        queryPath.pop(0)
        # try:
        data = self.parsedQuery['data']

        keyToUpdate = str(id)
        if len(queryPath) > 0:
            keyToUpdate += '.'+'.'.join(queryPath)

        ##print('KTU', id, keyToUpdate, data)

        self.collection.update_one(
            {"_id": id},
            {"$set": {keyToUpdate: data}},
            upsert=True
        )

        result['status'] = True
        result['doc'] = data
        return result


    def post(self):
        unique_key = '-' + ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        queryPath = self.parsedQuery['queryPath']
        queryPath.append(unique_key)
        self.parsedQuery['queryPath'] = queryPath
        result = self.put()
        if result['status']:
            doc = {"name":unique_key}
            result['doc'] = doc
        
        return result


    def patch(self):

        data = self.parsedQuery['data']
        queryPath = self.parsedQuery['queryPath'].copy()
        result = {'status':False}

        result_internal = self.get()

        if  result_internal['status']:        
            self.parsedQuery['queryPath'] = queryPath.copy()
            if isinstance(result_internal['doc'], str):
                ##print('QP', self.parsedQuery)
                result = self.put()
                return result

        for key, val in data.items():
            new_data = val
            new_key = queryPath.copy()
            new_key.append(key)
            self.parsedQuery['data'] = new_data
            self.parsedQuery['queryPath'] = new_key
            result = self.put()
            if not result['status']:
                return result
        
        result['doc'] = data
        return result
            
    def delete(self):

        result = {}
        try:
            queryPath = self.parsedQuery['queryPath']
        except:
            result['status'] = False
            return result

        try:
            id = int(queryPath[0])
        except:
            result['status'] = False
            return result

        queryPath.pop(0)

        keyToDelete = str(id)
        if len(queryPath) > 0:
            keyToDelete += '.'+'.'.join(queryPath)
        else:
            try:
                self.collection.delete_one({"_id":id})
                result['status'] = True
            except:
                result['status'] = False
            
            return result
            
        deleteValue = { "$unset": { keyToDelete: "" } }

        try:
            self.collection.update_one(
                {"_id":id}, 
                deleteValue)
        except:
            result['status'] = False
            return result

        result['status'] = True
        return result


    def createIndex(self):
        data = self.parsedQuery['data']
        queryPath = self.parsedQuery['queryPath'].copy()
        result = {'status':True}
        ##print(data)
        indexField = re.sub(r'/', '.', data['.indexOn'])
        ##print('IE', indexField)
        try:
            self.collection.create_index([(indexField, 1)])
        except:
            result['status'] = False
            return result 
        
        result['doc'] = "Index created on " + str(indexField)
        return result