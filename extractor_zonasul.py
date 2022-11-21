from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from vendor import opensearch
from vendor import sqs
from vendor import mongo
import time
import logging
import configparser
import ast
import traceback

def extract_product_info(product_sku):
    zonasul_sku_search = "https://www.zonasul.com.br/{0}".format(product_sku)
    opts = webdriver.ChromeOptions()
    opts.add_argument("--window-size=2560,1440")

    driver = webdriver.Chrome(executable_path="./chromedriver",options=opts)
    driver.get(zonasul_sku_search)

    try:
        page_contents = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vtex-flex-layout-0-x-flexCol--contentDesktop"))
        )
        
        # targeting only the first element found with such class, maybe in the future I want to get all of them
        product = driver.find_element(By.CLASS_NAME, "vtex-search-result-3-x-galleryItem")
        product.click()

        # wait for product details, which means the page is full loaded
        results = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vtex-flex-layout-0-x-flexColChild--details-product-main"))
        )

        product_name = driver.find_element(By.CLASS_NAME, "vtex-store-components-3-x-productBrand").text

        # In the product type path (under the top menu) usually the type of the product has many levels ans sub groups, here
        # the script gets the most granular (last) because its easier
        product_type_path = driver.find_elements(By.CLASS_NAME, "vtex-breadcrumb-1-x-link")
        product_type = product_type_path[-2].text
        return (product_name, product_type, product_sku)
    except NoSuchElementException:
        raise
    except TimeoutException:
        not_found = driver.find_element(By.CLASS_NAME, "vtex-search-result-3-x-searchNotFound")
        return None
    except Exception as e:
        logging.error(traceback.format_exc())
        logging.error("Failed extraction for product {0}".format(product_sku))
    finally:
        driver.quit()

def fail_processing(error_message, message):
    logging.error(error_message)
    sqs.send_one_message(config["sqs"]["hortifruti_error_queue_url"], message)

if __name__ == "__main__":
    logging.basicConfig()
    # logging.root.setLevel(logging.NOTSET)

    config = configparser.ConfigParser()
    config.read("config.ini")

    while True:
        try:
            message = None
            product_message = None
            product = None
            logging.info("Waiting for message in queue")
            message = sqs.get_one_message(config["sqs"]["zonasul_queue_url"])

            overall_start_time = time.time()
            product_message = ast.literal_eval(message['Body'])
            logging.debug(product_message)

            extract_start_time = time.time()
            product = extract_product_info(product_message["product"])
            logging.debug(product)
            extract_time = (time.time() - extract_start_time)*1000

            if not product:
                fail_processing("Product wasn't found or market website with error", str(product_message))
                overall_time = (time.time() - overall_start_time)*1000
                opensearch_save_time = 0
                mongo_product_save_time = 0
                mongo_receipt_update_time = 0
                continue

            # In opensearch saving the product with all data needed
            opensearch_save_start_time = time.time()
            logging.info("Create opensearch index if doesn't exists")
            opensearch.create_index(
                host=config["opensearch"]["Host"],
                port=config["opensearch"]["Port"],
                user=config["opensearch"]["User"],
                password=config["opensearch"]["Password"],
                index_name='products',
                mapping={
                    "mappings" : {
                        "properties" :  {
                            "datetime" : {
                                "type" : "date",
                                "format" : "dd/MM/yyyy HH:mm:ss"
                            }
                        }
                    }
                }
            )
            logging.info("Save product info to opensearch")
            opensearch.save_to_opensearch(
                host=config["opensearch"]["Host"],
                port=config["opensearch"]["Port"],
                user=config["opensearch"]["User"],
                password=config["opensearch"]["Password"],
                index_name='products',
                data=product
            )
            opensearch_save_time = (time.time() - opensearch_save_start_time)*1000

            # In mongo saving only metadata about the product (no data related to a specific receipt)
            logging.info("Search if product already exists")
            mongo_product_save_start_time = time.time()
            result = mongo.count_items(
                uri=config["mongodb"]["ConnString"],
                database=config["mongodb"]["Database"],
                collection="products",
                data={
                    "product_name": product["product_name"],
                    "product_code": product["product_code"],
                    "store": product["store"]
                }
            )
            if result == 0:
                logging.info("Save product metadata to mongo")
                mongo_product = dict()
                mongo_product["product_name"] = product["product_name"]
                mongo_product["product_code"] = product["product_code"]
                # TODO: unit test when product details extraction fails 
                mongo_product["product_type"] = "" or product.get("product_type")
                mongo_product["unity_type"] = product["unity_type"]
                mongo_product["store"] = product["store"]
                mongo_product_id = mongo.save_to_mongo(
                    uri=config["mongodb"]["ConnString"],
                    database=config["mongodb"]["Database"],
                    collection="products",
                    data=mongo_product
                )
                #print("product saved", mongo_product_id)
                product["product_id"] = mongo_product_id
            elif result > 1:
                logging.warning("Alert: duplicated product")
                #TODO raise exception
            else:
                logging.info("Product already exists, skipping")
                mongo_product = mongo.search_item(
                    uri=config["mongodb"]["ConnString"],
                    database=config["mongodb"]["Database"],
                    collection="products",
                    data={
                        "product_name": product["product_name"],
                        "product_code": product["product_code"],
                        "store": product["store"]
                    }
                )
                product["product_id"] = mongo_product[0]["_id"]
            mongo_product_save_time = (time.time() - mongo_product_save_start_time)*1000
            
            # update product id in receipt object in mongo along with other specific info of the purchase
            receipt_url = product_message["receipt_url"]
            mongo_receipt_update_start_time = time.time()
            mongo_result = mongo.update_item(
                uri=config["mongodb"]["ConnString"],
                database=config["mongodb"]["Database"],
                collection="receipts",
                filter={"url": receipt_url},
                change={"$push": {
                            "products": {
                                "product_id": product["product_id"],
                                "product_quantity": product["product_quantity"],
                                "unity_type": product["unity_type"],
                                "total_value": product["total_value"]
                            }
                        }
                    }
            )
            mongo_receipt_update_time = (time.time() - mongo_receipt_update_start_time)*1000
            overall_time = (time.time() - overall_start_time)*1000
        except Exception as e:
            logging.error(traceback.format_exc())
            fail_processing("An error ocurred during processing of the product", str(product_message))
            continue
        finally:
            logging.debug("Removing message from queue after processing")
            if message:
                sqs.delete_message(config["sqs"]["hortifruti_queue_url"], message["ReceiptHandle"])

            columns = ["full_extraction", "product_extraction", "opensearch_save", "mongo_product_save", "mongo_receipt_update"]
            with open('hortifruti_extractor_metrics.csv', 'a', newline='') as f:
                csvwriter = csv.DictWriter(f, fieldnames=columns)
                metrics = {
                    "full_extraction": str(overall_time),
                    "product_extraction": str(extract_time),
                    "opensearch_save": str(opensearch_save_time),
                    "mongo_product_save": str(mongo_product_save_time),
                    "mongo_receipt_update": str(mongo_receipt_update_time)
                }
                #csvwriter.writeheader()
                csvwriter.writerow(metrics)