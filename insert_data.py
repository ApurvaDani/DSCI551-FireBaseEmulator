import json
import pymongo


client = pymongo.MongoClient('mongodb://localhost:27017/')

# Create a new database and collection
db = client['apartment']
collection = db['listings']

# Open the JSON file and load its contents
with open('./data/apartment.json', 'r') as file:
    data = json.load(file)

# Insert the data into the collection
collection.insert_many(data)

# Close the MongoDB connection
client.close()