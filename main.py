from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

def get_table_line(tr_id):
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

receipt_url = "http://www4.fazenda.rj.gov.br/consultaNFCe/QRCode?p=33220331487473003538650010002551641625634243|2|1|2|d953fa67b328f9812dafcbad42739acef04e655c"
driver = webdriver.Chrome(executable_path="./chromedriver")
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
    
    receipt_data["products"] = list()
    item_count = 1
    while(True):
        try:
            product = get_table_line("Item + {0}".format(item_count))
            receipt_data["products"].append(product)

            item_count = item_count + 1
        except NoSuchElementException:
            print("End of products table, {0} products found".format(item_count-1))
            break
    
    total_billing = driver.find_element_by_css_selector(".totalNumb.txtMax").text
    receipt_data["total"] = total_billing

    payment_type = driver.find_element_by_xpath("/html[@class='ui-mobile']/body[@class='ui-mobile-viewport ui-overlay-a']/div[@class='ui-page ui-page-theme-a ui-page-active']/div[@class='ui-content']/div[@id='conteudo']/div[@id='totalNota']/div[@id='linhaTotal'][5]/label[@class='tx']")
    receipt_data["payment"] = payment_type.text

    date = driver.find_element_by_xpath("/html[@class='ui-mobile']/body[@class='ui-mobile-viewport ui-overlay-a']/div[@class='ui-page ui-page-theme-a ui-page-active']/div[@class='ui-content']/div[@id='infos']/div[@class='ui-collapsible ui-collapsible-inset ui-corner-all ui-collapsible-themed-content'][1]/div[@class='ui-collapsible-content ui-body-inherit']/ul[@class='ui-listview']/li[@class='ui-li-static ui-body-inherit ui-first-child ui-last-child']")
    tmp_date = date.text.split("Emissão: ")[1]
    receipt_data["datetime"] = tmp_date.split(" - Via Consumidor")[0]
    print(receipt_data)
finally:
    driver.quit()