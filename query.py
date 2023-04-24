class Query:

    def __init__(self, query, collection='listings'):
        self.query = query
        self.collection = collection

    def parseQuery(self):
        
        parseResult = {}
        
        if not isinstance(self.query, str) or len(self.query) == 0:
            parseResult['status'] = False
            return parseResult

        querySplit = self.query.split('/')
        
        if '.json' in querySplit[0]:
            if len(querySplit) == 1:
                parseResult['collection'] = querySplit[0].split('.')[0]
                parseResult['status'] = True
                parseResult['queryPath'] = []
                return parseResult
            else:
                parseResult['status'] = False
                return parseResult   


        parseResult['collection'] = querySplit[0]

        querySplit.pop(0)
        queryPath = []
        queryPathIndex = None
        foundotJson = False
        
        for index in range(len(querySplit)):

            queryPathIndex = index 
            if not foundotJson:
                if '.json' in querySplit[index]:
                    foundotJson = True
                    val = querySplit[index].split('.')
                    if len(val) < 2 and val[-1] != '.json':
                        parseResult['status'] = False
                        return parseResult
                    else:
                        queryPath.append(val[0])
                    break
                
                else:
                    queryPath.append(querySplit[index])

        print('QPPP', queryPath)
        if len(queryPath) == 0:
            parseResult['status'] = False
            return parseResult    
        
        parseResult['queryPath'] = queryPath
        parseResult['status'] = True
        return parseResult


    def verifyCollection(self, collection):
        if self.collection == collection:
            return True
        else:
            return False

    def listToDict(self, data):

        for key, val in data.items():
            if isinstance(val, list):
                mini_dict = {}
                for index in range(len(val)):
                    mini_dict[index] = val[index]
                data[key] = mini_dict
            elif isinstance(val, dict):
                data[key] = self.listToDict(val)
        
        return data