import io
import os
import re
import json
import prestapyt
import traceback
from tqdm import tqdm
from random import randint
from threading import Semaphore
from concurrent.futures import ThreadPoolExecutor

DEFAULT_LINK = "http://localhost:8080/api/"
SCRIPT_DIR = os.path.dirname(__file__).split("api_service")[0]

semaphore = Semaphore(1)


def add_category(name: str, parent_id: int) -> int:
    category = prestashop.get("categories", options={
        "filter[name]": name
    })

    if not category["categories"]:
        category_schema["category"]["name"]["language"]["value"] = name
        category_schema["category"]["id_parent"] = parent_id
        category_schema["category"]["active"] = 1
        category_schema["category"]["link_rewrite"]["language"]["value"] = re.sub(
            r"[^a-zA-Z0-9]+", "-", name).lower()
        category_schema["category"]["description"][
            "language"]["value"] = f"Kategoria {name}"
        return prestashop.add("categories", category_schema)["prestashop"]["category"]["id"]
    else:
        return category["categories"]["category"]["attrs"]["id"]


def add_features(attributes: dict) -> dict:
    feat_ids_values = dict()
    for name, value in attributes.items():
        name = re.sub(r"\[.*?\]|<|>", "", name)
        value = re.sub(r"\[.*?\]|<|>|=", "", value)
        if len(value) > 255 or any(substring in name.lower() for substring in ["waga", "masa"]):
            continue
        feature = prestashop.get("product_features", options={
            "filter[name]": name
        })
        if feature["product_features"]:
            feature_id = feature["product_features"]["product_feature"]["attrs"]["id"]
        else:
            feature_schema["product_feature"]["name"]["language"]["value"] = name
            feature_schema["product_feature"]["position"] = 1
            feature_id = prestashop.add(
                "product_features", feature_schema)["prestashop"]["product_feature"]["id"]

        feature_option_schema["product_feature_value"]["id_feature"] = feature_id
        feature_option_schema["product_feature_value"]["value"]["language"]["value"] = value
        feature_option_schema["product_feature_value"]["custom"] = 1
        value_id = prestashop.add(
            "product_feature_values", feature_option_schema)["prestashop"]["product_feature_value"]["id"]
        feat_ids_values[feature_id] = value_id
    return feat_ids_values


def add_images_to_product(scraped_id: int, product_id: int) -> None:
    for image in os.listdir(f"{SCRIPT_DIR}scraper_results/images/{scraped_id}"):
        fd = io.open(
            f"{SCRIPT_DIR}scraper_results/images/{scraped_id}/{image}", "rb")
        content = fd.read()
        fd.close()
        prestashop.add(f"images/products/{product_id}", files=[
            ("image", image, content)
        ])


def change_quantity(product_id: int) -> None:
    schema_id = prestashop.search("stock_availables", options={
        "filter[id_product]": product_id
    })[0]
    stock_available_schema = prestashop.get(
        "stock_availables", resource_id=schema_id)
    stock_available_schema["stock_available"]["quantity"] = randint(0, 10)
    stock_available_schema["stock_available"]["depends_on_stock"] = 0
    prestashop.edit("stock_availables", stock_available_schema)


def add_product(product: dict) -> None:
    try:
        semaphore.acquire()
        feature_ids = add_features(product["attributes"])
        semaphore.release()
        category_id = prestashop.get("categories", options={
            "filter[name]": product["category"]
        })["categories"]["category"]["attrs"]["id"]
        product_schema["product"]["name"]["language"]["value"] = product["title"].replace(
            ";", "")
        product_schema["product"]["id_category_default"] = category_id
        product_schema["product"]["id_shop_default"] = 1
        product_schema["product"]["reference"] = product["id"]
        product_schema["product"]["id_tax_rules_group"] = 1
        price = round(float(product["price"])/1.23, 2)
        product_schema["product"]["price"] = price
        product_schema["product"]["active"] = 1
        product_schema["product"]["state"] = 1
        product_schema["product"]["available_for_order"] = 1
        product_schema["product"]["minimal_quantity"] = 1
        product_schema["product"]["show_price"] = 1
        product_schema["product"]["link_rewrite"]["language"]["value"] = re.sub(
            r"[^a-zA-Z0-9]+", "-", product["title"]).lower()
        product_schema["product"]["meta_title"]["language"]["value"] = product["title"]
        product_features = []
        for feature_id, value_id in feature_ids.items():
            product_features.append({
                "id": feature_id,
                "id_feature_value": value_id
            })
        product_schema["product"]["associations"]["product_features"]["product_feature"] = product_features
        product_schema["product"]["associations"]["categories"] = {
            "category": [
                {"id": 2},
                {"id": category_id}
            ],
        }
        weight = None
        try:
            for key, value in product["attributes"].items():
                lowercase_key = key.lower()
                if any(substring in lowercase_key for substring in ["waga", "masa"]):
                    weight = float(value.split(" ")[0])
                    if " g" in value:
                        weight /= 1000
                    break
        except Exception as e:
            pass

        if weight is None:
            weight = randint(1, 600) / 10
        weight = round(max(weight, 0.001), 3)

        product_schema["product"]["weight"] = weight
        product_schema["product"]["description_short"]["language"][
            "value"] = f"{product['description'].split('.')[0]}."
        product_schema["product"]["description"]["language"][
            "value"] = f"{product['description']}<br><br>Masa produktu: {weight} kg."
        product_id = prestashop.add("products", product_schema)[
            "prestashop"]["product"]["id"]
        change_quantity(product_id)
        add_images_to_product(scraped_id=product["id"], product_id=product_id)
    except Exception as e:
        print(f"Error while adding product: {product['id']}")
        print(traceback.format_exc())


def add_products(clean: bool = False) -> None:
    if clean:
        products = prestashop.get("products")["products"]
        if products:
            products_data = products["product"]

            if isinstance(products_data, dict):
                products_data = [products_data]

            ids = [int(product["attrs"]["id"]) for product in products_data]
            if ids:
                print("Deleting products...")
                prestashop.delete("products", resource_ids=ids)

        features = prestashop.get("product_features")["product_features"]
        if features:
            features_data = prestashop.get("product_features")[
                "product_features"]["product_feature"]

            if isinstance(features_data, dict):
                features_data = [features_data]

            ids = [int(feature["attrs"]["id"]) for feature in features_data]
            if ids:
                print("Deleting features...")
                prestashop.delete("product_features", resource_ids=ids)

    with open(f"{SCRIPT_DIR}scraper_results/products.json") as file:
        products = json.loads(file.read())

    amount = len(products)

    with ThreadPoolExecutor(max_workers=15) as executor:
        list(tqdm(executor.map(add_product, products),
             total=amount, desc="Adding products"))


def add_categories(clean: bool = False):

    if clean:
        ids = []
        for category in prestashop.get("categories")["categories"]["category"]:
            if int(category["attrs"]["id"]) not in [1, 2]:
                ids.append(int(category["attrs"]["id"]))
        if ids:
            print("Deleting categories...")
            prestashop.delete("categories", resource_ids=ids)

    with open(f"{SCRIPT_DIR}scraper_results/categories.json") as file:
        categories = json.loads(file.read())

    index = 2
    amount = sum(len(subcategories) for subcategories in
                 categories.values()) + len(categories)

    with tqdm(total=amount, desc="Adding categories") as pbar:
        for category in categories:
            try:
                parent_id = add_category(category, index)
                pbar.update(1)
                for subcategory in categories[category]:
                    add_category(subcategory, parent_id)
                    pbar.update(1)
            except Exception as e:
                print(f"Error while adding category: {category}")
                print(traceback.format_exc())


if __name__ == "__main__":
    prestashop = prestapyt.PrestaShopWebServiceDict(
        DEFAULT_LINK, "H1C47QDSEC5G8CNCAIZ49ZN6WEQEF1QK")

    category_schema = prestashop.get("categories", options={
        "schema": "blank"
    })

    product_schema = prestashop.get("products", options={
        "schema": "blank"
    })

    del product_schema["product"]["position_in_category"]
    del product_schema["product"]["associations"]["combinations"]

    feature_schema = prestashop.get("product_features", options={
        "schema": "blank"
    })

    feature_option_schema = prestashop.get("product_feature_values", options={
        "schema": "blank"
    })

    add_categories(clean=True)
    add_products(clean=True)
