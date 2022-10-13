from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from vendor import opensearch
from vendor import mongo

import configparser
import hortifruti.extractor
import zonasul.extractor
import csv


def get_table_line(driver, tr_id):
    line = driver.find_element_by_id(tr_id)
    
    product_name = line.find_element_by_class_name("txtTit").text
    
    raw_product_code = line.find_element_by_class_name("RCod").text
    product_code = raw_product_code.split(" ")[1]

    raw_product_quantity = line.find_element_by_class_name("Rqtd").text
    product_quantity = raw_product_quantity.split(".:")[1]

    raw_unity_type = line.find_element_by_class_name("RUN").text
    unity_type = raw_unity_type.split(": ")[1]

    raw_unity_value = line.find_element_by_class_name("RvlUnit").text
    unity_value = raw_unity_value.split(".:   ")[1]

    total_value = line.find_element_by_class_name("valor").text

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

def extract_receipt_info(driver, receipt_url):
    driver.get(receipt_url)
    try:
        page_contents = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "conteudo"))
        )
        receipt_data = dict()
        receipt_data["url"] = receipt_url

        text_center_elements = driver.find_elements_by_class_name("txtCenter")
        for element in text_center_elements:
            if not element.get_attribute("id"):
                receipt_data["store"] = element.find_element_by_class_name("txtTopo").text
        
        total_billing = driver.find_element_by_css_selector(".totalNumb.txtMax").text
        receipt_data["total"] = total_billing

        payment_type = driver.find_element_by_xpath("/html[@class='ui-mobile']/body[@class='ui-mobile-viewport ui-overlay-a']/div[@class='ui-page ui-page-theme-a ui-page-active']/div[@class='ui-content']/div[@id='conteudo']/div[@id='totalNota']/div[@id='linhaTotal'][5]/label[@class='tx']")
        receipt_data["payment"] = payment_type.text

        date = driver.find_element_by_xpath("/html[@class='ui-mobile']/body[@class='ui-mobile-viewport ui-overlay-a']/div[@class='ui-page ui-page-theme-a ui-page-active']/div[@class='ui-content']/div[@id='infos']/div[@class='ui-collapsible ui-collapsible-inset ui-corner-all ui-collapsible-themed-content'][1]/div[@class='ui-collapsible-content ui-body-inherit']/ul[@class='ui-listview']/li[@class='ui-li-static ui-body-inherit ui-first-child ui-last-child']")
        tmp_date = date.text.split("Emissão: ")[1]
        receipt_data["datetime"] = tmp_date.split(" - Via Consumidor")[0]

        products = list()
        item_count = 1
        while(True):
            try:
                product = get_table_line(driver, "Item + {0}".format(item_count))
                product.update(receipt_data)
                products.append(product)

                item_count = item_count + 1
            except NoSuchElementException:
                print("End of products table, {0} products found".format(item_count-1))
                break
        
        return products
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

    config = configparser.ConfigParser()
    config.read("config.ini")

    receipt_url = "http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode?p=33220331487473003538650010002551641625634243|2|1|2|d953fa67b328f9812dafcbad42739acef04e655c"
    # extract to config ini
    driver = webdriver.Chrome(executable_path=config["selenium"]["DriverPath"])
    products = extract_receipt_info(driver, receipt_url)

    # # # print(products)
    for product in products:
        if product["store"] == "HORTIGIL HORTIFRUTI S/A":
            product_details = hortifruti.extractor.extract_product_info(product["product_code"])
            # print(product_details)
        elif product["store"] == "ZONA SUL":
            product_details = zonasul.extractor.extract_product_info(product["product_code"])
        print(product["product_code"], product_details)
        if product_details:
            product["product_name"] = product_details[0]
            product["product_type"] = product_details[1]
        # In opensearch saving the product with all data needed
        print("Save product info to opensearch")
        opensearch.save_to_opensearch(
            host=config["opensearch"]["Host"],
            port=config["opensearch"]["Port"],
            user=config["opensearch"]["User"],
            password=config["opensearch"]["Password"],
            product=product
        )
        # In mongo saving only metadata about the product (no data related to a specific receipt)
        print("Search if product already exists")
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
            print("Save product metadata to mongo")
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
            print("Alert: duplicated product")
            #TODO raise exception
        else:
            print("Product already exists, skipping")
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
    # save receipt to mongo too
    
    save_receipt_data(
        mongo_uri=config["mongodb"]["ConnString"],
        database=config["mongodb"]["Database"],
        products=products
    )
    #save_to_csv(products)