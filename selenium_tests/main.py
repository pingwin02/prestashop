from selenium import webdriver
from selenium.webdriver.common.by import By

DEFAULT_LINK = "http://localhost:8080"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)
browser = webdriver.Chrome(options=chrome_options)


def test() -> None:
    browser.get(DEFAULT_LINK)
    browser.find_element(By.CSS_SELECTOR, "#category-3 > a").click()
    browser.find_element(By.CSS_SELECTOR, "#subcategories > ul > li:nth-child(1) > div.subcategory-image > a").click()
    browser.find_element(By.CSS_SELECTOR, "#js-product-list > div.products.row > div:nth-child(1) > article > div > "
                                          "div.thumbnail-top > a > img").click()
    browser.find_element(By.CSS_SELECTOR, "#add-to-cart-or-refresh > div.product-add-to-cart.js-product-add-to-cart > "
                                          "div > div.add > button").click()


if __name__ == "__main__":
    test()
