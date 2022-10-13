from pymongo import MongoClient
#from pymongo import errors.ConnectionFailure

def save_to_mongo(uri, database, collection, data):
    mongodb_client = MongoClient(uri)
    
    try:
        mongo_database = mongodb_client[database]
        mongo_collection = mongo_database[collection]

        insert_response = mongo_collection.insert_one(data)
        return insert_response.inserted_id
    except Exception as e:
        print(e)
        raise
    finally:
        mongodb_client.close()

def search_item(uri, database, collection, data):
    mongodb_client = MongoClient(uri)
    
    try:
        mongo_database = mongodb_client[database]
        mongo_collection = mongo_database[collection]

        product_result = mongo_collection.find(data)
        return list(product_result)
    except Exception as e:
        print(e)
        raise
    finally:
        mongodb_client.close()
        
def count_items(uri, database, collection, data):
    mongodb_client = MongoClient(uri)
    
    try:
        mongo_database = mongodb_client[database]
        mongo_collection = mongo_database[collection]

        product_result = mongo_collection.count_documents(data)
        return product_result
    except Exception as e:
        print(e)
        raise
    finally:
        mongodb_client.close()