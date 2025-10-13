"""
Script de prueba para verificar la deduplicación de características
"""

# Simular technical_data con duplicados
technical_data = [
    {"attribute": {"name": "Serie"}, "options": [{"option": {"value_string": "Easy"}}], "position": 0},
    {"attribute": {"name": "Serie"}, "options": [{"option": {"value_string": "Easy"}}], "position": 0},
    {"attribute": {"name": "5 cm"}, "options": [{"option": {"value_string": "45"}}], "position": 2},
    {"attribute": {"name": "5 cm"}, "options": [{"option": {"value_string": "45"}}], "position": 2},
    {"attribute": {"name": "Material del Lavabo"}, "options": [{"option": {"value_string": "Cerámica"}}], "position": 14},
    {"attribute": {"name": "Material del Lavabo"}, "options": [{"option": {"value_string": "Cerámica"}}], "position": 14},
]

def clean_html_text(text):
    """Función de limpieza básica"""
    return str(text).strip() if text else ""

# ANTES (con duplicados)
print("=" * 60)
print("ANTES (Método antiguo - CON DUPLICADOS):")
print("=" * 60)
features_list_old = [f"{clean_html_text(item['attribute']['name'])}:{clean_html_text(item['options'][0]['option']['value_string'])}:{item.get('position', 0)}"
                 for item in technical_data if item.get('attribute') and item.get('options')]
print(f"Total características: {len(features_list_old)}")
for i, feature in enumerate(features_list_old, 1):
    print(f"  {i}. {feature}")

# DESPUÉS (sin duplicados)
print("\n" + "=" * 60)
print("DESPUÉS (Método nuevo - SIN DUPLICADOS):")
print("=" * 60)
features_dict = {}
for item in technical_data:
    if item.get('attribute') and item.get('options'):
        attr_name = clean_html_text(item['attribute']['name'])
        attr_value = clean_html_text(item['options'][0]['option']['value_string'])
        position = item.get('position', 0)
        # Solo añadir si no existe, para evitar duplicados
        if attr_name not in features_dict:
            features_dict[attr_name] = f"{attr_name}:{attr_value}:{position}"

features_list_new = list(features_dict.values())
print(f"Total características: {len(features_list_new)}")
for i, feature in enumerate(features_list_new, 1):
    print(f"  {i}. {feature}")

print("\n" + "=" * 60)
print(f"✅ Reducción: {len(features_list_old)} → {len(features_list_new)} características")
print(f"✅ Eliminados: {len(features_list_old) - len(features_list_new)} duplicados")
print("=" * 60)
