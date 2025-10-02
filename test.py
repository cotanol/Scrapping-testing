import json
import csv
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIÓN ---
URL = "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-easy-2-cajones-suspendido-con-lavabo-de-ceramica-enzo.html"
TAX_RATE = 1.21
PRODUCT_OUTPUT_FILENAME = 'product_final.csv'
COMBINATION_OUTPUT_FILENAME = 'combinations_final.csv'

# --- DEFINICIÓN DE CABECERAS CSV COMPLETAS ---
PRODUCT_CSV_HEADERS = [
    'Product ID','Active (0/1)','Name *','Categories (x,y,z...)','Price tax excluded','Tax rules ID','Wholesale price',
    'On sale (0/1)','Discount amount','Discount percent','Discount from (yyyy-mm-dd)','Discount to (yyyy-mm-dd)',
    'Reference #','Supplier reference #','Supplier','Manufacturer','EAN13','UPC','Ecotax','Width','Height','Depth',
    'Weight','Delivery time of in-stock products','Delivery time of out-of-stock products with allowed orders',
    'Quantity','Minimal quantity','Low stock level','Send me an email when the quantity is under this level',
    'Visibility','Additional shipping cost','Unity','Unit price','Summary','Description','Tags (x,y,z...)',
    'Meta title','Meta keywords','Meta description','URL rewritten','Text when in stock','Text when backorder allowed',
    'Available for order (0 = No, 1 = Yes)','Product available date','Product creation date',
    'Show price (0 = No, 1 = Yes)','Image URLs (x,y,z...)','Image alt texts (x,y,z...)',
    'Delete existing images (0 = No, 1 = Yes)','Feature(Name:Value:Position)','Available online only (0 = No, 1 = Yes)',
    'Condition','Customizable (0 = No, 1 = Yes)','Uploadable files (0 = No, 1 = Yes)','Text fields (0 = No, 1 = Yes)',
    'Out of stock action','Virtual product','File URL','Number of allowed downloads','Expiration date','Number of days',
    'ID / Name of shop','Advanced stock management','Depends On Stock','Warehouse','Acessories  (x,y,z...)'
]

COMBINATION_CSV_HEADERS = [
    'Product ID*','Attribute (Name:Type:Position)*','Value (Value:Position)*','Supplier reference','Reference','EAN13',
    'UPC','Wholesale price','Impact on price','Ecotax','Quantity','Minimal quantity','Low stock level','Impact on weight',
    'Default (0 = No, 1 = Yes)','Combination available date','Image position','Image URLs (x,y,z...)',
    'Image alt texts (x,y,z...)','ID / Name of shop','Advanced Stock Managment','Depends on stock','Warehouse'
]

# ==============================================================================
# FUNCIÓN PARA EXTRAER DATOS DEL PRODUCTO PRINCIPAL (66 COLUMNAS)
# ==============================================================================
def extract_product_data(nuxt_data):
    try:
        product_data = nuxt_data['state']['product']['product']
        prices = product_data.get('prices', {})
        seo_data = product_data.get('seo', {})
        technical_data = nuxt_data['state']['product'].get('technical_data', [])
    except (KeyError, TypeError): return None

    tech_data_map = {item['attribute']['name'].lower(): item['options'][0]['option']['value_string'] 
                     for item in technical_data if item.get('attribute') and item.get('options')}
    
    price_final = prices.get('pvp_web', 0) / 100
    price_tax_excluded = round(price_final / TAX_RATE, 6) if price_final > 0 else 0
    
    on_sale = 1 if prices.get('pvp_supplier', 0) > prices.get('pvp_web', 0) else 0
    discount_amount = round((prices.get('pvp_supplier', 0) - prices.get('pvp_web', 0)) / 100, 2) if on_sale else 0

    categories_list = product_data.get('categories', [])
    categories_str = ",".join([cat['name'] for cat in categories_list if 'name' in cat])
    
    images_list = product_data.get('images', [])
    image_urls = ",".join([f"https://cdn.todomueblesdebano.com/image/upload/f_auto,q_auto/v1/{img['public_id']}" for img in images_list])
    
    features_list = [f"{item['attribute']['name']}:{item['options'][0]['option']['value_string']}:{item.get('position', 0)}"
                     for item in technical_data if item.get('attribute') and item.get('options')]

    tags = list(set([word.lower() for word in re.split(r'\s|,', product_data.get('name', '')) if len(word) > 3]))
    tags.extend([cat['name'].lower() for cat in categories_list if 'name' in cat])
    tags.append(product_data.get('supplier', {}).get('name', '').lower())

    delivery_time_obj = product_data.get('delivery_time', {})
    delivery_time = f"Entre {delivery_time_obj.get('min', '?')} y {delivery_time_obj.get('max', '?')} días" if delivery_time_obj else ""

    files_list = product_data.get('files', [])
    file_url = next((f['url'] for f in files_list if f.get('file_type') == 'data_sheet'), '')

    final_data = {
        'Product ID': product_data.get('id', ''), 'Active (0/1)': 1, 'Name *': product_data.get('name', ''),
        'Categories (x,y,z...)': categories_str, 'Price tax excluded': price_tax_excluded, 'Tax rules ID': 1,
        'Wholesale price': '', 'On sale (0/1)': on_sale, 'Discount amount': discount_amount if on_sale else '',
        'Discount percent': prices.get('web_discount', '') if on_sale else '', 'Discount from (yyyy-mm-dd)': '',
        'Discount to (yyyy-mm-dd)': '', 'Reference #': product_data.get('ref', ''), 'Supplier reference #': '',
        'Supplier': product_data.get('supplier', {}).get('name', ''), 'Manufacturer': product_data.get('supplier', {}).get('name', ''),
        'EAN13': product_data.get('ean', ''), 'UPC': '', 'Ecotax': '', 'Width': '',
        'Height': tech_data_map.get('alto seleccionable estándar', '').replace(' cm', ''),
        'Depth': tech_data_map.get('fondo seleccionable estándar', '').replace(' cm', ''), 'Weight': '',
        'Delivery time of in-stock products': delivery_time,
        'Delivery time of out-of-stock products with allowed orders': '', 'Quantity': 0, 'Minimal quantity': 1,
        'Low stock level': '', 'Send me an email when the quantity is under this level': 0, 'Visibility': 'both',
        'Additional shipping cost': '', 'Unity': '', 'Unit price': '', 'Summary': seo_data.get('short_description', ''),
        'Description': seo_data.get('description', ''), 'Tags (x,y,z...)': ",".join(list(set(tags))),
        'Meta title': seo_data.get('meta_title', ''), 'Meta keywords': '', 'Meta description': seo_data.get('meta_description', ''),
        'URL rewritten': product_data.get('slug', ''), 'Text when in stock': 'Disponible', 'Text when backorder allowed': '',
        'Available for order (0 = No, 1 = Yes)': 1, 'Product available date': '', 'Product creation date': '',
        'Show price (0 = No, 1 = Yes)': 1, 'Image URLs (x,y,z...)': image_urls, 'Image alt texts (x,y,z...)': '',
        'Delete existing images (0 = No, 1 = Yes)': 1, 'Feature(Name:Value:Position)': ";".join(features_list),
        'Available online only (0 = No, 1 = Yes)': 0, 'Condition': 'new', 'Customizable (0 = No, 1 = Yes)': 0,
        'Uploadable files (0 = No, 1 = Yes)': 0, 'Text fields (0 = No, 1 = Yes)': 0, 'Out of stock action': 0,
        'Virtual product': 1 if file_url else 0, 'File URL': file_url, 'Number of allowed downloads': '',
        'Expiration date': '', 'Number of days': '', 'ID / Name of shop': 1, 'Advanced stock management': 0,
        'Depends On Stock': 0, 'Warehouse': 0, 'Acessories  (x,y,z...)': ''
    }
    return final_data

# ==============================================================================
# FUNCIÓN PARA EXTRAER DATOS DE LAS COMBINACIONES (VERSIÓN SIMPLE Y ROBUSTA)
# ==============================================================================
def extract_combinations_data(nuxt_data):
    try:
        product_data = nuxt_data['state']['product']['product']
        variants = product_data.get('variants', [])
        if not variants: return []
        
        product_id = product_data.get('id')
        base_price_cents = product_data.get('prices', {}).get('pvp_web', 0)
        all_combinations = []
    except (KeyError, TypeError): return []

    attribute_mapping = {}
    if variants and 'options' in variants[0] and 'options' in variants[0]['options']:
        for index, option in enumerate(variants[0]['options']['options']):
            attribute_mapping[option['attribute_id']] = {"name": f"Attribute_{index+1}", "type": "select", "position": index}
    attributes_header = ",".join([f"{v['name']}:{v['type']}:{v['position']}" for v in attribute_mapping.values()])

    default_assigned = False
    for variant in variants:
        values_list = []
        for option in variant.get('options', {}).get('options', []):
            attr_id = option.get('attribute_id')
            if attr_id in attribute_mapping:
                pos = attribute_mapping[attr_id]['position']
                values_list.append(f"{option.get('name', '')}:{pos}")
        values_str = ",".join(sorted(values_list, key=lambda x: x.split(':')[1]))
        
        variant_price_cents = variant.get('prices', {}).get('pvp_web', 0)
        price_impact = round((variant_price_cents - base_price_cents) / 100, 6) if base_price_cents > 0 else 0
        
        is_default = 0
        if not default_assigned and price_impact == 0:
            is_default = 1
            default_assigned = True
            
        all_combinations.append({
            'Product ID*': product_id, 'Attribute (Name:Type:Position)*': attributes_header,
            'Value (Value:Position)*': values_str, 'Reference': variant.get('ref', ''), 'EAN13': variant.get('ean', ''),
            'Impact on price': price_impact, 'Default (0 = No, 1 = Yes)': is_default, 'Image URLs (x,y,z...)': '',
            'Supplier reference': '', 'UPC': '', 'Wholesale price': '', 'Ecotax': 0, 'Quantity': 100,
            'Minimal quantity': 1, 'Low stock level': '', 'Impact on weight': 0, 'Combination available date': '',
            'Image position': '', 'Image alt texts (x,y,z...)': '', 'ID / Name of shop': 1,
            'Advanced Stock Managment': 0, 'Depends on stock': 0, 'Warehouse': 0
        })
    return all_combinations

# ==============================================================================
# BLOQUE PRINCIPAL DE EJECUCIÓN
# ==============================================================================
if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")

    driver = None
    try:
        print("Iniciando scraper final...")
        # Usar el chromedriver local
        service = Service(executable_path='chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(URL)
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__nuxt")))
        nuxt_data = driver.execute_script("return window.__NUXT__;")
        
        # --- PROCESAR Y ESCRIBIR CSV DE PRODUCTO ---
        product_for_csv = extract_product_data(nuxt_data)
        if product_for_csv:
            with open(PRODUCT_OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=PRODUCT_CSV_HEADERS, delimiter=';')
                writer.writeheader()
                writer.writerow(product_for_csv)
            print(f"[ÉXITO] Archivo '{PRODUCT_OUTPUT_FILENAME}' generado con las 66 columnas.")
        
        # --- PROCESAR Y ESCRIBIR CSV DE COMBINACIONES ---
        combinations_for_csv = extract_combinations_data(nuxt_data)
        if combinations_for_csv:
            with open(COMBINATION_OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=COMBINATION_CSV_HEADERS, delimiter=';')
                writer.writeheader()
                writer.writerows(combinations_for_csv)
            print(f"[ÉXITO] Archivo '{COMBINATION_OUTPUT_FILENAME}' generado correctamente.")

    except Exception as e:
        print(f"Ocurrió un error en el proceso principal: {e}")
    finally:
        if driver:
            driver.quit()
            print("\nScript finalizado.")