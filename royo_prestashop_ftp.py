import json
import csv
import re
import time
from ftplib import FTP
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Importamos el módulo para obtener URLs
from get_urls_by_brand import get_all_product_urls_from_brand

# --- CONFIGURACIÓN ---
BRAND_URL_TO_SCRAPE = "https://www.todomueblesdebano.com/marcas/royo/"
TAX_RATE = 1.21
PRODUCT_OUTPUT_FILENAME = 'products_import.csv'
COMBINATION_OUTPUT_FILENAME = 'combinations_import.csv'

# --- CABECERAS CSV PRESTASHOP ---
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

# ================================
# 1. FUNCIÓN FTP
# ================================
def leer_configuracion_ftp(archivo_config):
    config = {}
    try:
        with open(archivo_config, "r", encoding="utf-8") as f:
            for linea in f:
                if "=" in linea:
                    clave, valor = linea.strip().split("=", 1)
                    config[clave.strip()] = valor.strip()
        return config
    except Exception as e:
        print(f"❌ Error al leer configuración FTP: {e}")
        return None

def subir_archivo_ftp(nombre_archivo, servidor, usuario, contraseña, ruta_remota="/"):
    try:
        ftp = FTP(servidor)
        ftp.login(usuario, contraseña)
        print(f"🔗 Conectado al FTP: {servidor}")
        
        directorio_actual = ftp.pwd()
        print(f"📁 Directorio actual: {directorio_actual}")
        
        if ruta_remota and ruta_remota != "/" and ruta_remota.strip():
            try:
                ftp.cwd(ruta_remota)
                print(f"📁 Cambiado a: {ruta_remota}")
            except Exception as e:
                print(f"⚠️  No se pudo cambiar a '{ruta_remota}': {e}")
                print(f"📁 Usando directorio actual: {directorio_actual}")
        
        with open(nombre_archivo, 'rb') as archivo:
            ftp.storbinary(f'STOR {nombre_archivo}', archivo)
        
        print(f"✅ Archivo '{nombre_archivo}' subido correctamente al FTP.")
        ftp.quit()
        return True
    except Exception as e:
        print(f"❌ Error al subir '{nombre_archivo}' al FTP: {e}")
        return False

# ================================
# 2. EXTRACCIÓN DATOS PRESTASHOP
# ================================
def extract_product_data(nuxt_data):
    try:
        product_data = nuxt_data['state']['product']['product']
        prices = product_data.get('prices', {})
        seo_data = product_data.get('seo', {})
        technical_data = nuxt_data['state']['product'].get('technical_data', [])
    except (KeyError, TypeError): 
        return None

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

    return {
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
        'Virtual product': 1, 'File URL': file_url, 'Number of allowed downloads': '', 'Expiration date': '',
        'Number of days': '', 'ID / Name of shop': 1, 'Advanced stock management': 0, 'Depends On Stock': 0,
        'Warehouse': 0, 'Acessories  (x,y,z...)': ''
    }

def extract_combinations_data(nuxt_data):
    try:
        product_data = nuxt_data['state']['product']['product']
        variants = product_data.get('variants', [])
        if not variants: return []
        
        product_id = product_data.get('id')
        base_price_cents = product_data.get('prices', {}).get('pvp_web', 0)
        all_combinations = []
    except (KeyError, TypeError): return []

    # Crear mapping de atributos
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

# ================================
# 3. FUNCIÓN PRINCIPAL INTEGRADA
# ================================
def main():
    print("🚀 INICIANDO: Scraper Royo + PrestaShop + FTP")
    print("=" * 50)
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    
    driver = None
    all_products_data = []
    all_combinations_data = []
    
    try:
        # PASO 1: Obtener todas las URLs de productos
        print("🔍 PASO 1: Obteniendo URLs de productos...")
        service = Service(executable_path='chromedriver.exe')
        driver = webdriver.Chrome(service=service, options=options)
        
        product_urls_with_context = get_all_product_urls_from_brand(driver, BRAND_URL_TO_SCRAPE)
        print(f"✅ Se encontraron {len(product_urls_with_context)} productos")
        
        # PASO 2: Procesar cada producto
        print(f"\n🕷️ PASO 2: Procesando productos (formato PrestaShop)...")
        for i, product_info in enumerate(product_urls_with_context, 1):
            product_url = product_info['url']
            print(f"  [{i}/{len(product_urls_with_context)}] Procesando: {product_url}")
            
            driver.get(product_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__nuxt")))
            nuxt_data = driver.execute_script("return window.__NUXT__;")
            
            # Extraer datos del producto
            product_data = extract_product_data(nuxt_data)
            if product_data:
                all_products_data.append(product_data)
            
            # Extraer combinaciones
            combinations_data = extract_combinations_data(nuxt_data)
            all_combinations_data.extend(combinations_data)
            
            time.sleep(1)  # Pausa entre productos
        
        # PASO 3: Generar CSVs
        print(f"\n📄 PASO 3: Generando archivos CSV...")
        
        if all_products_data:
            with open(PRODUCT_OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=PRODUCT_CSV_HEADERS, delimiter=';')
                writer.writeheader()
                writer.writerows(all_products_data)
            print(f"✅ {PRODUCT_OUTPUT_FILENAME} generado ({len(all_products_data)} productos)")
        
        if all_combinations_data:
            with open(COMBINATION_OUTPUT_FILENAME, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=COMBINATION_CSV_HEADERS, delimiter=';')
                writer.writeheader()
                writer.writerows(all_combinations_data)
            print(f"✅ {COMBINATION_OUTPUT_FILENAME} generado ({len(all_combinations_data)} combinaciones)")
        
        # PASO 4: Subir a FTP
        print(f"\n📤 PASO 4: Subiendo archivos definitivos al FTP...")
        config = leer_configuracion_ftp("ftp_config.txt")
        
        if config:
            if all_products_data:
                subir_archivo_ftp(PRODUCT_OUTPUT_FILENAME, config.get("servidor"), 
                                config.get("usuario"), config.get("contraseña"), 
                                config.get("ruta_remota", "/"))
            
            if all_combinations_data:
                subir_archivo_ftp(COMBINATION_OUTPUT_FILENAME, config.get("servidor"), 
                                config.get("usuario"), config.get("contraseña"), 
                                config.get("ruta_remota", "/"))
            
            print(f"\n🎉 PROCESO COMPLETADO: {len(all_products_data)} productos procesados y subidos al FTP!")
        else:
            print(f"\n⚠️ Archivos generados pero sin configuración FTP.")
            print(f"📄 Archivos disponibles localmente:")
            print(f"   • {PRODUCT_OUTPUT_FILENAME}")
            print(f"   • {COMBINATION_OUTPUT_FILENAME}")
    
    except Exception as e:
        print(f"❌ Error en el proceso: {e}")
    finally:
        if driver:
            driver.quit()
            print("\n👋 Scraper finalizado.")

if __name__ == "__main__":
    main()