from cgitb import text
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
finally:
    driver.quit()