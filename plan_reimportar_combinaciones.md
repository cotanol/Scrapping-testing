# Plan: Limpiar y reimportar combinaciones del producto 132

## ⚠️ IMPORTANTE: Backup primero

1. Ve a **Producto 132 → Combinaciones**
2. Toma una captura de pantalla de todas las combinaciones
3. O exporta el producto completo como respaldo

---

## 🗑️ PASO 1: Eliminar combinaciones del producto 132

1. Ve a **Catálogo → Productos**
2. Busca "Royo Dai" (ID 132)
3. Haz clic en **"Editar"**
4. Ve a la pestaña **"Combinaciones"**
5. Selecciona **TODAS las combinaciones** (checkbox superior)
6. En el menú desplegable "Acciones en masa", selecciona **"Eliminar"**
7. Confirma la eliminación
8. **NO elimines el producto, solo las combinaciones**

---

## 🧹 PASO 2: Limpiar atributos basura (OPCIONAL pero recomendado)

**Solo si estos atributos NO se usan en otros productos:**

1. Ve a **Catálogo → Atributos y Características**
2. Busca y elimina estos atributos genéricos **si no los usas**:

   - [ ] Attribute_1
   - [ ] Attribute_2
   - [ ] Attribute_3
   - [ ] Attribute_4
   - [ ] Opción 1
   - [ ] Opción 2
   - [ ] Paper Type
   - [ ] Dimension

3. **CONSERVA estos atributos importantes:**
   - ✅ Medida
   - ✅ Acabado
   - ✅ Espejo
   - ✅ Tamaño (si lo usas)
   - ✅ Color (si lo usas)
   - ✅ Color mueble (si lo usas)

---

## 📥 PASO 3: Reimportar combinaciones

1. Ve a **Configuración Avanzada → Importar**
2. Selecciona **"Combinaciones"** como tipo de entidad
3. Sube el archivo: `20251007195104-royo-combinations_import.csv`
4. Configura las opciones:

   - ✅ **Separador:** `;` (punto y coma)
   - ✅ **Múltiples separador de valores:** `,` (coma)
   - ✅ **Eliminar todos los productos antes de la importación:** ❌ NO
   - ✅ **Usar referencia de producto como clave:** ❌ NO (usa Product ID)
   - ✅ **Omitir miniaturas de regeneración:** ✅ SÍ (para ir más rápido)
   - ✅ **Forzar todos los números de identificación:** ❌ NO

5. Haz clic en **"Siguiente paso"**

---

## 🗺️ PASO 4: Mapear columnas correctamente

Asegúrate que las columnas estén mapeadas así:

| Columna del CSV                | Campo de PrestaShop                        |
| ------------------------------ | ------------------------------------------ |
| Product ID                     | Product ID\*                               |
| Product reference              | Referencia de producto                     |
| Attribute (Name:Type:Position) | Atributo (Nombre:Tipo:Posición)\*          |
| Value (Value:Position)         | Valor (Valor:Posición)\*                   |
| Supplier reference             | Referencia de proveedor                    |
| Reference                      | Referencia                                 |
| EAN13                          | EAN13                                      |
| UPC                            | UPC                                        |
| MPN                            | MPN                                        |
| Wholesale price                | Precio de coste                            |
| Impact on price                | Impacto en el precio                       |
| Ecotax                         | Impuesto ecológico                         |
| Quantity                       | Cantidad                                   |
| Minimal quantity               | Cantidad mínima                            |
| Low stock level                | Nivel de stock bajo                        |
| Low stock alert                | Enviar email cuando el stock sea menor que |
| Impact on weight               | Impacto en el peso                         |
| Default (0 = No, 1 = Yes)      | Por defecto (0 = No, 1 = Sí)               |
| Combination available date     | Fecha de disponibilidad                    |
| Image URLs (x,y,z...)          | URLs de imágenes (x,y,z...)                |
| Image alt texts (x,y,z...)     | Textos alternativos de imágenes            |
| Delete existing images         | Eliminar imágenes existentes               |

---

## ✅ PASO 5: Importar

1. Haz clic en **"Importar"**
2. Espera a que termine (puede tardar unos minutos si hay muchas combinaciones)
3. Revisa el log de importación:
   - ✅ Combinaciones importadas correctamente
   - ⚠️ Si hay errores, anótalos

---

## 🔧 PASO 6: Configurar combinación por defecto

1. Ve a **Producto 132 → Combinaciones**
2. Busca una combinación común (ej: "80 cm + Blanco brillo + Sin espejo")
3. Marca el **radio button "Por defecto"** (última columna)
4. Guarda cambios

---

## 🧽 PASO 7: Limpiar caché

1. Ve a **Configuración Avanzada → Rendimiento**
2. Haz clic en **"Limpiar caché"**
3. También limpia el caché del navegador (Ctrl + Shift + Delete)
4. Prueba en modo incógnito

---

## 🎯 PASO 8: Verificar en el frontend

1. Abre el producto 132 en el frontend
2. Verifica que aparezcan los 3 selectores:
   - ✅ Medida (60 cm, 80 cm, 100 cm)
   - ✅ Acabado (Blanco brillo, Arena mate, etc.)
   - ✅ Espejo (Espejo oferta del pack, Sin espejo, etc.)

---

## 🐛 Si aún no funciona después de reimportar:

### Verifica en DevTools (F12):

1. Abre el producto en el frontend
2. Presiona F12 → Pestaña "Console"
3. Busca errores JavaScript
4. Copia y pega cualquier error que veas

### Verifica el HTML:

1. F12 → Pestaña "Elements"
2. Busca `<select` o `<div class="product-variants"`
3. ¿Existen 3 selectores o solo 2?

---

## 💡 Alternativa: Importar solo producto 132

Si quieres importar SOLO las combinaciones del producto 132 (no todas):

1. Crea un CSV temporal solo con el producto 132:

   ```bash
   # En PowerShell:
   Select-String -Path "20251007195104-royo-combinations_import.csv" -Pattern "^132;" |
   Select-Object -First 1 | Out-File "temp_dai_combinations.csv" -Encoding UTF8

   # Agregar header:
   Get-Content "20251007195104-royo-combinations_import.csv" -First 1 |
   Set-Content "temp_dai_combinations_final.csv" -Encoding UTF8

   Select-String -Path "20251007195104-royo-combinations_import.csv" -Pattern "^132;" |
   ForEach-Object { $_.Line } | Add-Content "temp_dai_combinations_final.csv" -Encoding UTF8
   ```

2. Importa ese CSV temporal

---

## 📊 Resumen:

- ✅ Elimina combinaciones del producto 132
- ✅ Limpia atributos genéricos (Attribute_1, etc.)
- ✅ Reimporta el CSV de combinaciones
- ✅ Configura combinación por defecto
- ✅ Limpia caché
- ✅ Prueba en frontend
