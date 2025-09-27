import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

BASE_DOMAIN = "https://www.todomueblesdebano.com"
WAIT_TIMEOUT = 10
WAIT_FOR_BUTTON = 5
PAUSE_AFTER_CLICK = 3
PAUSE_SHORT = 1

def get_all_product_urls_from_brand(driver, brand_url):
    driver.get(brand_url)
    print(f"--- Accediendo a la marca: {brand_url} ---")
    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(EC.element_to_be_clickable((By.ID, "accept-cookies"))).click()
        print("  -> Cookies aceptadas.")
    except Exception:
        pass

    soup_brand = BeautifulSoup(driver.page_source, 'html.parser')
    brand_name = soup_brand.select_one("h1").text.strip()

    while True:
        try:
            load_more_button = WebDriverWait(driver, WAIT_FOR_BUTTON).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.load-more")))
            driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
            time.sleep(PAUSE_SHORT)
            load_more_button.click()
            print("  -> Clic en 'Ver más colecciones'...")
            time.sleep(PAUSE_AFTER_CLICK)
        except Exception:
            print("  -> No hay más colecciones que cargar.")
            break
            
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    collections_data = []
    collection_containers = soup.select("div.col-span-12.md\\:col-span-6.lg\\:col-span-3")
    for container in collection_containers:
        name_element = container.select_one("h3")
        link_element = container.find("a", string="Ver esta colección")
        if name_element and link_element:
            collection_name = name_element.text.strip()
            href = link_element.get('href')
            full_url = BASE_DOMAIN + href
            collections_data.append({'name': collection_name, 'url': full_url})
                
    print(f"  -> Se encontraron {len(collections_data)} colecciones.")
    
    all_product_urls_with_context = []
    for collection in collections_data:
        collection_url = collection['url']
        collection_name = collection['name']
        print(f"    --- Extrayendo URLs de la colección: {collection_name} ---")
        driver.get(collection_url)
        
        while True:
            try:
                load_more_button = WebDriverWait(driver, WAIT_FOR_BUTTON).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'load-more') and contains(text(), 'Cargar Mas')]")))
                driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
                time.sleep(PAUSE_SHORT)
                load_more_button.click()
                print("      -> Clic en 'Cargar Mas'...")
                time.sleep(PAUSE_AFTER_CLICK)
            except Exception:
                print("      -> No hay más productos que cargar.")
                break
        
        product_soup = BeautifulSoup(driver.page_source, 'html.parser')
        product_containers = product_soup.select('div.product-snippet')
        
        for container in product_containers:
            link_element = container.select_one('a[title^="Ir a"]')
            if link_element and link_element.get('href'):
                relative_url = link_element['href']
                full_url = BASE_DOMAIN + relative_url
                all_product_urls_with_context.append({
                    'marca': brand_name,
                    'coleccion': collection_name,
                    'url': full_url
                })
    
    print(f"\n  -> Se encontraron un total de {len(all_product_urls_with_context)} productos para esta marca.")
    return all_product_urls_with_context