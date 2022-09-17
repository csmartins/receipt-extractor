from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time

def extract_product_info(product_sku):
    hortifruti_sku_search = "https://www.zonasul.com.br/{0}".format(product_sku)
    opts = webdriver.ChromeOptions()
    opts.add_argument("--window-size=2560,1440")

    driver = webdriver.Chrome(executable_path="./chromedriver",options=opts)
    driver.get(hortifruti_sku_search)

    try:
        page_contents = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vtex-flex-layout-0-x-flexCol--contentDesktop"))
        )
        
        # targeting only the first element found with such class, maybe in the future I want to get all of them
        product = driver.find_element_by_class_name("vtex-search-result-3-x-galleryItem")
        product.click()

        # wait for product details, which means the page is full loaded
        results = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "vtex-flex-layout-0-x-flexColChild--details-product-main"))
        )

        product_name = driver.find_element_by_class_name("vtex-store-components-3-x-productBrand").text

        # In the product type path (under the top menu) usually the type of the product has many levels ans sub groups, here
        # the script gets the most granular (last) because its easier
        product_type_path = driver.find_elements_by_class_name("vtex-breadcrumb-1-x-link")
        product_type = product_type_path[-2].text
        return (product_name, product_type, product_sku)
    except NoSuchElementException:
        raise
    except TimeoutException:
        not_found = driver.find_element_by_class_name("vtex-search-result-3-x-searchNotFound")
        return None
    finally:
        driver.quit()