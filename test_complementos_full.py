"""
Script de prueba para verificar la extracción de complementos
CON TODOS LOS 48 PRODUCTOS DE ROYO
"""

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from get_urls_by_brand import get_all_product_urls_from_brand
from get_complementos import extract_all_complements, generate_complements_csv

def test_complementos_full():
    print("=" * 80)
    print("TEST COMPLETO: Extracción de Complementos (48 productos Royo)")
    print("=" * 80)
    
    # Configurar Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Obtener TODAS las URLs de productos Royo
        BRAND_URL = "https://www.todomueblesdebano.com/marcas/royo/"
        print(f"\n>> Obteniendo URLs de productos Royo...")
        
        product_urls_with_context = get_all_product_urls_from_brand(driver, BRAND_URL)
        product_urls = [p['url'] for p in product_urls_with_context]
        
        print(f"[OK] Se encontraron {len(product_urls)} productos")
        
        # Extraer complementos
        unique_complements, complement_mapping, key_to_uuid, stats = extract_all_complements(driver, product_urls)
        
        # Mostrar estadísticas
        print(f"\n{'=' * 80}")
        print("RESULTADOS DEL TEST COMPLETO:")
        print(f"{'=' * 80}")
        print(f"Productos procesados: {stats['total_products_processed']}")
        print(f"Productos con complementos: {stats['total_products_with_complements']}")
        print(f"Total complementos extraídos: {stats['total_complements_extracted']}")
        print(f"Complementos únicos: {stats['total_unique_complements']}")
        print(f"\nClaves únicas por tipo:")
        print(f"  - Por REF: {stats['unique_keys_by_type']['by_ref']}")
        print(f"  - Por SLUG: {stats['unique_keys_by_type']['by_slug']}")
        print(f"  - Por NAME: {stats['unique_keys_by_type']['by_name']}")
        print(f"  - Por UUID: {stats['unique_keys_by_type']['by_uuid']}")
        
        if unique_complements:
            # Generar CSV
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            csv_filename, key_to_prestashop_id = generate_complements_csv(unique_complements, timestamp)
            
            print(f"\n{'=' * 80}")
            print(f"[OK] CSV generado: {csv_filename}")
            print(f"[OK] IDs de PrestaShop mapeados: {len(key_to_prestashop_id)}")
            print(f"{'=' * 80}")
            
            # Análisis por categoría
            print(f"\nDistribución por tipo de complemento:")
            tipo_count = {}
            for comp in unique_complements.values():
                tipo = comp.get('complement_type_name', 'Desconocido')
                tipo_count[tipo] = tipo_count.get(tipo, 0) + 1
            
            for tipo, count in sorted(tipo_count.items(), key=lambda x: x[1], reverse=True):
                print(f"  - {tipo}: {count} complementos")
            
            # Mostrar algunos ejemplos por categoría
            print(f"\nEjemplos de complementos por categoría:")
            tipos_mostrados = set()
            for i, (key, comp) in enumerate(unique_complements.items(), 1):
                tipo = comp.get('complement_type_name', 'Desconocido')
                if tipo not in tipos_mostrados:
                    print(f"\n  {tipo}:")
                    print(f"    - {comp.get('name', 'Sin nombre')}")
                    print(f"      REF: {comp.get('ref', 'N/A')}")
                    print(f"      PrestaShop ID: {key_to_prestashop_id.get(key, 'N/A')}")
                    tipos_mostrados.add(tipo)
                
                if len(tipos_mostrados) >= 7:  # Mostrar hasta 7 tipos
                    break
        else:
            print("\n[!] No se encontraron complementos")
        
    except Exception as e:
        print(f"\n[ERROR] Error en el test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("\n>> Test finalizado.")

if __name__ == "__main__":
    test_complementos_full()
