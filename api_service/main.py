import io
import json
import os
import sys
from xml.etree.ElementTree import Element, ElementTree, SubElement, tostring
from random import randint
import mysql.connector

import requests
from prestapyt import PrestaShopWebServiceDict
from tqdm import tqdm

DEFAULT_LINK = "http://localhost:8080/api/"
SCRIPT_DIR = os.path.dirname(__file__)

def create_category_xml(name, parent_id):
    prestashop = Element("prestashop", xmlns_xlink="http://www.w3.org/1999/xlink")
    category = Element("category")

    name_elem = SubElement(category, "name")
    lang_elem = SubElement(name_elem, "language", id="1")
    lang_elem.text = f"{name}"

    link_rewrite_elem = SubElement(category, "link_rewrite")
    lang_elem_link = SubElement(link_rewrite_elem, "language", id="1")
    lang_elem_link.text = f'{name.lower().replace(" ", "-")}-demo'

    desc_elem = SubElement(category, "description")
    lang_elem_desc = SubElement(desc_elem, "language", id="1")
    lang_elem_desc.text = f"my awesome {name.lower()} description"

    active_elem = SubElement(category, "active")
    active_elem.text = str(1)

    parent_elem = SubElement(category, "id_parent")
    parent_elem.text = str(parent_id)
    prestashop.append(category)
    return prestashop


def prettify(elem):
    rough_string = tostring(elem, "utf-8")
    return rough_string


def create_category(name, parent_id):
    category = prestashop.add(
        "categories", prettify(create_category_xml(name, parent_id))
    )
    return category["prestashop"]["category"]["id"]

def create_cdata_element(parent, tag, text):
    """Creates an element with CDATA content."""
    element = SubElement(parent, tag)
    element.text = text
    return element

def create_cdata_element_with_xlink(parent, tag, text, link):
    """Creates an element with CDATA content."""
    element = SubElement(parent, tag, xlink=link)
    element.text = text
    return element

def create_cdata_element_with_id(parent, tag, text, id):
    """Creates an element with CDATA content and id."""
    element = SubElement(parent, tag, id=id)
    element.text = text
    return element

def create_product_xml(product_data, category_id):
    prestashop = Element("prestashop", xmlns_xlink="http://www.w3.org/1999/xlink")
    product = SubElement(prestashop, "product")

    create_cdata_element(product, "id_category_default", "2")
    create_cdata_element(product, "new", "1")
    create_cdata_element(product, "id_tax_rules_group", "3")
    create_cdata_element(product, "type", "simple")
    create_cdata_element(product, "id_shop_default", "1")
    create_cdata_element(product, "additional_delivery_times", "1")
    create_cdata_element(product, "reference", product_data["id"])
    create_cdata_element(product, "supplier_reference", product_data["attributes"].get("Producent", ""))
    create_cdata_element(product, "state", "1")
    create_cdata_element(product, "price", product_data["price"])
    create_cdata_element(product, "unit_price", product_data["price"])
    create_cdata_element(product, "active", "1")
    create_cdata_element(product, "minimal_quantity", "1")
    create_cdata_element(product, "available_for_order", "1")
    create_cdata_element(product, "show_price", "1")

    meta_description_elem = SubElement(product, "meta_description")
    create_cdata_element_with_id(meta_description_elem, "language",  product_data["description"].split(".")[0], id="1")

    meta_keywords_elem = SubElement(product, "meta_keywords")
    keywords = []
    for attribute in product_data["attributes"]:
        keywords.append(attribute)
    create_cdata_element_with_id(meta_keywords_elem, "language", " ".join(keywords), id="1")

    meta_title_elem = SubElement(product, "meta_title")
    create_cdata_element_with_id(meta_title_elem, "language", product_data["title"], id="1")

    link_rewrite_elem = SubElement(product, "link_rewrite")
    create_cdata_element_with_id(link_rewrite_elem, "language", product_data["title"].lower().replace(" ", "-"), id="1")

    name_elem = SubElement(product, "name")
    create_cdata_element_with_id(name_elem, "language", product_data["title"], id="1")

    desc_elem = SubElement(product, "description")
    create_cdata_element_with_id(desc_elem, "language", product_data["description"], id="1")

    desc_short_elem = SubElement(product, "description_short")
    create_cdata_element_with_id(desc_short_elem, "language", product_data["description"].split(".")[0], id="1")

    associations = SubElement(product, "associations")
    categories = SubElement(associations, "categories")
    category_elem = SubElement(categories, "category")
    create_cdata_element(category_elem, "id", str(2))
    category_elem = SubElement(categories, "category")
    create_cdata_element(category_elem, "id", str(category_id))

    return prestashop

def create_stock_supplies_xml(product_id, how_many):
    prestashop = Element("prestashop", xmlns_xlink="http://www.w3.org/1999/xlink")
    stock_available = SubElement(prestashop, "stock_available")

    create_cdata_element(stock_available, "id", str(product_id))
    create_cdata_element(stock_available, "id_product", str(product_id))
    create_cdata_element(stock_available, "id_shop", "1")
    create_cdata_element(stock_available, "id_product_attribute", "1")
    create_cdata_element(stock_available, "quantity", "4")
    create_cdata_element(stock_available, "depends_on_stock", "0")
    create_cdata_element(stock_available, "out_of_stock", "2")
    return prestashop

def create_product(product):
    category_id = prestashop.get("categories", options={'filter[name]': product["category"]})["categories"]["category"]["attrs"]["id"]
    response = prestashop.add("products", prettify(create_product_xml(product, int(category_id))))
    return response["prestashop"]["product"]["id"]


def create_image(images, product_id, id):
    for image in images:
        img_name = f'images/{id}/{image.split("/")[-1]}'
        if not os.path.isfile(os.path.join(SCRIPT_DIR, img_name)):
            img_data = requests.get(image).content
            if not os.path.exists(os.path.join(SCRIPT_DIR, f'images/{id}/')):
                os.makedirs(os.path.dirname(os.path.join(SCRIPT_DIR, f'images/{id}/')))
            with open(f'{img_name}', 'wb') as handler:
                handler.write(img_data)
        fd = io.open(img_name, "rb")
        content = fd.read()
        fd.close()
        prestashop.add(f"/images/products/{product_id}", files=[('image', img_name, content)])

def create_stock_supplies(product_id, how_many):

    xd = prestashop.edit(f"stock_availables/{product_id}", prettify(create_stock_supplies_xml(product_id, how_many)))
    print(xd)
def manage_categories():
    with open("../scraper/categories.json") as file:
        categories = json.loads(file.read())

    ids = []
    for category in prestashop.get("categories")["categories"]["category"]:
        if int(category["attrs"]["id"]) not in [1, 2]:
            ids.append(int(category["attrs"]["id"]))
    if ids:
        print("Deleting...")
        prestashop.delete("categories", resource_ids=ids)

    index = 2
    total = sum(len(subcategories) for subcategories in categories.values()) + len(
        categories
    )

    with tqdm(total=total) as pbar:
        for category in categories:
            parent_id = create_category(category, index)
            pbar.update(1)

            for subcategory in categories[category]:
                subcategory_id = create_category(subcategory, parent_id)
                pbar.update(1)

def manage_products():
    ids = []
    products = prestashop.get("products")["products"]
    if products and len(products['product']) > 2:
        for product in prestashop.get("products")["products"]["product"]:
            if product != "attrs":
                ids.append(int(product["attrs"]["id"]))
        if ids:
            print("Deleting...")
            prestashop.delete("products", resource_ids=ids)

    with open("../scraper/products.json") as file:
        products = json.loads(file.read())

    total = len(products)

    with tqdm(total=10) as pbar:
        for product in products[:8]:
            product_id = create_product(product)
            create_image(product["images"], product_id, product["id"])
            #create_stock_supplies(product_id, randint(20, 200))
            pbar.update(1)

    conn = mysql.connector.connect(
        host='0.0.0.0',
        user='root',
        password='admin',
        database='presta_database'
    )
    cursor = conn.cursor()

    sql_query = """
    UPDATE ps_stock_available 
    SET quantity = %s
    WHERE id_stock_available = %s
    """

    cursor.execute("SELECT id_stock_available FROM ps_stock_available")
    all_ids = cursor.fetchall()

    for id in all_ids:
        random_quantity = randint(10, 200)
        cursor.execute(sql_query, (random_quantity, id[0]))

    conn.commit()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    prestashop = PrestaShopWebServiceDict(
        "http://localhost:8080/api", "H1C47QDSEC5G8CNCAIZ49ZN6WEQEF1QK"
    )
    #manage_categories()
    manage_products()
