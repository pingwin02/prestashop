import io
import json
import os
import traceback
from typing import Dict, List
import re
from xml.etree.ElementTree import Element, SubElement, tostring
from random import randint
import mysql.connector

from prestapyt import PrestaShopWebServiceDict
from tqdm import tqdm

DEFAULT_LINK = "http://localhost:8080/api/"
SCRIPT_DIR = os.path.dirname(__file__)


def create_category_xml(name: str, parent_id: int) -> Element:
    prestashop = Element(
        "prestashop", xmlns_xlink="http://www.w3.org/1999/xlink")
    category = Element("category")

    name_elem = SubElement(category, "name")
    lang_elem = SubElement(name_elem, "language", id="1")
    lang_elem.text = f"{name}"

    link_rewrite_elem = SubElement(category, "link_rewrite")
    lang_elem_link = SubElement(link_rewrite_elem, "language", id="1")
    lang_elem_link.text = f'{name.lower().replace(" ", "-")}-demo'

    desc_elem = SubElement(category, "description")
    lang_elem_desc = SubElement(desc_elem, "language", id="1")
    lang_elem_desc.text = f"{name.lower()} description"

    active_elem = SubElement(category, "active")
    active_elem.text = str(1)

    parent_elem = SubElement(category, "id_parent")
    parent_elem.text = str(parent_id)
    prestashop.append(category)
    return prestashop


def prettify(elem: Element) -> str:
    rough_string = tostring(elem, "utf-8")
    return rough_string


def create_category(name: str, parent_id: int) -> int:
    category = prestashop.get(
        "categories", options={"filter[name]": name}
    )

    if not category["categories"]:
        category = prestashop.add(
            "categories", prettify(create_category_xml(name, parent_id))
        )
        return category["prestashop"]["category"]["id"]
    else:
        return category["categories"]["category"]["attrs"]["id"]


def create_cdata_element(parent: Element, tag: str, text: str) -> SubElement:
    """Creates an element with CDATA content."""
    element = SubElement(parent, tag)
    element.text = text
    return element


def create_cdata_element_with_xlink(
    parent: SubElement, tag: str, text: str, link: str
) -> SubElement:
    """Creates an element with CDATA content."""
    element = SubElement(parent, tag, xlink=link)
    element.text = text
    return element


def create_cdata_element_with_id(
    parent: SubElement, tag: str, text: str, id_: str
) -> SubElement:
    """Creates an element with CDATA content and id."""
    element = SubElement(parent, tag, id=id_)
    element.text = text
    return element


def create_product_xml(product_data: Dict, category_id: int, feature_ids: Dict[int, int]) -> Element:
    prestashop = Element(
        "prestashop", xmlns_xlink="http://www.w3.org/1999/xlink")
    product = SubElement(prestashop, "product")

    create_cdata_element(product, "id_category_default", "2")
    create_cdata_element(product, "new", str(0))
    create_cdata_element(product, "id_tax_rules_group", "1")
    create_cdata_element(product, "type", "simple")
    create_cdata_element(product, "id_shop_default", "1")
    create_cdata_element(product, "additional_delivery_times", "1")
    create_cdata_element(product, "reference", product_data["id"])
    create_cdata_element(
        product, "supplier_reference", product_data["attributes"].get(
            "Producent", "")
    )

    create_cdata_element(product, "state", "1")
    price = str(round(float(product_data["price"])/1.23, 2))
    create_cdata_element(product, "price", price)
    create_cdata_element(product, "unit_price", price)
    create_cdata_element(product, "active", "1")
    create_cdata_element(product, "minimal_quantity", "1")
    create_cdata_element(product, "available_for_order", "1")
    create_cdata_element(product, "show_price", "1")

    meta_keywords_elem = SubElement(product, "meta_keywords")
    keywords = []
    for attribute in product_data["attributes"].values():
        if len(attribute) <= 255:
            keywords.append(attribute)
    create_cdata_element_with_id(
        meta_keywords_elem, "language", " ".join(keywords[:4]), id_="1"
    )

    meta_title_elem = SubElement(product, "meta_title")
    create_cdata_element_with_id(
        meta_title_elem, "language", product_data["title"], id_="1"
    )

    link_rewrite_elem = SubElement(product, "link_rewrite")
    create_cdata_element_with_id(
        link_rewrite_elem,
        "language",
        product_data["title"].lower().replace(" ", "-"),
        id_="1",
    )

    name_elem = SubElement(product, "name")
    create_cdata_element_with_id(
        name_elem, "language", product_data["title"].replace(";", ""), id_="1")

    desc_elem = SubElement(product, "description")
    create_cdata_element_with_id(
        desc_elem, "language", product_data["description"], id_="1"
    )

    desc_short_elem = SubElement(product, "description_short")
    create_cdata_element_with_id(
        desc_short_elem, "language", product_data["description"].split(".")[0], id_="1"
    )

    associations = SubElement(product, "associations")
    categories = SubElement(associations, "categories")
    category_elem = SubElement(categories, "category")
    create_cdata_element(category_elem, "id", str(2))
    category_elem = SubElement(categories, "category")
    create_cdata_element(category_elem, "id", str(category_id))

    features = SubElement(associations, "product_features")
    for feature_id, value_id in feature_ids.items():
        feature_elem = SubElement(features, "product_feature")
        create_cdata_element(feature_elem, "id", str(feature_id))
        create_cdata_element(feature_elem, "id_feature_value", str(value_id))
    return prestashop


def create_product(product: Dict, feature_ids: Dict[int, int]) -> int:
    category_id = prestashop.get(
        "categories", options={"filter[name]": product["category"]}
    )["categories"]["category"]["attrs"]["id"]
    response = prestashop.add(
        "products", prettify(create_product_xml(
            product, int(category_id), feature_ids))
    )
    return response["prestashop"]["product"]["id"]


def create_image(images: List[str], product_id: int, id_: str) -> None:
    for image in images:
        img_name = f'../scraper_results/images/{id_}/{image.split("/")[-1]}'
        if os.path.exists(img_name):
            fd = io.open(img_name, "rb")
            content = fd.read()
            fd.close()
            prestashop.add(
                f"/images/products/{product_id}", files=[("image", img_name, content)]
            )


def create_stock_supplies() -> None:
    conn = mysql.connector.connect(
        host="0.0.0.0", user="root", password="admin", database="presta_database"
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
        random_quantity = randint(0, 10)
        cursor.execute(sql_query, (random_quantity, id[0]))

    conn.commit()

    cursor.close()
    conn.close()


def create_feature_xml(attribute: str) -> Element:
    prestashop = Element(
        "prestashop", xmlns_xlink="http://www.w3.org/1999/xlink")
    stock_available = SubElement(prestashop, "product_feature")

    create_cdata_element(stock_available, "position", str(1))
    name_elem = SubElement(stock_available, "name")
    create_cdata_element_with_id(name_elem, "language", attribute, id_="1")
    return prestashop


def create_feature_value_xml(value: str, feature_id: int) -> Element:
    prestashop = Element(
        "prestashop", xmlns_xlink="http://www.w3.org/1999/xlink")
    stock_available = SubElement(prestashop, "product_feature_value")

    create_cdata_element(stock_available, "id_feature", str(feature_id))
    create_cdata_element(stock_available, "custom", str(0))
    value_elem = SubElement(stock_available, "value")
    create_cdata_element_with_id(value_elem, "language", value, id_="1")
    return prestashop


def create_features_and_values(attributes: Dict[str, str]) -> Dict[int, int]:
    attr_val = dict()
    for attribute, value in attributes.items():
        attribute = re.sub(r"\[.*?\]|<|>", "", attribute)
        value = re.sub(r"\[.*?\]|<|>", "", value)
        value = value.replace("=", "-")
        if len(value) <= 255:
            feature_name = prestashop.get(
                "product_features", options={"filter[name]": attribute}
            )
            if feature_name["product_features"]:
                attr_id = feature_name["product_features"]["product_feature"]["attrs"]["id"]
            else:
                attr_id = prestashop.add(
                    "product_features", prettify(create_feature_xml(attribute))
                )
                attr_id = attr_id["prestashop"]["product_feature"]["id"]

            feature_option_name = prestashop.get(
                "product_feature_values", options={"filter[value]": value}
            )
            if feature_option_name["product_feature_values"]:
                attr_val[attr_id] = feature_option_name["product_feature_values"]["product_feature_value"]["attrs"]["id"]
            else:
                value_id = prestashop.add(
                    "product_feature_values",
                    prettify(create_feature_value_xml(value, attr_id)),
                )
                attr_val[attr_id] = value_id["prestashop"]["product_feature_value"]["id"]
    return attr_val


def manage_categories() -> None:
    # ids = []
    # for category in prestashop.get("categories")["categories"]["category"]:
    #     if int(category["attrs"]["id"]) not in [1, 2]:
    #         ids.append(int(category["attrs"]["id"]))
    # if ids:
    #     print("Deleting categories...")
    #     prestashop.delete("categories", resource_ids=ids)

    with open("../scraper_results/categories.json") as file:
        categories = json.loads(file.read())

    index = 2
    total = sum(len(subcategories) for subcategories in categories.values()) + len(
        categories
    )

    with tqdm(total=total) as pbar:
        for category in categories:
            try:
                parent_id = create_category(category, index)
                pbar.update(1)

                for subcategory in categories[category]:
                    create_category(subcategory, parent_id)
                    pbar.update(1)
            except Exception as e:
                with open("venv/error_log.txt", "a") as file:
                    file.write(
                        f"Error while adding category: {category}\n")
                    file.write(f"{traceback.format_exc()}\n")


def manage_products() -> None:
    # ids = []
    # products = prestashop.get("products")["products"]
    # if products and len(products["product"]) > 2:
    #     for product in prestashop.get("products")["products"]["product"]:
    #         if product != "attrs":
    #             ids.append(int(product["attrs"]["id"]))
    #     if ids:
    #         print("Deleting products...")
    #         prestashop.delete("products", resource_ids=ids)

    # features = prestashop.get("product_features")["product_features"]
    # if features and len(features["product_feature"]) > 2:
    #     ids = []
    #     for feature in features["product_feature"]:
    #         if feature != "attrs":
    #             ids.append(int(feature["attrs"]["id"]))
    #     if ids:
    #         print("Deleting features...")
    #         prestashop.delete("product_features", resource_ids=ids)

    with open("../scraper_results/products.json") as file:
        products = json.loads(file.read())

    total = len(products)

    with tqdm(total=total) as pbar:
        for product in products[0:total]:
            try:
                feature_ids = create_features_and_values(product["attributes"])
                product_id = create_product(product, feature_ids)
                create_image(product["image_urls"], product_id, product["id"])
                pbar.update(1)
            except Exception as e:
                with open("venv/error_log.txt", "a") as file:
                    file.write(
                        f"Error while adding product id: {product['id']}\n")
                    file.write(f"{traceback.format_exc()}\n")


if __name__ == "__main__":
    prestashop = PrestaShopWebServiceDict(
        "http://localhost:8080/api", "H1C47QDSEC5G8CNCAIZ49ZN6WEQEF1QK")

    manage_categories()
    manage_products()
    create_stock_supplies()
