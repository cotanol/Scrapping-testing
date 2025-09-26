import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN ---
PRODUCT_URL = "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-nisy-2-cajones.html"
JSON_FILENAME = 'producto_combinaciones_final.json'
BASE_DOMAIN = "https://www.todomueblesdebano.com"

# --- VARIABLES GLOBALES DE TIEMPO ---
WAIT_TIMEOUT = 10
WAIT_FOR_BUTTON = 5
PAUSE_AFTER_CLICK = 3
PAUSE_SHORT = 1
PAUSE_COMPLEMENTS = 1.5 # <-- AJUSTE: Aumentado para dar más tiempo al volver

def get_current_view_data(soup):
    """
    Función auxiliar para extraer los datos de la vista actual del panel.
    """
    items_list = []
    item_containers = soup.select("div.colour-item, div.product-attribute-list-comp")
    
    for item in item_containers:
        if 'colour-item' in item.get('class', []):
            name = item.get('title', 'N/A').replace('color ', '')
            price = 'N/A'
            subtitle = ''
        else:
            name_elem = item.select_one("span.font-normal, span.font-medium")
            subtitle_elem = item.select_one("span.text-xs")
            price_elem = item.select_one("div.attribute-price span")
            name = name_elem.text.strip() if name_elem else 'N/A'
            subtitle = subtitle_elem.text.strip() if subtitle_elem else ''
            price = price_elem.text.strip() if price_elem else 'N/A'
            
        items_list.append({'nombre': name, 'subtitulo': subtitle, 'precio_extra': price})
    return items_list

def scrape_product_configuration(driver):
    """
    Función principal que abre el configurador y navega por TODAS las opciones.
    """
    full_configuration = {}

    try:
        print("-> Abriendo el configurador de producto...")
        entry_point = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ver todas las opciones')] | //div[contains(@class, 'item-attribute')]"))
        )
        entry_point.click()
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.header-sidebar")))
        print("-> Configurador abierto.")
    except Exception as e:
        print(f"-> No se pudo abrir el configurador. Error: {e}")
        return {}

    while True:
        try:
            time.sleep(PAUSE_AFTER_CLICK)
            
            try:
                view_more_button = driver.find_element(By.XPATH, "//span[contains(text(), 'Ver más')]")
                print("  -> Encontrado botón 'Ver más' dentro del panel. Haciendo clic...")
                view_more_button.click()
                time.sleep(PAUSE_AFTER_CLICK)
            except Exception:
                pass
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            title_element = soup.select_one("div.product-description-component span.text-xl, div.product-description-component span.text-2xl")
            section_title = title_element.text.strip() if title_element else "Desconocido"
            print(f"\n--- Extrayendo datos de: '{section_title}' ---")

            if "complementos" in section_title.lower():
                print("  -> Detectada sección compleja 'Complementos'.")
                complements_data = {}
                category_buttons = driver.find_elements(By.CSS_SELECTOR, "a.cat-list-component-link")
                category_names = [btn.text.split('\n')[0] for btn in category_buttons]
                
                for i in range(len(category_names)):
                    driver.find_elements(By.CSS_SELECTOR, "a.cat-list-component-link")[i].click()
                    current_cat_name = category_names[i]
                    print(f"    -> Entrando a sub-categoría: '{current_cat_name}'...")
                    
                    time.sleep(PAUSE_COMPLEMENTS) 
                    WebDriverWait(driver, WAIT_TIMEOUT).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-attribute-list-comp"))
                    )
                    
                    sub_soup = BeautifulSoup(driver.page_source, 'html.parser')
                    sub_section_title_elem = sub_soup.select_one("div.product-description-component span.text-xl")
                    sub_section_title = sub_section_title_elem.text.strip() if sub_section_title_elem else current_cat_name
                    complements_data[sub_section_title] = get_current_view_data(sub_soup)
                    
                    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'go-back-sidebar') and (contains(., 'Volver'))]"))).click()
                    print(f"    -> Volviendo a la lista de complementos.")

                    time.sleep(PAUSE_COMPLEMENTS) 
                    WebDriverWait(driver, WAIT_TIMEOUT).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "a.cat-list-component-link"))
                    )
                
                full_configuration[section_title] = complements_data
                print("  -> Buscando botón 'Finalizar' para cerrar.")
                driver.find_element(By.XPATH, "//button[contains(text(), 'Finalizar')]").click()
                break
            else:
                data = get_current_view_data(soup)
                full_configuration[section_title] = data
                print(f"  -> Se encontraron {len(data)} opciones.")
                
                print("  -> Buscando botón 'Continuar'...")
                driver.find_element(By.XPATH, "//button[contains(text(), 'Continuar')]").click()
                print("  -> Pasando a la siguiente sección...")
        
        except Exception:
            print("\n-> Fin del configurador (no se encontró 'Continuar' o 'Finalizar').")
            break
            
    return full_configuration

def main():
    print("Iniciando scraper de configuración de producto...")
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.get(PRODUCT_URL)
    
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "accept-cookies"))).click()
        print("Cookies aceptadas.")
    except Exception:
        print("Banner de cookies no encontrado.")

    product_config = scrape_product_configuration(driver)

    final_json = {"Combinaciones": product_config}

    if product_config:
        try:
            with open(JSON_FILENAME, 'w', encoding='utf-8') as f:
                json.dump(final_json, f, ensure_ascii=False, indent=4)
            print(f"\n¡ÉXITO! ✨ Configuración completa guardada en '{JSON_FILENAME}'")
        except IOError:
            print("\nERROR al escribir el archivo JSON.")
            
    driver.quit()

if __name__ == "__main__":
    main()