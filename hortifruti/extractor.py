from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

import time

def extract_product_info(product_sku):
    hortifruti_sku_search = "https://hortifruti.com.br/search.html?query={0}&page=1".format(product_sku)
    driver = webdriver.Chrome(executable_path="./chromedriver")
    driver.get(hortifruti_sku_search)

    try:
        results_message_xpath = "/html[@class='wf-opensans-n4-active wf-active']/body/div[@id='root']/main[@class='main-root-1dr']/div[@class='main-page-6lS']/article[@class='searchPage-root-106']/div/div[@class='searchPage-heading-nhA']/div[@class='searchPage-container-1EZ']/div[@class='searchPage-searchBox-39C categoryHeader-categoryBox-3Jm']/h1[@class='searchPage-searchTitle-234']"
        page_contents = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, results_message_xpath))
        )
        # has_results = driver.find_element_by_class_name("noResultsFound-root-2wn")
        result_message = driver.find_element_by_xpath(results_message_xpath).text
        print(result_message)

        # when no products are found the message is slightly the same, it only doesn't have the number of results
        if "Foram encontrados resultados" in result_message:
            # didn't found necessary to check if the no results element doesn't really exists. But if this approach
            # causes problems, just check if noResultsFound-root-2wn exists and catch the NoSuchElementException
            return None

        results = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "searchPage-items-1Ee"))
        )
        # returns only the first element found with such class, maybe in the future I want to get all of them
        product = driver.find_element_by_class_name("item-infosLink-1xn")
        product.click()
        results = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "productFullDetail-root-1R8"))
        )

        product_name = driver.find_element_by_class_name("productFullDetail-productName-Isc").text

        # In the product type path (under the top menu) usually the type of the product is the third 
        # but sometimes the product doesn't have that info in the website, therefore the type will be empty
        product_type_path = driver.find_elements_by_class_name("breadcrumbs-link-1sU")
        product_type = ""
        if product_type_path:
           product_type = product_type_path[2]
        return (product_name, product_type, product_sku)
    except NoSuchElementException:
        # 
        # time.sleep(60)
        # print("test")
        raise
    finally:
        driver.quit()