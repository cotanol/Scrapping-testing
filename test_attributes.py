"""
Script de prueba para ver la estructura de atributos en el JSON
"""
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# URL de prueba de un producto
TEST_URL = "https://www.todomueblesdebano.com/conjuntos-de-bano/conjunto-mueble-de-bano-royo-easy-2-cajones-suspendido-con-lavabo-de-ceramica-enzo/"

print("🔍 Analizando estructura de atributos...")

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

try:
    driver.get(TEST_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__nuxt")))
    
    # Esperar más tiempo para que carguen las variantes dinámicamente
    time.sleep(3)
    
    nuxt_data = driver.execute_script("return window.__NUXT__;")
    
    print("\n📋 Estructura encontrada:\n")
    
    # 1. Verificar configuration.options.attributes
    config_attrs = nuxt_data.get('state', {}).get('product', {}).get('configuration', {}).get('options', {}).get('attributes', [])
    print(f"1. configuration.options.attributes: {len(config_attrs)} atributos")
    if config_attrs:
        for attr in config_attrs[:3]:  # Mostrar primeros 3
            print(f"   - ID: {attr.get('id')}")
            print(f"     Nombre: {attr.get('name')}")
            print(f"     Keys: {list(attr.keys())}")
    
    # 2. Verificar variantes
    variants = nuxt_data['state']['product']['product'].get('variants', [])
    print(f"\n2. Variantes encontradas: {len(variants)}")
    if variants:
        print("\n   Primera variante - estructura completa:")
        first_variant = variants[0]
        print(f"   Keys en variante: {list(first_variant.keys())}")
        
        if 'options' in first_variant:
            print(f"\n   Options structure: {list(first_variant['options'].keys())}")
            options_list = first_variant.get('options', {}).get('options', [])
            print(f"   Cantidad de opciones: {len(options_list)}")
            
            for i, opt in enumerate(options_list[:2]):  # Mostrar primeras 2
                print(f"\n   Opción {i+1}:")
                print(f"     Keys disponibles: {list(opt.keys())}")
                print(f"     attribute_id: {opt.get('attribute_id')}")
                print(f"     name (valor): {opt.get('name')}")
                if 'attribute' in opt:
                    print(f"     attribute object: {opt.get('attribute')}")
    else:
        print("   ⚠️ No se encontraron variantes. Revisando estructura product completa...")
        product = nuxt_data['state']['product']['product']
        print(f"   Keys en product: {list(product.keys())}")
    
    # 3. Guardar estructura completa para análisis
    with open('debug_nuxt_full.json', 'w', encoding='utf-8') as f:
        json.dump(nuxt_data, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Estructura COMPLETA guardada en 'debug_nuxt_full.json'")
    
finally:
    driver.quit()
