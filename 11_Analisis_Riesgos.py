# Paso 11 (extra): análisis de riesgos de la cartera de proyectos
import pandas as pd
import plotly.express as px
from datos import cargar, factores_riesgo, COSTO, COSTO_M2, DURACION

df = cargar()
ORDEN = ["Bajo", "Medio", "Alto"]

# 1) Cuántos proyectos hay en cada nivel y cuánto presupuesto concentran
niveles = df.groupby("nivel_riesgo").agg(
    proyectos=("id_proyecto", "count"),
    riesgo_promedio=("indice_riesgo", "mean"),
    presupuesto_soles=(COSTO, "sum"),
).reindex(ORDEN)
niveles["% del presupuesto"] = (niveles["presupuesto_soles"] / niveles["presupuesto_soles"].sum() * 100).round(1)
print("Niveles de riesgo (terciles del índice):")
print(niveles.round(3))

# 2) Riesgo por tipo de proyecto
por_tipo = df.groupby("tipo_proyecto").agg(
    riesgo_promedio=("indice_riesgo", "mean"),
    pct_riesgo_alto=("nivel_riesgo", lambda s: (s == "Alto").mean() * 100),
).round(2).sort_values("riesgo_promedio", ascending=False)
print("\nRiesgo por tipo de proyecto:")
print(por_tipo)

fig = px.histogram(df, x="tipo_proyecto", color="nivel_riesgo", barnorm="percent",
                   category_orders={"nivel_riesgo": ORDEN},
                   color_discrete_map={"Bajo": "#2a9d8f", "Medio": "#e9c46a", "Alto": "#e63946"},
                   title="Distribución de niveles de riesgo por tipo de proyecto",
                   labels={"tipo_proyecto": "Tipo de proyecto", "nivel_riesgo": "Nivel de riesgo"})
fig.update_layout(yaxis_title="% de proyectos")
fig.show()

# 3) ¿Qué factor aporta más riesgo en cada tipo de proyecto?
factores = factores_riesgo(df)
factores["tipo_proyecto"] = df["tipo_proyecto"]
mapa = factores.groupby("tipo_proyecto").mean().round(2)
print("\nValor promedio de cada factor de riesgo por tipo (0 = bajo, 1 = alto):")
print(mapa)
px.imshow(mapa, text_auto=".2f", color_continuous_scale="YlOrRd", aspect="auto",
          title="Factores de riesgo por tipo de proyecto",
          labels={"color": "Riesgo (0-1)"}).show()

# 4) Matriz de riesgo: riesgo vs costo por m²
riesgo_medio, costo_medio = df["indice_riesgo"].mean(), df[COSTO_M2].mean()
df["cuadrante"] = "Riesgo y costo bajos"
df.loc[(df["indice_riesgo"] > riesgo_medio) & (df[COSTO_M2] <= costo_medio), "cuadrante"] = "Riesgo alto, costo bajo"
df.loc[(df["indice_riesgo"] <= riesgo_medio) & (df[COSTO_M2] > costo_medio), "cuadrante"] = "Riesgo bajo, costo alto"
df.loc[(df["indice_riesgo"] > riesgo_medio) & (df[COSTO_M2] > costo_medio), "cuadrante"] = "Riesgo y costo altos"
print("\nProyectos por cuadrante de la matriz de riesgo:")
print(df["cuadrante"].value_counts())
print("\nProyectos prioritarios (riesgo y costo por m² sobre el promedio):")
prioritarios = df[df["cuadrante"] == "Riesgo y costo altos"].sort_values("indice_riesgo", ascending=False)
print(prioritarios[["id_proyecto", "tipo_proyecto", "indice_riesgo", COSTO_M2]].head(8).to_string(index=False))

fig = px.scatter(df, x="indice_riesgo", y=COSTO_M2, color="tipo_proyecto", hover_data=["id_proyecto"],
                 title="Matriz de riesgo: índice de riesgo vs costo por m²",
                 labels={"indice_riesgo": "Índice de riesgo (0-1)", COSTO_M2: "Costo por m² (S/)"})
fig.add_vline(x=riesgo_medio, line_dash="dash", line_color="gray")
fig.add_hline(y=costo_medio, line_dash="dash", line_color="gray")
fig.show()

# 5) ¿Qué factores se asocian con más costo por m² y más duración?
corr = pd.DataFrame({
    "con costo por m²": factores.drop(columns="tipo_proyecto").corrwith(df[COSTO_M2]),
    "con duración": factores.drop(columns="tipo_proyecto").corrwith(df[DURACION]),
}).round(2)
print("\nCorrelación de cada factor de riesgo:")
print(corr)
