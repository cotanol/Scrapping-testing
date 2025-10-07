"""
Test de integración: Verifica que la extracción de complementos y el mapeo funcionen correctamente
con 3 productos antes de correr el script completo.
"""

import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from get_complementos import extract_all_complements, generate_complements_csv

# URLs de prueba (3 productos)
test_urls = [
    "https://www.decorabano.com/muebles-de-bano/royo-group/165cm-life-1712-life-1713",
    "https://www.decorabano.com/muebles-de-bano/royo-group/100cm-life-900-life-903",
    "https://www.decorabano.com/muebles-de-bano/royo-group/80cm-life-700-life-703"
]

print("🧪 TEST DE INTEGRACIÓN: Complementos + Mapeo")
print("=" * 60)

# Configurar Selenium
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--log-level=3")

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service, options=options)

try:
    # PASO 1: Extraer complementos
    print("\n📦 PASO 1: Extrayendo complementos de 3 productos...")
    stats = extract_all_complements(driver, test_urls)

    print(f"  ✅ Total extraído: {stats['total_extracted']}")
    print(f"  ✅ Únicos: {stats['unique_count']}")
    print(f"  ✅ Por REF: {stats['dedup_by_ref']}")
    print(f"  ✅ Por SLUG: {stats['dedup_by_slug']}")

    # PASO 2: Generar CSV y obtener mapeo
    print("\n📄 PASO 2: Generando CSV y mapeo de IDs...")
    csv_name, key_to_prestashop_id = generate_complements_csv(
        stats['unique_complements'],
        start_id=5001
    )

    print(f"  ✅ CSV generado: {csv_name}")
    print(f"  ✅ Complementos en mapeo: {len(key_to_prestashop_id)}")

    # PASO 3: Mostrar algunos ejemplos del mapeo
    print("\n🔍 PASO 3: Ejemplos de mapeo unique_key → PrestaShop ID:")
    for i, (key, ps_id) in enumerate(list(key_to_prestashop_id.items())[:5], 1):
        print(f"  {i}. {key[:50]}... → ID {ps_id}")

    # PASO 4: Verificar que el mapeo contiene los productos de prueba
    print("\n🔗 PASO 4: Verificando mapeo por producto...")
    product_uuids = [
        "03c5eaf4-d3f3-41e7-a091-e0d18acb1c85",  # Life 1712-1713
        "11c19fa9-8e43-49a2-bc08-9f45e4f0f8e8",  # Life 900-903
        "c6e3e3a3-79fb-4e20-a3c0-48e7faa68f46"   # Life 700-703
    ]

    for uuid in product_uuids:
        matching_keys = [k for k in key_to_prestashop_id.keys() if uuid in k]
        print(f"  • Producto {uuid[:8]}...: {len(matching_keys)} complementos mapeados")

    print("\n✅ TEST DE INTEGRACIÓN COMPLETADO")
    print("=" * 60)
    print("\n💡 Si ves complementos mapeados, la integración está funcionando correctamente.")
    print("   Puedes proceder a ejecutar royo_prestashop_ftp.py con confianza.")
    
finally:
    driver.quit()
