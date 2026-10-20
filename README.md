# AVPF-2 – Gestión de proyectos de construcción 

100 proyectos de construcción con 14 variables. En el AVPF-1 se usaron solo algunas; aquí se usan todas.

## Cómo ejecutarlo
1. Abre esta carpeta en VS Code (File → Open Folder).
2. En la terminal: `pip install -r requirements.txt`
3. Ejecuta en orden: `python 1_Cargar_Dataset.py`, `python 2_Limpieza_y_KPI.py`, ... hasta `8_Modelo_predictivo.py`
4. Análisis extra: `python 11_Analisis_Riesgos.py` y `python 12_Analisis_Costos.py`
5. Excel: `python 10_Exportar_Excel.py`
6. Dashboard: `python -m streamlit run 9_Dashboard_Integral.py`
   o abre `9_Dashboard_propia_web.html` en el navegador y carga `projects.csv`.

## Qué se agregó
- Uso de todas las variables: pisos, capacidad del contratista, recursos, madurez de gestión,
  exposición climática y de suministro, madurez tecnológica.
- Índice de riesgo (0 a 1): promedio de las exposiciones y de las deficiencias de contratista, recursos,
  gestión y tecnología (pesos iguales; es una propuesta del grupo y puede ajustarse en `datos.py`).
- **Análisis de riesgos** (`11_`): niveles bajo/medio/alto (terciles del índice), riesgo por tipo, factores de riesgo
  por tipo, matriz de riesgo vs costo por m², y correlación de cada factor con costo y duración.
- **Análisis de costos** (`12_`): presupuesto por tipo, diagrama de Pareto, costo por día de obra, obras críticas
  respecto al promedio de su propio tipo, y reserva de contingencia según el nivel de riesgo.
- KPIs y comparación por tipo de proyecto.
- Modelos de regresión para costo y duración, usando la partición train/validation/test del dataset.
- Dashboard interactivo con filtro por tipo de proyecto, y reporte Excel con más pestañas.

## Supuestos editables (en `datos.py`)
- `CONTINGENCIA`: porcentaje de reserva por nivel de riesgo (5 %, 10 %, 15 %). Son valores de ejemplo: el grupo
  debe justificarlos o ajustarlos.
- `UMBRAL_DESVIACION`: 20 % por encima del costo por m² promedio de su tipo para considerar una obra crítica relativa.

## Nota
El dataset no tiene fechas, por eso el paso 7 (serie temporal) se reemplazó por la tendencia según el número de pisos.
