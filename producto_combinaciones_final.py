import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- CONFIGURACIÓN DE TIEMPOS ---
WAIT_TIMEOUT = 10
PAUSE_AFTER_CLICK = 2
PAUSE_COMPLEMENTS = 1.5

def get_current_view_data(soup):
    """Función auxiliar para extraer los datos de la vista actual del panel."""
    items_list = []
    item_containers = soup.select("div.colour-item, div.product-attribute-list-component")
    for item in item_containers:
        subtitle = ''
        if 'colour-item' in item.get('class', []):
            name = item.get('title', 'N/A').replace('color ', '')
            price = 'N/A'
        else:
            name_elem = item.select_one("span.font-normal, span.font-medium")
            subtitle_elem = item.select_one("span.text-xs")
            price_elem = item.select_one("div.attribute-price span")
            name = name_elem.text.strip() if name_elem else 'N/A'
            subtitle = subtitle_elem.text.strip() if subtitle_elem else ''
            price = price_elem.text.strip() if price_elem else 'N/A'
        items_list.append({'nombre': name, 'subtitulo': subtitle, 'precio_extra': price})
    return items_list

# --- FUNCIÓN REUTILIZABLE ---
def scrape_all_product_combinations(driver, product_url):
    """
    Función experta que recibe un driver y una URL, y devuelve un diccionario
    con todas las combinaciones extraídas del configurador del producto.
    """
    driver.get(product_url)
    print(f"\n--- Analizando combinaciones para: {product_url} ---")
    
    full_configuration = {}

    try:
        print("-> Abriendo el configurador de producto...")
        entry_point = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Ver todas las opciones')] | //div[contains(@class, 'item-attribute')]"))
        )
        entry_point.click()
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.header-sidebar")))
        print("-> Configurador abierto.")
    except Exception:
        print(f"-> Este producto no parece tener un configurador de opciones.")
        return {"Combinaciones": {}}

    while True:
        try:
            time.sleep(PAUSE_AFTER_CLICK)
            try:
                view_more_button = driver.find_element(By.XPATH, "//span[contains(@class, 'underline') and contains(text(), 'Ver más')]")
                driver.execute_script("arguments[0].click();", view_more_button)
                time.sleep(PAUSE_AFTER_CLICK)
            except Exception:
                pass
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            title_element = soup.select_one("div.product-description-component span.text-xl, div.product-description-component span.text-2xl")
            section_title = title_element.text.strip() if title_element else "Desconocido"
            print(f"--- Extrayendo datos de: '{section_title}' ---")

            if "complementos" in section_title.lower():
                # (La lógica de complementos no cambia)
                complements_data = {}
                category_buttons = driver.find_elements(By.CSS_SELECTOR, "a.cat-list-component-link")
                category_names = [btn.text.split('\n')[0] for btn in category_buttons]
                
                for i in range(len(category_names)):
                    driver.find_elements(By.CSS_SELECTOR, "a.cat-list-component-link")[i].click()
                    current_cat_name = category_names[i]
                    time.sleep(PAUSE_COMPLEMENTS)
                    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-attribute-list-comp")))
                    complements_data[current_cat_name] = get_current_view_data(BeautifulSoup(driver.page_source, 'html.parser'))
                    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'go-back-sidebar') and (contains(., 'Volver'))]"))).click()
                    time.sleep(PAUSE_COMPLEMENTS)
                    WebDriverWait(driver, WAIT_TIMEOUT).until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.cat-list-component-link")))
                
                full_configuration[section_title] = complements_data
                driver.find_element(By.XPATH, "//button[contains(text(), 'Finalizar')]").click()
                break
            else:
                # --- LÓGICA DE NAVEGACIÓN MEJORADA ---
                data = get_current_view_data(soup)
                full_configuration[section_title] = data
                print(f"  -> Se encontraron {len(data)} opciones.")
                
                try:
                    # Prioridad 1: Intentar continuar
                    continue_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Continuar')]")
                    continue_button.click()
                    print("  -> Pasando a la siguiente sección...")
                except:
                    # Prioridad 2: Si no, intentar finalizar
                    finish_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Finalizar')]")
                    finish_button.click()
                    print("  -> Clic en 'Finalizar', cerrando configurador.")
                    break # Salimos del bucle principal
        
        except Exception:
            print("\n-> Fin del configurador (no se encontró 'Continuar' ni 'Finalizar').")
            break
            
    return {"Combinaciones": full_configuration}