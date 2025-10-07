"""
Script de prueba para verificar extracción de precio visual de Decorabano
"""
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuración
TAX_RATE = 1.21
test_url = "https://www.todomueblesdebano.com/mueble-de-bano-dai-top-arena-royo.html"

service = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=service)

try:
    print(f"🌐 Cargando: {test_url}\n")
    driver.get(test_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "__nuxt")))
    
    # EXTRAER PRECIO VISUAL (método del script principal)
    price_element = driver.find_element(By.CSS_SELECTOR, "span.price")
    price_text = price_element.text.strip()
    
    print("=" * 80)
    print("EXTRACCIÓN DE PRECIO VISUAL")
    print("=" * 80)
    print(f"Texto original: '{price_text}'")
    
    # Limpiar y convertir
    price_text_clean = price_text.replace('€', '').strip()
    if ',' in price_text_clean and '.' in price_text_clean:
        price_text_clean = price_text_clean.replace('.', '').replace(',', '.')
    elif ',' in price_text_clean:
        price_text_clean = price_text_clean.replace(',', '.')
    
    price_with_tax = float(price_text_clean)
    price_without_tax = round(price_with_tax / TAX_RATE, 6)
    
    print(f"✅ Precio CON IVA (21%): {price_with_tax}€")
    print(f"✅ Precio SIN IVA: {price_without_tax}€")
    
    # COMPARAR CON __NUXT__
    print("\n" + "=" * 80)
    print("COMPARACIÓN CON __NUXT__")
    print("=" * 80)
    nuxt_data = driver.execute_script("return window.__NUXT__;")
    prices = nuxt_data['state']['product']['product'].get('prices', {})
    pvp_web = prices.get('pvp_web', 0) / 100
    pvp_supplier = prices.get('pvp_supplier', 0) / 100
    
    print(f"pvp_web (NUXT): {pvp_web}€")
    print(f"pvp_supplier (NUXT): {pvp_supplier}€")
    
    print("\n" + "=" * 80)
    print("RESULTADO")
    print("=" * 80)
    print(f"🎯 PRECIO ESPERADO: 390,03€ (con IVA)")
    print(f"✅ PRECIO EXTRAÍDO: {price_with_tax}€ (con IVA)")
    print(f"✅ PRECIO PARA CSV: {price_without_tax}€ (sin IVA, 'Price tax excluded')")
    print(f"✅ PrestaShop mostrará: {price_without_tax * TAX_RATE:.2f}€ (aplicando Tax rules ID 1)")
    
    if abs(price_with_tax - 390.03) < 0.01:
        print("\n🎉 ¡PERFECTO! El precio coincide con la web original")
    else:
        print(f"\n⚠️  Diferencia: {abs(price_with_tax - 390.03):.2f}€")

finally:
    driver.quit()
    print("\n✅ Test completado")

