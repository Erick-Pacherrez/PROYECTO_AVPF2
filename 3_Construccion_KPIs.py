# Paso 3: indicadores clave (KPIs) generales y por tipo de proyecto
from datos import cargar, COSTO, DURACION, COSTO_M2

df = cargar()

prom_m2 = df[COSTO_M2].mean()
criticas = df[df[COSTO_M2] > prom_m2]

print(f"Proyectos analizados: {len(df)}")
print(f"Costo planificado promedio: S/ {df[COSTO].mean():,.2f}")
print(f"Costo por m² promedio: S/ {prom_m2:,.2f}")
print(f"Duración promedio: {df[DURACION].mean():.1f} días")
print(f"Índice de riesgo promedio (0 a 1): {df['indice_riesgo'].mean():.3f}")
print(f"Obras críticas (costo/m² sobre el promedio): {len(criticas)} ({len(criticas)/len(df):.0%})")

print("\nKPIs por tipo de proyecto:")
por_tipo = df.groupby("tipo_proyecto").agg(
    proyectos=("id_proyecto", "count"),
    costo_m2_promedio=(COSTO_M2, "mean"),
    duracion_promedio=(DURACION, "mean"),
    riesgo_promedio=("indice_riesgo", "mean"),
).round(2)
print(por_tipo)

print("\nLos 5 proyectos con mayor índice de riesgo:")
print(df.nlargest(5, "indice_riesgo")[["id_proyecto", "tipo_proyecto", "indice_riesgo", COSTO_M2]])
