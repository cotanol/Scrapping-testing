import json
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- CONFIGURACIÓN ---
URL = "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-easy-2-cajones-suspendido-con-lavabo-de-ceramica-enzo.html"

# ==============================================================================
# FUNCIÓN PARA EXTRAER DATOS DE LAS COMBINACIONES (VERSIÓN FINAL Y ROBUSTA)
# ==============================================================================
def extract_combinations_data(nuxt_data):
    print("\n[INFO] Iniciando extracción de datos de Combinaciones (Dinámica y con Imágenes)...")
    try:
        product_data = nuxt_data['state']['product']['product']
        variants = product_data.get('variants', [])
        all_images = product_data.get('images', [])
        if not variants:
            return []
        
        product_id = product_data.get('id')
        base_price_cents = product_data.get('prices', {}).get('pvp_web', 0)
        all_combinations = []
    except KeyError:
        return []

    # --- 1. DESCUBRIMIENTO DINÁMICO DE ATRIBUTOS ---
    # Usamos la primera variante para "aprender" la estructura de los atributos
    attribute_mapping = {}
    if variants and 'options' in variants[0] and 'options' in variants[0]['options']:
        for index, option in enumerate(variants[0]['options']['options']):
            # Asignamos un nombre genérico. En PrestaShop se puede renombrar una vez.
            # El tipo "color" se puede inferir si el nombre del atributo contiene "color".
            attr_name = "Color" if "color" in option.get('name', '').lower() else f"Attribute_{index+1}"
            attr_type = "color" if attr_name == "Color" else "select"
            
            attribute_mapping[option['attribute_id']] = {
                "name": attr_name, 
                "type": attr_type, 
                "position": index
            }
    attributes_header = ",".join([f"{v['name']}:{v['type']}:{v['position']}" for v in attribute_mapping.values()])

    # --- 2. PRE-PROCESAMIENTO DEL MAPA DE IMÁGENES ---
    image_map = {}
    for image in all_images:
        url = f"https://cdn.todomueblesdebano.com/image/upload/f_auto,q_auto/v1/{image['public_id']}"
        # El campo 'attributes' en cada imagen contiene los IDs de las OPCIONES a las que pertenece
        for attr_option_id in image.get('attributes', []):
            if attr_option_id not in image_map:
                image_map[attr_option_id] = []
            image_map[attr_option_id].append(url)

    # --- 3. BUCLE PRINCIPAL SOBRE LAS VARIANTES ---
    for variant in variants:
        values_list = []
        variant_option_ids = []
        for option in variant.get('options', {}).get('options', []):
            variant_option_ids.append(option.get('option_id'))
            attr_id = option.get('attribute_id')
            if attr_id in attribute_mapping:
                pos = attribute_mapping[attr_id]['position']
                values_list.append(f"{option.get('name', '')}:{pos}")
        values_str = ",".join(sorted(values_list, key=lambda x: x.split(':')[1]))

        # --- 4. LÓGICA DE ASOCIACIÓN DE IMÁGENES ---
        variant_image_urls = []
        for option_id in variant_option_ids:
            if option_id in image_map:
                variant_image_urls.extend(image_map[option_id])
        # Eliminamos duplicados manteniendo el orden
        image_urls_str = ",".join(list(dict.fromkeys(variant_image_urls)))

        # --- Construcción de la fila ---
        variant_price_cents = variant.get('prices', {}).get('pvp_web', 0)
        price_impact = round((variant_price_cents - base_price_cents) / 100, 6) if base_price_cents > 0 else 0
        is_default = 1 if variant_price_cents == base_price_cents else 0

        combination = {
            'Product ID*': product_id,
            'Attribute (Name:Type:Position)*': attributes_header,
            'Value (Value:Position)*': values_str,
            'Reference': variant.get('ref', ''),
            'EAN13': variant.get('ean', ''),
            'Impact on price': price_impact,
            'Default (0 = No, 1 = Yes)': is_default,
            'Image URLs (x,y,z...)': image_urls_str,
            # Rellenar el resto de campos estáticos
            'Supplier reference': '', 'UPC': '', 'Wholesale price': '', 'Ecotax': 0, 'Quantity': 100, 
            'Minimal quantity': 1, 'Low stock level': '', 'Impact on weight': 0, 
            'Combination available date': '', 'Image position': '', 'Image alt texts (x,y,z...)': '', 
            'ID / Name of shop': 1, 'Advanced Stock Managment': 0, 'Depends on stock': 0, 'Warehouse': 0
        }
        all_combinations.append(combination)
        
    print(f"[INFO] Extracción de {len(all_combinations)} combinaciones finalizada.")
    return all_combinations

# ==============================================================================
# BLOQUE PRINCIPAL (No necesita cambios, solo ejecutará la nueva función)
# ==============================================================================
if __name__ == "__main__":
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        service = ChromeService()
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(URL)
        
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__nuxt")))
        nuxt_data = driver.execute_script("return window.__NUXT__;")
        
        # --- PROCESAR Y ESCRIBIR CSV DE COMBINACIONES ---
        combinations_for_csv = extract_combinations_data(nuxt_data)
        if combinations_for_csv:
            # Nos aseguramos de que las cabeceras coincidan con el formato que necesita PrestaShop
            combination_headers = [
                'Product ID*', 'Attribute (Name:Type:Position)*', 'Value (Value:Position)*', 
                'Supplier reference', 'Reference', 'EAN13', 'UPC', 'Wholesale price', 
                'Impact on price', 'Ecotax', 'Quantity', 'Minimal quantity', 
                'Low stock level', 'Impact on weight', 'Default (0 = No, 1 = Yes)', 
                'Combination available date', 'Image position', 'Image URLs (x,y,z...)', 
                'Image alt texts (x,y,z...)', 'ID / Name of shop', 'Advanced Stock Managment', 
                'Depends on stock', 'Warehouse'
            ]
            with open('combinations_final.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=combination_headers, delimiter=';')
                writer.writeheader()
                writer.writerows(combinations_for_csv)
            print("[ÉXITO] Archivo 'combinations_final.csv' generado correctamente.")

    except Exception as e:
        print(f"Ocurrió un error en el proceso principal: {e}")
    finally:
        if driver:
            driver.quit()
            print("\nScript finalizado. Navegador cerrado correctamente.")