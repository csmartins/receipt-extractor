import logging
from pymongo import MongoClient
#from pymongo import errors.ConnectionFailure

logger = logging.getLogger(__name__)


def save_to_mongo(uri, database, collection, data):
    mongodb_client = MongoClient(uri)
    logger.debug("Connection to mongo initiated")    
    try:
        mongo_database = mongodb_client[database]
        mongo_collection = mongo_database[collection]
        
        logger.debug("Insert data to collection")
        insert_response = mongo_collection.insert_one(data)
        return insert_response.inserted_id
    except Exception as e:
        logger.exception(e)
        raise
    finally:
        mongodb_client.close()
        logger.debug("Connection to mongo closed")

def search_item(uri, database, collection, data):
    mongodb_client = MongoClient(uri)
    logger.debug("Connection to mongo initiated")
    try:
        mongo_database = mongodb_client[database]
        mongo_collection = mongo_database[collection]

        logger.debug("Find data in collection")
        product_result = mongo_collection.find(data)
        return list(product_result)
    except Exception as e:
        logger.exception(e)
        raise
    finally:
        mongodb_client.close()
        logger.debug("Connection to mongo closed")
        
def count_items(uri, database, collection, data):
    mongodb_client = MongoClient(uri)
    logger.debug("Connection to mongo initiated")
    try:
        mongo_database = mongodb_client[database]
        mongo_collection = mongo_database[collection]

        logger.debug("Counting documents")
        product_result = mongo_collection.count_documents(data)
        return product_result
    except Exception as e:
        logger.exception(e)
        raise
    finally:
        mongodb_client.close()
        logger.debug("Connection to mongo closed")

def update_item(uri, database, collection, filter, change):
    mongodb_client = MongoClient(uri)
    logger.debug("Connection to mongo initiated")
    try:
        mongo_database = mongodb_client[database]
        mongo_collection = mongo_database[collection]

        logger.debug("Update document in collection")
        product_result = mongo_collection.update_one(filter=filter, update=change)
        return product_result
    except Exception as e:
        logger.exception(e)
        raise
    finally:
        mongodb_client.close()
        logger.debug("Connection to mongo closed")