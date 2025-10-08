"""
Test para extraer TODOS los precios (original y con descuento) del producto Royo Dai (ID 132)
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-dai.html"
    print(f"🔍 Navegando a: {url}\n")
    driver.get(url)
    
    wait = WebDriverWait(driver, 10)
    time.sleep(3)
    
    # Buscar todos los elementos de precio
    print("📋 BUSCANDO TODOS LOS PRECIOS EN LA PÁGINA:\n")
    
    # Precio principal (span.price)
    try:
        price_main = driver.find_element(By.CSS_SELECTOR, "span.price")
        print(f"✅ span.price: {price_main.text}")
    except:
        print("❌ No se encontró span.price")
    
    # Precio original tachado (si existe)
    try:
        price_original = driver.find_element(By.CSS_SELECTOR, ".price-before-discount, .regular-price, .old-price, del.price, s.price")
        print(f"✅ Precio tachado: {price_original.text}")
    except:
        print("⚠️  No se encontró precio tachado")
    
    # Buscar en todos los spans con clase que contenga "price"
    all_price_spans = driver.find_elements(By.CSS_SELECTOR, "[class*='price']")
    print(f"\n📊 Total de elementos con 'price' en clase: {len(all_price_spans)}")
    
    unique_prices = set()
    for span in all_price_spans:
        text = span.text.strip()
        if text and '€' in text:
            unique_prices.add(text)
    
    print("\n💰 PRECIOS ÚNICOS ENCONTRADOS:")
    for price in sorted(unique_prices):
        print(f"   - {price}")
    
    # Extraer __NUXT__ data para ver precios de la API
    print("\n📦 EXTRAYENDO DATOS DEL __NUXT__:")
    script_content = driver.find_element(By.ID, "__NUXT_DATA__").get_attribute("textContent")
    
    # Buscar precios en el JSON
    import re
    # Buscar pvp_web, pvp_supplier, etc.
    pvp_matches = re.findall(r'"pvp_\w+":(\d+)', script_content)
    
    if pvp_matches:
        print("\n💵 PRECIOS EN __NUXT__ (en céntimos):")
        # Buscar contexto alrededor
        for match in re.finditer(r'"(pvp_\w+)":(\d+)', script_content):
            field_name = match.group(1)
            price_cents = int(match.group(2))
            price_euros = price_cents / 100
            print(f"   - {field_name}: {price_cents} céntimos → {price_euros:.2f}€")
    
    print("\n" + "="*70)
    print("ANÁLISIS:")
    print("="*70)
    
    # Calcular descuento si hay dos precios
    prices_list = []
    for price_text in unique_prices:
        price_clean = price_text.replace('€', '').replace('.', '').replace(',', '.').strip()
        try:
            prices_list.append(float(price_clean))
        except:
            pass
    
    if len(prices_list) >= 2:
        prices_list.sort(reverse=True)
        precio_original = prices_list[0]
        precio_descuento = prices_list[1]
        descuento = precio_original - precio_descuento
        porcentaje = (descuento / precio_original) * 100
        
        print(f"💰 Precio ORIGINAL: {precio_original:.2f}€")
        print(f"🏷️  Precio con DESCUENTO: {precio_descuento:.2f}€")
        print(f"💵 Descuento: {descuento:.2f}€ ({porcentaje:.1f}%)")
        print(f"\n📊 SIN IVA (÷ 1.21):")
        print(f"   Original: {precio_original/1.21:.2f}€")
        print(f"   Con descuento: {precio_descuento/1.21:.2f}€")
    else:
        print(f"ℹ️  Solo se encontró un precio: {prices_list[0] if prices_list else 'N/A'}€")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
