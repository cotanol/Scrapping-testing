# Solución: Selector "Espejo" no aparece en frontend PrestaShop

## Pasos a seguir (en orden de probabilidad):

### ✅ PASO 1: Configurar combinación por defecto

1. Ve a: **Catálogo → Productos → Royo Dai (ID 132)**
2. Pestaña **"Combinaciones"**
3. Busca una combinación común (ej: "80 cm + Blanco brillo + Sin espejo")
4. Marca el checkbox **"Por defecto"** al lado de esa combinación
5. Haz clic en **"Guardar"**
6. Ve a **Configuración Avanzada → Rendimiento → "Limpiar caché"**
7. Prueba en el frontend (Ctrl + F5 para refrescar)

### ✅ PASO 2: Verificar tipo de atributo

1. Ve a: **Catálogo → Atributos y Características**
2. Busca **"Espejo" (ID 7)**
3. Haz clic en **"Editar"**
4. Verifica que **"Tipo de atributo"** sea: **"Lista desplegable"** o **"Botón de radio"**
5. NO debe ser "Color" o "Textura"
6. Marca **"Público en la página del producto" = SÍ**
7. Guarda cambios

### ✅ PASO 3: Verificar orden de atributos

1. Ve a: **Catálogo → Atributos y Características**
2. Asegúrate que el orden sea:
   - 1. **Medida** (posición 0)
   - 2. **Acabado** (posición 1)
   - 3. **Espejo** (posición 2)
3. Usa las flechas ↑↓ para reordenar si es necesario
4. Guarda cambios

### ✅ PASO 4: Probar con tema Classic

1. Ve a: **Diseño → Tema**
2. Activa el tema **"Classic"** (tema por defecto de PrestaShop)
3. Prueba si ahora aparece el selector de "Espejo"
4. Si funciona, el problema es el tema personalizado

### ✅ PASO 5: Limpiar todo el caché

1. **PrestaShop:** Configuración Avanzada → Rendimiento → "Limpiar caché"
2. **Navegador:** Ctrl + Shift + Delete → Borrar caché
3. Prueba en **modo incógnito**

### ✅ PASO 6: Re-importar combinaciones (último recurso)

Si nada funciona:

1. Ve al producto 132 en PrestaShop
2. **ELIMINA TODAS las combinaciones** del producto
3. Ve a **Configuración Avanzada → Importar**
4. Importa de nuevo el archivo: `20251007195104-royo-combinations_import.csv`
5. Selecciona **"Combinaciones"** como tipo de importación
6. Mapea las columnas correctamente
7. Marca **"Product ID" = 132** en el filtro si es posible
8. Importa

## 🎯 Problema detectado más común:

**Falta combinación por defecto**. Sin una combinación marcada como "por defecto", PrestaShop no sabe qué mostrar inicialmente y puede no renderizar los selectores.

## 📊 Para verificar en el navegador:

1. Abre el producto en el frontend
2. Presiona **F12** (DevTools)
3. Ve a la pestaña **"Console"**
4. Busca errores JavaScript relacionados con "combinations" o "attributes"
5. Si hay errores, cópialos y avísame

## 🔧 Si el CSV está mal:

El formato actual es correcto:

```
"Medida:select:0,Acabado:select:1,Espejo:select:2"
```

Si necesitas regenerar el CSV con otro formato, avísame.
