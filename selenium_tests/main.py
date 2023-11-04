import time
from math import ceil
from selenium import webdriver
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

DEFAULT_LINK = "http://localhost:8080"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)


def add_to_cart() -> None:
    driver.find_element(By.CSS_SELECTOR, "#add-to-cart-or-refresh > div.product-add-to-cart.js-product-add-to-cart > "
                                         "div > div.add > button").click()
    WebDriverWait(driver, 7).until(ec.element_to_be_clickable(
        (By.CSS_SELECTOR, "#blockcart-modal > div > div > div.modal-header > button > span > i"))).click()


def delete_from_cart() -> None:
    driver.find_element(By.CSS_SELECTOR, "#_desktop_cart > div > div > a > span.hidden-sm-down").click()
    driver.find_element(By.CSS_SELECTOR, "#main > div > div.cart-grid-body.col-xs-12.col-lg-8 > div > "
                                         "div.cart-overview.js-cart > ul > li > div > "
                                         "div.product-line-grid-right.product-line-actions.col-md-5.col-xs-12 > div > "
                                         "div.col-md-2.col-xs-2.text-xs-right > div > a > i").click()


def register_user() -> None:
    driver.find_element(By.CSS_SELECTOR, "#_desktop_user_info > div > a > span").click()
    driver.find_element(By.CSS_SELECTOR, "#content > div > a").click()
    driver.find_element(By.CSS_SELECTOR, "#field-id_gender-1").click()
    driver.find_element(By.CSS_SELECTOR, "#field-firstname").send_keys("Harry")
    driver.find_element(By.CSS_SELECTOR, "#field-lastname").send_keys("Potter")
    driver.find_element(By.CSS_SELECTOR, "#field-email").send_keys("potter@gmail.com")  # change it after first use
    driver.find_element(By.CSS_SELECTOR, "#field-password").send_keys("12345")
    driver.find_element(By.CSS_SELECTOR, "#customer-form > div > div:nth-child(8) > div.col-md-6 > span > label > "
                                         "input[type=checkbox]").click()
    driver.find_element(By.CSS_SELECTOR, "#customer-form > div > div:nth-child(10) > div.col-md-6 > span > label > "
                                         "input[type=checkbox]").click()
    driver.find_element(By.CSS_SELECTOR, "#customer-form > footer > button").click()


def test() -> None:
    driver.get(DEFAULT_LINK)

    # a. - add 10 items to cart
    for j in [5, 30]:
        for i in range(1, 7):
            menu = driver.find_element(By.CSS_SELECTOR, "#category-2 > a")
            ActionChains(driver).move_to_element(menu).perform()
            WebDriverWait(driver, 7).until(ec.element_to_be_clickable(
                (By.CSS_SELECTOR, f"#category-{j} > a"))).click()
            driver.find_element(By.CSS_SELECTOR, f'#js-product-list > div.products.row > div:nth-child({i}) > article'
                                                 f' > div > div.thumbnail-top > a > img').click()
            add_to_cart()
            if j == 5 and i == 4:
                break

    # b. add 1 item from search
    (driver.find_element(By.CSS_SELECTOR, "#search_widget > form > input.ui-autocomplete-input")
     .send_keys("ipad", Keys.RETURN))
    driver.find_element(By.CSS_SELECTOR, '#js-product-list > div.products.row > div:nth-child(2) > article'
                                         ' > div > div.thumbnail-top > a > img').click()
    add_to_cart()

    # c. - delete 3 items from cart
    for _ in range(3):
        delete_from_cart()

    # d. register new user
    register_user()

    # e. order
    driver.find_element(By.CSS_SELECTOR, "#_desktop_cart > div > div > a > span.hidden-sm-down").click()
    driver.find_element(By.CSS_SELECTOR, "#main > div > div.cart-grid-right.col-xs-12.col-lg-4 > "
                                         "div.card.cart-summary > "
                                         "div.checkout.cart-detailed-actions.js-cart-detailed-actions.card-block > "
                                         "div > a").click()
    driver.find_element(By.CSS_SELECTOR, "#field-address1").send_keys("qwerty")
    driver.find_element(By.CSS_SELECTOR, "#field-postcode").send_keys("12-345")
    driver.find_element(By.CSS_SELECTOR, "#field-city").send_keys("Gdansk")
    driver.find_element(By.CSS_SELECTOR, "#delivery-address > div > footer > button").click()

    # g. delivery choice
    driver.find_element(By.CSS_SELECTOR, "#delivery_option_3").click()
    WebDriverWait(driver, 10).until(ec.element_to_be_clickable(
        (By.CSS_SELECTOR, "#js-delivery > button"))).click()

    # TODO f. pay method choice - FIX
    driver.find_element(By.CSS_SELECTOR, "#payment-option-2").click()
    driver.find_element(By.CSS_SELECTOR, "#conditions_to_approve\[terms-and-conditions\]").click()

    # h. order confirmation
    driver.find_element(By.CSS_SELECTOR, "#payment-confirmation > div.ps-shown-by-js > button").click()

    # i. verify order status
    driver.find_element(By.CSS_SELECTOR, "#_desktop_user_info > div > a.account > span").click()
    driver.find_element(By.CSS_SELECTOR, "#history-link > span > i").click()
    driver.find_element(By.CSS_SELECTOR, "#content > table > tbody > tr > td.text-sm-center.order-actions > "
                                         "a:nth-child(1)").click()

    # TODO j. get VAT


if __name__ == "__main__":
    start_time = time.time()
    test()
    time_spent = ceil(time.time() - start_time)
    print(f"minutes : {time_spent // 60}, seconds : {time_spent % 60}")
