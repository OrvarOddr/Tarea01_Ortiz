# Tarea 1: limpieza de datos

Trabajo de limpieza y análisis exploratorio usando datos de producción de cobre de la minería chilena.

## Estructura

- `datos/originales/`: planilla descargada desde COCHILCO.
- `datos/limpios/`: bases exportadas después de la limpieza.
- `notebooks/`: notebook principal, con el análisis y los gráficos.
- `scripts/`: apoyo para regenerar tablas y gráficos cuando haga falta.
- `resultados/figuras/`: gráficos producidos por el notebook.
- `presentacion_latex/`: presentación en Beamer y PDF final.
- `documento_latex/`: informe escrito en LaTeX y PDF final.

## Para ejecutar el notebook

1. Activar el entorno:

   ```bash
   source .venv/bin/activate
   ```

2. Abrir JupyterLab:

   ```bash
   source .venv/bin/activate
   jupyter lab
   ```

3. Abrir el notebook `notebooks/tarea_1_limpieza_datos.ipynb`.
4. Ejecutar las celdas en orden.

## Dataset elegido

- Tema: minería chilena.
- Fuente: COCHILCO.
- Archivo: `datos/originales/produccion_cobre_mina_empresa_mensual.xlsx`.
- Descripción: producción mensual chilena de cobre de mina por empresa/faena.
- Unidad: miles de toneladas métricas de cobre fino.
- Período útil después de limpieza inicial: enero de 2014 a marzo de 2026.

Con esta base se revisan estadísticas descriptivas, histogramas, diagramas de dispersión, valores faltantes, outliers, asimetría, concentración y acciones de limpieza.
