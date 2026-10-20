# Paso 2: limpieza (nulos y duplicados) y cálculo del KPI costo por m²
from datos import cargar, COSTO_M2

crudo = cargar(limpio=False, calculadas=False)
print("Valores nulos por columna:")
print(crudo.isnull().sum())
print(f"Filas duplicadas: {crudo.duplicated().sum()}")

df = cargar()
print(f"Dimensiones después de limpiar: {df.shape}")
print(df[["tipo_proyecto", "area_m2", "costo_planificado_soles", COSTO_M2, "indice_riesgo"]].head())
