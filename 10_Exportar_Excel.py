# Paso extra: exportar resultados a Excel (como en el AVPF-1), ahora con pestañas de riesgo y costos
import pandas as pd
from datos import cargar, COSTO, DURACION, COSTO_M2

df = cargar()
resumen = df[[DURACION, COSTO, COSTO_M2, "indice_riesgo"]].describe()
por_tipo = df.groupby("tipo_proyecto").agg(
    proyectos=("id_proyecto", "count"),
    presupuesto_soles=(COSTO, "sum"),
    costo_m2_promedio=(COSTO_M2, "mean"),
    costo_dia_promedio=("costo_por_dia_soles", "mean"),
    duracion_promedio=(DURACION, "mean"),
    riesgo_promedio=("indice_riesgo", "mean"),
).round(2)
contingencia = df.groupby("nivel_riesgo").agg(
    proyectos=("id_proyecto", "count"),
    costo_base=(COSTO, "sum"),
    contingencia=("contingencia_soles", "sum"),
    costo_con_contingencia=("costo_con_contingencia", "sum"),
).reindex(["Bajo", "Medio", "Alto"]).round(2)
criticas_globales = df[df[COSTO_M2] > df[COSTO_M2].mean()].sort_values(COSTO_M2, ascending=False)
criticas_relativas = df[df["critica_relativa"]].sort_values("desviacion_vs_tipo", ascending=False)

archivo = "Reporte_AVPF2.xlsx"
with pd.ExcelWriter(archivo, engine="openpyxl") as escritor:
    df.to_excel(escritor, sheet_name="Dataset_Procesado", index=False)
    resumen.to_excel(escritor, sheet_name="Resumen_Estadistico")
    por_tipo.to_excel(escritor, sheet_name="Por_Tipo")
    contingencia.to_excel(escritor, sheet_name="Contingencia_por_riesgo")
    criticas_globales.to_excel(escritor, sheet_name="Criticas_vs_promedio", index=False)
    criticas_relativas.to_excel(escritor, sheet_name="Criticas_vs_su_tipo", index=False)
print(f"Resultados exportados en: {archivo}")
