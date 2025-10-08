"""
Test para extraer precio TACHADO (original) del producto Royo Logika
URL: https://www.todomueblesdebano.com/mueble-de-bano-con-encimera-de-madera-royo-logika.html
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-logika-encimera.html"
    print(f"🔍 Navegando a: {url}\n")
    driver.get(url)
    
    wait = WebDriverWait(driver, 10)
    time.sleep(3)
    
    print("="*70)
    print("EXTRAYENDO PRECIOS (CON LA NUEVA LÓGICA)")
    print("="*70)
    
    # Buscar todos los elementos que contengan precio (€)
    all_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '€')]")
    print(f"\n📊 Encontrados {len(all_elements)} elementos con '€'")
    
    precios_encontrados = []
    for elem in all_elements[:15]:  # Limitar a primeros 15
        texto = elem.text.strip()
        if texto and '€' in texto and len(texto) < 20:  # Filtrar textos cortos con €
            precios_encontrados.append(texto)
            print(f"   - {texto}")
    
    # Intentar obtener precio TACHADO primero
    precio_original_con_iva = None
    try:
        original_price_element = driver.find_element(By.CSS_SELECTOR, "span.line-through")
        original_price_text = original_price_element.text.strip()
        print(f"\n✅ Precio ORIGINAL (tachado): {original_price_text}")
        
        # Limpiar y convertir
        price_clean = original_price_text.replace('€', '').strip()
        if ',' in price_clean and '.' in price_clean:
            price_clean = price_clean.replace('.', '').replace(',', '.')
        elif ',' in price_clean:
            price_clean = price_clean.replace(',', '.')
        
        precio_original_con_iva = float(price_clean)
        precio_original_sin_iva = precio_original_con_iva / 1.21
        
        print(f"💰 Precio ORIGINAL CON IVA: {precio_original_con_iva:.2f}€")
        print(f"💵 Precio ORIGINAL SIN IVA: {precio_original_sin_iva:.2f}€")
        
    except Exception as e:
        print(f"⚠️  No se encontró precio tachado (producto sin descuento)")
        print(f"   Error: {e}")
    
    # Precio actual (con descuento)
    try:
        # Selector más específico basado en el HTML proporcionado
        price_element = driver.find_element(By.CSS_SELECTOR, "span.price, span.text-4xl.font-extrabold")
        price_text = price_element.text.strip()
        print(f"\n✅ Precio ACTUAL (con descuento): {price_text}")
        
        # Limpiar y convertir
        price_clean = price_text.replace('€', '').strip()
        if ',' in price_clean and '.' in price_clean:
            price_clean = price_clean.replace('.', '').replace(',', '.')
        elif ',' in price_clean:
            price_clean = price_clean.replace(',', '.')
        
        precio_actual_con_iva = float(price_clean)
        precio_actual_sin_iva = precio_actual_con_iva / 1.21
        
        print(f"💰 Precio ACTUAL CON IVA: {precio_actual_con_iva:.2f}€")
        print(f"💵 Precio ACTUAL SIN IVA: {precio_actual_sin_iva:.2f}€")
        
    except Exception as e:
        print(f"❌ No se encontró precio actual")
        print(f"   Error: {e}")
    
    # Calcular descuento
    if 'precio_original_con_iva' in locals() and 'precio_actual_con_iva' in locals():
        descuento = precio_original_con_iva - precio_actual_con_iva
        porcentaje_descuento = (descuento / precio_original_con_iva) * 100
        
        print("\n" + "="*70)
        print("ANÁLISIS DE DESCUENTO")
        print("="*70)
        print(f"Precio ORIGINAL: {precio_original_con_iva:.2f}€ (sin IVA: {precio_original_sin_iva:.2f}€)")
        print(f"Precio ACTUAL: {precio_actual_con_iva:.2f}€ (sin IVA: {precio_actual_sin_iva:.2f}€)")
        print(f"Descuento: {descuento:.2f}€ ({porcentaje_descuento:.2f}%)")
        
        print("\n" + "="*70)
        print("LO QUE IRÁ AL CSV DE PRESTASHOP")
        print("="*70)
        print(f"Price tax excluded: {precio_original_sin_iva:.6f}€")
        print(f"Discount amount: {descuento:.2f}€")
        print(f"Discount percent: {porcentaje_descuento:.2f}%")
        print(f"\n🎯 PrestaShop mostrará: ~~{precio_original_con_iva:.2f}€~~ → {precio_actual_con_iva:.2f}€")
        print(f"✅ IDÉNTICO a la web original")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
