import re
from flask import Flask, request
from query import Query
from mongo import Mongo
from pymongo import MongoClient

app = Flask(__name__)

@app.route('/<path:x>', methods=['GET'])
def route_get(x):
    params = request.args
    if len(params) > 0 and 'orderBy' not in params:
        return {"error": "orderBy must be defined when other query parameters are defined"}
    query = Query(x)
    parsedQuery = query.parseQuery()
    print(params)
    if not parsedQuery['status']:
        return "null"

    for key, val in params.items():
        parsedQuery[key] = val

    mongodb = Mongo(parsedQuery)
    result = mongodb.get()
    if not result['status']:
        return "null"

    return result['doc']

@app.route('/<path:x>', methods=['PUT'])
def route_put(x):
    print('Request received in put')
    data = request.get_json()
    query = Query(x)
    parsedQuery = query.parseQuery()
    print('PQ', parsedQuery)
    if not parsedQuery['status']:
        return "null"

    data = query.listToDict(data)
    parsedQuery['data'] = data
    mongodb = Mongo(parsedQuery) 
    result = mongodb.put()

    if not result['status']:
        return "null"
    
    return result['doc']

@app.route('/<path:x>', methods=['POST'])
def route_post(x):
    print('Request received in post')
    data = request.get_json()
    query = Query(x)
    parsedQuery = query.parseQuery()
    print('PQ', parsedQuery)
    if not parsedQuery['status']:
        return "null"

    data = query.listToDict(data)
    parsedQuery['data'] = data
    mongodb = Mongo(parsedQuery) 
    result = mongodb.post()

    if not result['status']:
        return "null"
    
    return result['doc']

@app.route('/<path:x>', methods=['PATCH'])
def route_patch(x):
    print('Request received in patch')
    data = request.get_json()
    query = Query(x)
    parsedQuery = query.parseQuery()
    if not parsedQuery['status']:
        return "null"
    data = query.listToDict(data)
    parsedQuery['data'] = data
    mongodb = Mongo(parsedQuery)

    if '.indexOn' in data:
        result = mongodb.createIndex()
    else:
        result = mongodb.patch() 

    if not result['status']:
        return "null"
    
    return result['doc']

# @app.route('/<path:x>', methods=['POST'])
# def route_post(x):
#     return "post"

# @app.route('/<path:x>', methods=['PATCH'])
# def route(x):
#     return "patch"

@app.route('/<path:x>', methods=['DELETE'])
def route_delete(x):
    
    query = Query(x)
    parsedQuery = query.parseQuery()
    print('PQ', parsedQuery)
    if not parsedQuery['status']:
        return "null"

    mongodb = Mongo(parsedQuery) 
    result = mongodb.delete()

    if result['status']:
        return "null"
    
    return "null"

# curl -X GET 'http://localhost:5050/apartments/200.json
    
if __name__ == "__main__":
    app.run(port=5050, debug=True)