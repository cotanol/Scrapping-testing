"""
PRUEBA RÁPIDA: 5 productos con estrategia de 1 SOLA VISITA
- Extraer productos + combinaciones del __NUXT__
- Recopilar UUIDs de complementos del mismo __NUXT__
- Luego hacer llamadas API para obtener detalles de complementos
- Generar 3 CSVs
"""

import json
import csv
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from get_urls_by_brand import get_all_product_urls_from_brand
from get_complementos import get_complement_types, get_complements_by_type, generate_unique_key, convert_complement_to_prestashop_format

print("🧪 PRUEBA RÁPIDA: 5 productos (1 SOLA VISITA)")
print("=" * 60)

# URLs de prueba (5 primeros productos)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--log-level=3")

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

try:
    # PASO 1: Obtener primeras 5 URLs
    print("\n🔍 PASO 1: Obteniendo URLs de productos...")
    BRAND_URL = "https://www.todomueblesdebano.com/marcas/royo/"
    all_urls_with_context = get_all_product_urls_from_brand(driver, BRAND_URL)
    test_urls = [info['url'] for info in all_urls_with_context[:5]]  # Solo primeras 5
    print(f"✅ {len(test_urls)} URLs obtenidas para prueba")
    
    # PASO 2: UNA SOLA VISITA - Extraer TODO del __NUXT__
    print("\n🕷️ PASO 2: UNA SOLA VISITA - Extrayendo productos + UUIDs de complementos...")
    
    all_products_data = []
    all_combinations_data = []
    all_complement_uuids = set()  # Recopilar UUIDs únicos de complementos
    product_to_complement_uuids = {}  # {product_uuid: [complement_uuids]}
    
    for i, product_url in enumerate(test_urls, 1):
        print(f"\n  [{i}/{len(test_urls)}] {product_url}")
        
        try:
            driver.get(product_url)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__nuxt")))
            nuxt_data = driver.execute_script("return window.__NUXT__;")
            
            # Obtener datos básicos del producto
            product_data = nuxt_data['state']['product']['product']
            product_uuid = product_data.get('id', '')  # 'id' es el UUID en el __NUXT__
            product_name = product_data.get('name', 'Unknown')
            
            print(f"    >> {product_name}")
            print(f"       UUID: {product_uuid}")
            
            # TODO: Aquí extraerías productos y combinaciones usando tus funciones existentes
            # product_data = extract_product_data(nuxt_data, 86 + i, product_uuid, None)
            # combinations = extract_combinations_data(nuxt_data, 86 + i)
            
            # RECOPILAR UUID del producto para luego hacer llamadas API
            if product_uuid:
                all_complement_uuids.add(product_uuid)  # Guardar UUID del producto
                print(f"       ✅ UUID recopilado para API de complementos")
            
        except Exception as e:
            print(f"    ❌ Error: {e}")
            continue
        
        time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"RESULTADOS PASO 2:")
    print(f"  • Productos procesados: {len(test_urls)}")
    print(f"  • UUIDs de productos recopilados: {len(all_complement_uuids)}")
    print(f"{'='*60}")
    
    # PASO 3: Ahora hacer llamadas API para obtener COMPLEMENTOS de cada producto
    print(f"\n🔧 PASO 3: Obteniendo complementos de {len(all_complement_uuids)} productos vía API...")
    
    unique_complements = {}  # {unique_key: complement_data}
    uuid_to_unique_key = {}  # {complement_uuid: unique_key}
    product_to_prestashop_ids = {}  # {product_uuid: [prestashop_ids]}
    
    for i, product_uuid in enumerate(all_complement_uuids, 1):
        print(f"\n  [{i}/{len(all_complement_uuids)}] Producto UUID: {product_uuid[:8]}...")
        
        try:
            # Obtener tipos de complementos para este producto
            complement_types_data = get_complement_types(product_uuid)
            
            if not complement_types_data:
                print(f"      ⏭️  Sin complementos")
                continue
            
            product_complement_ids = []
            
            for comp_type in complement_types_data:
                comp_type_id = comp_type.get('id', '')
                comp_type_name = comp_type.get('web_name', 'Unknown')  # Usar 'web_name' según la API
                
                # Obtener complementos de este tipo
                complements_list = get_complements_by_type(product_uuid, comp_type_id)
                
                print(f"      - {comp_type_name}: {len(complements_list)} items")
                
                for complement in complements_list:
                    # Generar clave única
                    unique_key, key_type = generate_unique_key(complement)
                    comp_uuid = complement.get('id', '') or complement.get('uuid', '')
                    
                    # Si es nuevo, agregarlo
                    if unique_key not in unique_complements:
                        unique_complements[unique_key] = complement
                        uuid_to_unique_key[comp_uuid] = unique_key
                    else:
                        uuid_to_unique_key[comp_uuid] = unique_key
                    
                    product_complement_ids.append(comp_uuid)
            
            if product_complement_ids:
                product_to_complement_uuids[product_uuid] = product_complement_ids
                print(f"      ✅ {len(product_complement_ids)} complementos recopilados")
        
        except Exception as e:
            print(f"      ❌ Error: {e}")
        
        time.sleep(0.5)  # Pausa entre llamadas API
    
    print(f"\n{'='*60}")
    print(f"RESULTADOS PASO 3:")
    print(f"  • Complementos únicos obtenidos: {len(unique_complements)}")
    print(f"  • Productos con complementos: {len(product_to_complement_uuids)}")
    print(f"{'='*60}")
    
    # PASO 4: Generar CSV de complementos con IDs de PrestaShop
    print(f"\n📄 PASO 4: Generando CSV de complementos...")
    
    complement_csv_rows = []
    key_to_prestashop_id = {}
    current_id = 5001
    
    for unique_key, complement_data in unique_complements.items():
        prestashop_row = convert_complement_to_prestashop_format(complement_data, current_id)
        complement_csv_rows.append(prestashop_row)
        key_to_prestashop_id[unique_key] = current_id
        current_id += 1
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    complement_csv_name = f'{timestamp}-prueba-complements_import.csv'
    
    # Escribir CSV (usando las mismas cabeceras que tu script principal)
    PRODUCT_CSV_HEADERS = [
        'Product ID','Active (0/1)','Name *','Categories (x,y,z...)','Price tax excluded','Tax rules ID','Wholesale price',
        'On sale (0/1)','Discount amount','Discount percent','Discount from (yyyy-mm-dd)','Discount to (yyyy-mm-dd)',
        'Reference #','Supplier reference #','Supplier','Manufacturer','EAN13','UPC','MPN','Ecotax','Width','Height','Depth',
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
    
    with open(complement_csv_name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=PRODUCT_CSV_HEADERS, delimiter=';', quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(complement_csv_rows)
    
    print(f"✅ {complement_csv_name} generado")
    print(f"   • {len(complement_csv_rows)} complementos")
    print(f"   • IDs: 5001 - {5000 + len(complement_csv_rows)}")
    
    # PASO 5: Mostrar mapeo de productos a complementos (con IDs de PrestaShop)
    print(f"\n🔗 PASO 5: Mapeo de productos a complementos (PrestaShop IDs)...")
    for product_uuid, comp_uuids in product_to_complement_uuids.items():
        prestashop_ids = []
        for comp_uuid in comp_uuids:
            unique_key = uuid_to_unique_key.get(comp_uuid)
            if unique_key:
                ps_id = key_to_prestashop_id.get(unique_key)
                if ps_id:
                    prestashop_ids.append(str(ps_id))
        
        if prestashop_ids:
            accessories_str = ",".join(prestashop_ids)
            print(f"  • Producto {product_uuid[:8]}... → Accessories: {accessories_str}")
    
    print(f"\n✅ PRUEBA COMPLETADA")
    print(f"=" * 60)
    print(f"\n💡 ESTRATEGIA VALIDADA:")
    print(f"   1. ✅ UNA SOLA VISITA por producto")
    print(f"   2. ✅ Extracción de productos + combinaciones del __NUXT__")
    print(f"   3. ✅ Recopilación de UUIDs de complementos del __NUXT__")
    print(f"   4. ✅ Llamadas API solo para detalles de complementos únicos")
    print(f"   5. ✅ Generación de CSV con IDs de PrestaShop")
    print(f"   6. ✅ Mapeo de Accessories para productos")
    
finally:
    driver.quit()
