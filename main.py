from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from vendor import mongo
from vendor import sqs

import configparser
import csv
import logging
import ast



def get_table_line(driver, tr_id):
    line = driver.find_element(By.ID, tr_id)
    
    product_name = line.find_element(By.CLASS_NAME, "txtTit").text
    
    raw_product_code = line.find_element(By.CLASS_NAME, "RCod").text
    product_code = raw_product_code.split(" ")[1]

    raw_product_quantity = line.find_element(By.CLASS_NAME, "Rqtd").text
    product_quantity = raw_product_quantity.split(".:")[1]

    raw_unity_type = line.find_element(By.CLASS_NAME, "RUN").text
    unity_type = raw_unity_type.split(": ")[1]

    raw_unity_value = line.find_element(By.CLASS_NAME, "RvlUnit").text
    unity_value = raw_unity_value.split(".:   ")[1]

    total_value = line.find_element(By.CLASS_NAME, "valor").text

    product = dict()
    product["product_name"] = product_name
    product["product_code"] = product_code
    product["product_quantity"] = product_quantity
    product["unity_type"] = unity_type
    product["unity_value"] = unity_value
    product["total_value"] = total_value
    return product

def save_to_csv(receipts):
    columns = ["product_name","product_type","product_code","product_quantity","unity_type","unity_value","total_value","url","store","total","payment","datetime"]
    try:
        with open("receipts.csv", 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns)
            writer.writeheader()
            for receipt in receipts:
                writer.writerow(receipt)
    except IOError:
        print("I/O error")

def get_payment_method(driver):
    try:
        # try first the path when receipt has discounts
        payment_method = driver.find_element(By.XPATH, "/html[@class='ui-mobile']/body[@class='ui-mobile-viewport ui-overlay-a']/div[@class='ui-page ui-page-theme-a ui-page-active']/div[@class='ui-content']/div[@id='conteudo']/div[@id='totalNota']/div[@id='linhaTotal'][5]/label[@class='tx']")
    except NoSuchElementException:
        # if fails, it tries the path when doesn't
        payment_method = driver.find_element(By.XPATH, "/html[@class='ui-mobile']/body[@class='ui-mobile-viewport ui-overlay-a']/div[@class='ui-page ui-page-theme-a ui-page-active']/div[@class='ui-content']/div[@id='conteudo']/div[@id='totalNota']/div[@id='linhaTotal'][3]/label[@class='tx']")
    finally:
        return payment_method.text

def extract_receipt_info(driver, receipt_url):
    driver.get(receipt_url)
    try:
        page_contents = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "conteudo"))
        )
        receipt_data = dict()
        receipt_data["url"] = receipt_url

        text_center_elements = driver.find_elements(By.CLASS_NAME, "txtCenter")
        for element in text_center_elements:
            if not element.get_attribute("id"):
                receipt_data["store"] = element.find_element(By.CLASS_NAME, "txtTopo").text
        
        total_billing = driver.find_element(By.CSS_SELECTOR, ".totalNumb.txtMax").text
        receipt_data["total"] = total_billing
        
        receipt_data["payment"] = get_payment_method(driver)
        
        date = driver.find_element(By.XPATH, "/html[@class='ui-mobile']/body[@class='ui-mobile-viewport ui-overlay-a']/div[@class='ui-page ui-page-theme-a ui-page-active']/div[@class='ui-content']/div[@id='infos']/div[@class='ui-collapsible ui-collapsible-inset ui-corner-all ui-collapsible-themed-content'][1]/div[@class='ui-collapsible-content ui-body-inherit']/ul[@class='ui-listview']/li[@class='ui-li-static ui-body-inherit ui-first-child ui-last-child']")
        tmp_date = date.text.split("Emissão: ")[1]
        receipt_data["datetime"] = tmp_date.split(" - Via Consumidor")[0]

        products = list()
        item_count = 1
        while(True):
            try:
                product = get_table_line(driver, "Item + {0}".format(item_count))
                products.append(product)
                item_count = item_count + 1
            except NoSuchElementException:
                print("End of products table, {0} products found".format(item_count-1))
                break
        receipt_data["products"] = products
        return receipt_data
    
    finally:
        driver.quit()

def save_receipt_data(mongo_uri, database, products):
    receipt_data = dict()
    receipt_data["url"] = products[0]["url"]
    receipt_data["store"] = products[0]["store"]
    receipt_data["total"] = products[0]["total"]
    receipt_data["payment"] = products[0]["payment"]
    receipt_data["datetime"] = products[0]["datetime"]
    receipt_data["products"] = list()

    for product in products:
        try:
            temp_product = dict()
            temp_product["product_id"] = product["product_id"]
            temp_product["product_quantity"] = product["product_quantity"]
            temp_product["unity_value"] = product["unity_value"]
            temp_product["total_value"] = product["total_value"]
            receipt_data["products"].append(temp_product)
        except KeyError:
            print(product)
    print("Saving receipt to mongo")
    mongo_product_id = mongo.save_to_mongo(
            uri=mongo_uri,
            database=database,
            collection="receipts",
            data=receipt_data
        )


if __name__ == "__main__":

    logging.basicConfig()
    # logging.root.setLevel(logging.NOTSET)

    config = configparser.ConfigParser()
    config.read("config.ini")

    while True:
        try:
            receipt_message = ast.literal_eval(sqs.get_one_message(config["sqs"]["receipt_queue_url"]))
            receipt_url = receipt_message['receipt_url']
            selenium_service = Service(executable_path=config["selenium"]["DriverPath"])
            driver = webdriver.Chrome(service=selenium_service)
            receipt_data = extract_receipt_info(driver, receipt_url)
            print(receipt_data)
            products = receipt_data.pop("products")

            # removing products from receipt data and substitute for empty list
            receipt_data["products"] = list()
            # save receipt to mongo
            print("Saving receipt to mongo")
            mongo_product_id = mongo.save_to_mongo(
                    uri=config["mongodb"]["ConnString"],
                    database=config["mongodb"]["Database"],
                    collection="receipts",
                    data=receipt_data
            )
            print("Sending products to market queue")
            for product in products:
                message = dict()
                message["receipt_url"] = receipt_url
                message["product"] = product
                if receipt_data["store"] == "HORTIGIL HORTIFRUTI S/A":
                    sqs.send_one_message(config["sqs"]["hortifruti_queue_url"], str(message))
                elif "SUPERMERCADO ZONA SUL SA" in receipt_data["store"]:
                    sqs.send_one_message(config["sqs"]["zonasul_queue_url"], str(message))
        except TimeoutException:
            # TODO: send problematic urls to an error queue
            continue
    
    #save_to_csv(products)