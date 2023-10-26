import json
from pprint import pprint
from xml.dom import minidom
from xml.etree.ElementTree import Element, ElementTree, SubElement, tostring

import requests
from prestapyt import PrestaShopWebServiceDict

prestashop = PrestaShopWebServiceDict("http://localhost:8080/api", "YOUR_API_KEY")

data = """
{
    "category": {
        "Laptopy i komputery": {
            "Laptopy": [],
            "Komputery": [],
            "Serwery": [],
            "Tablety": []
        }
    }
}
"""

print(prestashop.get("categories", options={"filter[name]": "Laptopy i komputery"}))
# for i in prestashop.get('categories')['categories']['category']:
#     if i['attrs']['id'] != '1':
#         prestashop.delete('categories', resource_ids=[i['attrs']['id']])


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
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def create_category(name, parent_id):
    category = prestashop.get("categories", options={"filter[name]": name})
    if not category:
        print(category["categories"]["category"])
        return category
    else:
        category = prestashop.add(
            "categories", prettify(create_category_xml(name, parent_id))
        )
        return category["prestashop"]["category"]["id"]


def create_product(name, price, category_id):
    product = prestashop.get("products", options={"filter[name]": name})
    if product["products"]["product"]:
        return product["products"]["product"][0]["attrs"]["id"]
    else:
        product = prestashop.add(
            "products",
            payload={
                "product": {
                    "name": name,
                    "price": price,
                    "id_category_default": category_id,
                }
            },
        )
        return product["product"]["id"]


def create_image(product_id, image_url):
    product = prestashop.get("products", resource_id=product_id)
    if product["product"]["associations"]["images"]["image"]:
        return
    else:
        product = prestashop.add(
            "images/products",
            payload={
                "image": {
                    "id_product": product_id,
                    "id_image_type": 1,
                    "image_url": image_url,
                }
            },
        )
        return product["image"]["id"]


categories = json.loads(data)["category"]
address_data = prestashop.get("categories", 1)
print(address_data)

for category in categories:
    parent_id = create_category(category, 2)
    for subcategory in categories[category]:
        subcategory_id = create_category(subcategory, parent_id)
        # for product in categories[category][subcategory]:
        #     product_id = create_product(product['name'], product['price'], subcategory_id)
        #     create_image(product_id, product['image_url'])
