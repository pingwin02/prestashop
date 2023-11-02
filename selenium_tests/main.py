from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By

DEFAULT_LINK = "http://localhost:8080"


def test(drive: WebDriver) -> None:
    drive.get(DEFAULT_LINK)
    category = drive.find_element(By.XPATH, '//*[@id="category-3"]/a')
    category.click()
    first_subcategory = drive.find_element(By.XPATH, '//*[@id="subcategories"]/ul/li[1]/div[1]/a')
    first_subcategory.click()
    laptop = drive.find_element(By.XPATH, '//*[@id="js-product-list"]/div[1]/div[1]/article/div/div[1]/a/img')
    laptop.click()
    add_to_cart_btn = drive.find_element(By.XPATH, '//*[@id="add-to-cart-or-refresh"]/div[2]/div/div[2]/button')
    add_to_cart_btn.click()


if __name__ == "__main__":
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=chrome_options)
    test(browser)
