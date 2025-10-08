"""
Test para extraer precio visual del producto Royo Dai (ID 132)
URL: https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-dai.html
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configurar Chrome
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')  # Sin interfaz gráfica
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    url = "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-dai.html"
    print(f"🔍 Navegando a: {url}")
    driver.get(url)
    
    # Esperar a que cargue el precio
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.price")))
    time.sleep(2)  # Esperar un poco más para asegurar carga completa
    
    # Extraer precio
    price_element = driver.find_element(By.CSS_SELECTOR, "span.price")
    price_text = price_element.text.strip()
    
    print(f"\n✅ PRECIO EXTRAÍDO: {price_text}")
    
    # Limpiar y convertir
    price_clean = price_text.replace('€', '').strip()
    if ',' in price_clean and '.' in price_clean:
        price_clean = price_clean.replace('.', '').replace(',', '.')
    elif ',' in price_clean:
        price_clean = price_clean.replace(',', '.')
    
    price_with_tax = float(price_clean)
    price_without_tax = price_with_tax / 1.21
    
    print(f"💰 Precio CON IVA: {price_with_tax:.2f}€")
    print(f"💵 Precio SIN IVA: {price_without_tax:.2f}€")
    print(f"📊 Precio SIN IVA (6 decimales): {price_without_tax:.6f}€")
    
    # Comparar con lo esperado
    expected_price_with_tax = 436.93
    expected_price_without_tax = 361.099174
    
    print(f"\n📋 COMPARACIÓN:")
    print(f"Esperado CON IVA: {expected_price_with_tax}€")
    print(f"Extraído CON IVA: {price_with_tax:.2f}€")
    print(f"Diferencia: {abs(expected_price_with_tax - price_with_tax):.2f}€")
    
    if abs(price_without_tax - expected_price_without_tax) < 0.01:
        print("✅ Precio correcto")
    else:
        print(f"❌ Precio incorrecto - Debería ser {expected_price_without_tax:.2f}€ sin IVA")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

finally:
    driver.quit()
