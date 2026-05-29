# Bitácora de limpieza

Registro de las decisiones tomadas para pasar desde la planilla original de COCHILCO a una base usable para el análisis exploratorio.

## Datos recibidos

- Archivo original: `produccion_cobre_mina_empresa_mensual.xlsx`
- Fuente: COCHILCO, Producción de Cobre Mina por Empresa Mensual
- Fecha de descarga o entrega: 2026-05-26

## Problemas detectados

- La planilla venía como reporte, no como tabla lista para trabajar: traía encabezados institucionales, filas mensuales, resúmenes anuales y una nota de fuente.
- Los nombres de columnas tenían espacios, acentos, paréntesis y mayúsculas, lo que hacía incómodo usarlos directamente en Python.
- Después de quedarnos solo con filas mensuales había 156 meses, desde enero de 2014 hasta diciembre de 2026.
- Los meses de abril a diciembre de 2026 aparecían con `total_chile == 0`. Se interpretaron como meses futuros o sin producción informada, no como producción real igual a cero.
- No quedaron celdas faltantes (`NA`) en la base limpia en formato ancho.
- No se detectaron filas duplicadas ni fechas mensuales duplicadas en la base limpia.
- Hay valores muy altos o bajos en algunas variables, pero se trataron como posibles eventos reales de producción y no como errores automáticos.

## Decisiones de limpieza

- Eliminar encabezados institucionales, filas de resumen anual y nota de fuente.
- Mantener solo registros mensuales, identificados por tener una fecha válida.
- Estandarizar nombres de columnas: minúsculas, sin acentos, sin espacios y con guion bajo.
- Convertir la columna `fecha` a tipo fecha y las columnas de producción a valores numéricos.
- Eliminar 9 meses sin producción nacional informada: abril a diciembre de 2026.
- No imputar valores, porque la base limpia no quedó con `NA`.
- Conservar los ceros de faenas específicas en el formato ancho, porque pueden indicar meses sin producción en esa faena.
- Crear una segunda versión en formato largo para comparar empresa/faena con mayor facilidad. Esta versión no viene de otra fuente: sale de reorganizar las columnas de faenas del formato ancho.
- En el formato largo se dejaron solo registros con producción positiva por empresa/faena, para que los promedios por faena no se mezclen con meses sin operación o sin producción.

## Dataset final

- Archivo limpio generado: `datos/limpios/produccion_cobre_mensual_limpio_ancho.csv`
- Archivo adicional en formato largo: `datos/limpios/produccion_cobre_mensual_limpio_largo.csv`
- Resumen por empresa/faena: `datos/limpios/resumen_produccion_por_empresa.csv`
- Período final analizado: enero de 2014 a marzo de 2026
- Filas finales formato ancho: 147
- Columnas finales formato ancho: 44
- Filas finales formato largo: 5.694
- Columnas finales formato largo: 5
- Observación: el formato ancho sirve para mirar la evolución mensual completa del total nacional y de cada columna; el formato largo sirve para resumir y comparar faenas sin escribir el mismo cálculo muchas veces.
