# DSCI551-FireBaseEmulator

## Dataset
Download this dataset in csv format and save it in the data folder in this repository
```
https://www.kaggle.com/datasets/ariewijaya/rent-pricing-kuala-lumpur-malaysi
```

## Convert dataset to json file
Run the below command to convert csv to json format. This will save a new json file in the data folder
```
python csvJson.py
```

## Load the json file to MongoDB
Run the below command to load this json file to mongoDB database
```
python insert_data.py
```

## Run the server
```
python server.py
```

## Some queries you could run
```
curl -X GET 'http://localhost:5050/listings/0.json
```
```
curl -X PATCH -H "Content-Type: application/json" -d '{".indexOn": "rooms"}' 'http://localhost:5050/listings/rooms.json
```
```
curl -X POST -H "Content-Type: application/json" -d '{"newFacility":"pool table"}' 'http://localhost:5050/listings/1/facilities.json
```
```
curl -X DELETE http://localhost:5050/listings/1/additional_facilities.json
```
