"""
Script de prueba para verificar la extracción de complementos
"""

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from get_complementos import extract_all_complements, generate_complements_csv

def test_complementos():
    print("=" * 80)
    print("TEST: Extracción de Complementos")
    print("=" * 80)
    
    # Configurar Selenium
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--log-level=3")
    
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # URLs de prueba (solo 3 productos para testing)
        test_urls = [
            "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-easy-2-cajones-suspendido-con-lavabo-de-ceramica-enzo.html",
            "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-alfa-2-cajones.html",
            "https://www.todomueblesdebano.com/conjunto-mueble-de-bano-royo-vitale-con-patas-3-cajones.html"
        ]
        
        print(f"\n>> Probando con {len(test_urls)} productos...")
        
        # Extraer complementos
        unique_complements, complement_mapping, key_to_uuid, stats = extract_all_complements(driver, test_urls)
        
        # Mostrar estadísticas
        print(f"\n{'=' * 80}")
        print("RESULTADOS DEL TEST:")
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
            
            # Mostrar algunos ejemplos de complementos
            print(f"\nEjemplos de complementos extraídos:")
            for i, (key, comp) in enumerate(list(unique_complements.items())[:5], 1):
                print(f"\n  {i}. {comp.get('name', 'Sin nombre')}")
                print(f"     REF: {comp.get('ref', 'N/A')}")
                print(f"     Tipo: {comp.get('complement_type', 'N/A')}")
                print(f"     UUID: {comp.get('id', 'N/A')}")
                print(f"     PrestaShop ID: {key_to_prestashop_id.get(key, 'N/A')}")
        else:
            print("\n[!] No se encontraron complementos en los productos de prueba")
        
    except Exception as e:
        print(f"\n[ERROR] Error en el test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
        print("\n>> Test finalizado.")

if __name__ == "__main__":
    test_complementos()
