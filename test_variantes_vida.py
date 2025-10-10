"""
Test para verificar extracción de variantes/combinaciones del producto Royo Vida
URL: https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-vida.html
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import re

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-vida.html"
    print(f"🔍 Navegando a: {url}\n")
    driver.get(url)
    
    wait = WebDriverWait(driver, 10)
    time.sleep(3)
    
    # Extraer __NUXT_DATA__
    script_content = driver.find_element(By.ID, "__NUXT_DATA__").get_attribute("textContent")
    
    # Parsear JSON
    nuxt_data = json.loads(script_content)
    
    product_data = nuxt_data['state']['product']['product']
    variants = product_data.get('variants', [])
    
    print("="*70)
    print(f"PRODUCTO: {product_data.get('name', 'N/A')}")
    print("="*70)
    print(f"Total de variantes: {len(variants)}\n")
    
    # Analizar estructura de atributos
    if variants:
        print("📋 ANALIZANDO PRIMERA VARIANTE:")
        first_variant = variants[0]
        print(json.dumps(first_variant, indent=2, ensure_ascii=False))
        
        # Extraer información de atributos
        if 'options' in first_variant and 'options' in first_variant['options']:
            options_list = first_variant['options']['options']
            
            print("\n" + "="*70)
            print("ATRIBUTOS DETECTADOS:")
            print("="*70)
            
            for index, option in enumerate(options_list):
                attr_id = option.get('attribute_id')
                attr_name = option.get('name', 'N/A')
                
                # Verificar si tiene comas
                has_comma = ',' in attr_name
                comma_warning = " ⚠️ CONTIENE COMA" if has_comma else ""
                
                print(f"\nAtributo {index + 1}:")
                print(f"  ID: {attr_id}")
                print(f"  Valor: {attr_name}{comma_warning}")
                
                # Intentar obtener nombre del atributo
                if 'attribute' in option and isinstance(option['attribute'], dict):
                    friendly_name = option['attribute'].get('name') or option['attribute'].get('label')
                    if friendly_name:
                        print(f"  Nombre amigable: {friendly_name}")
        
        # Mostrar algunos ejemplos de variantes
        print("\n" + "="*70)
        print("EJEMPLOS DE VARIANTES (primeras 5):")
        print("="*70)
        
        for i, variant in enumerate(variants[:5]):
            options_names = []
            if 'options' in variant and 'options' in variant['options']:
                for opt in variant['options']['options']:
                    name = opt.get('name', 'N/A')
                    has_comma = ',' in name
                    comma_marker = " [COMA]" if has_comma else ""
                    options_names.append(f"{name}{comma_marker}")
            
            price_impact = variant.get('price_impact', 0) / 100
            ean = variant.get('ean', 'N/A')
            ref = variant.get('ref', 'N/A')
            
            print(f"\nVariante {i+1}:")
            print(f"  Opciones: {' | '.join(options_names)}")
            print(f"  Impacto precio: {price_impact:.2f}€")
            print(f"  EAN: {ean}")
            print(f"  REF: {ref}")
    
    else:
        print("⚠️  No se encontraron variantes para este producto")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
