# Paso 12 (extra): análisis de costos de la cartera de proyectos
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datos import cargar, COSTO, COSTO_M2, CONTINGENCIA, UMBRAL_DESVIACION

df = cargar()

# 1) Presupuesto por tipo de proyecto
presupuesto = df.groupby("tipo_proyecto").agg(
    proyectos=("id_proyecto", "count"),
    presupuesto_soles=(COSTO, "sum"),
    costo_m2_promedio=(COSTO_M2, "mean"),
    costo_dia_promedio=("costo_por_dia_soles", "mean"),
).sort_values("presupuesto_soles", ascending=False)
presupuesto["% del total"] = (presupuesto["presupuesto_soles"] / presupuesto["presupuesto_soles"].sum() * 100).round(1)
print("Presupuesto por tipo de proyecto:")
print(presupuesto.round(2))
px.bar(presupuesto.reset_index(), x="tipo_proyecto", y="presupuesto_soles", text="% del total",
       title="Presupuesto planificado por tipo de proyecto",
       labels={"tipo_proyecto": "Tipo de proyecto", "presupuesto_soles": "Presupuesto (S/)"}).show()

# 2) Pareto: ¿cuántos proyectos concentran el 80 % del presupuesto?
ordenado = df.sort_values(COSTO, ascending=False).reset_index(drop=True)
ordenado["acumulado_%"] = ordenado[COSTO].cumsum() / ordenado[COSTO].sum() * 100
n80 = int((ordenado["acumulado_%"] < 80).sum() + 1)
print(f"\n{n80} de {len(df)} proyectos ({n80/len(df):.0%}) concentran el 80 % del presupuesto total.")

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_bar(x=ordenado["id_proyecto"], y=ordenado[COSTO], name="Costo (S/)")
fig.add_scatter(x=ordenado["id_proyecto"], y=ordenado["acumulado_%"], name="% acumulado",
                mode="lines", line={"color": "red"}, secondary_y=True)
fig.add_hline(y=80, line_dash="dash", line_color="gray", secondary_y=True)
fig.update_layout(title="Diagrama de Pareto del presupuesto por proyecto", xaxis_title="Proyecto")
fig.update_yaxes(title_text="Costo (S/)", secondary_y=False)
fig.update_yaxes(title_text="% acumulado", range=[0, 100], secondary_y=True)
fig.show()

# 3) Costo por día de obra según tipo
px.box(df, x="tipo_proyecto", y="costo_por_dia_soles", color="tipo_proyecto", points="all",
       title="Costo por día de obra según el tipo de proyecto",
       labels={"tipo_proyecto": "Tipo de proyecto", "costo_por_dia_soles": "Costo por día (S/)"}).show()

# 4) Obras críticas: comparación con el promedio general vs con el promedio de su tipo
critica_global = df[COSTO_M2] > df[COSTO_M2].mean()
critica_tipo = df["critica_relativa"]
print(f"\nObras críticas por costo/m² sobre el promedio general: {critica_global.sum()}")
print(f"Obras críticas por más de {UMBRAL_DESVIACION:.0%} sobre el promedio de su tipo: {critica_tipo.sum()}")
print("Críticas según el promedio general, por tipo:")
print(df[critica_global]["tipo_proyecto"].value_counts().to_string())
print("\nProyectos más caros respecto a su propio tipo:")
print(df.nlargest(8, "desviacion_vs_tipo")[["id_proyecto", "tipo_proyecto", COSTO_M2, "desviacion_vs_tipo"]].to_string(index=False))

# 5) Reserva de contingencia según el nivel de riesgo (porcentajes definidos en datos.py)
cont = df.groupby("nivel_riesgo").agg(
    proyectos=("id_proyecto", "count"),
    costo_base=(COSTO, "sum"),
    contingencia=("contingencia_soles", "sum"),
).reindex(["Bajo", "Medio", "Alto"])
cont["% aplicado"] = [CONTINGENCIA[n] * 100 for n in cont.index]
print("\nReserva de contingencia por nivel de riesgo:")
print(cont.round(0))
total_base, total_cont = df[COSTO].sum(), df["contingencia_soles"].sum()
print(f"Costo total: S/ {total_base:,.0f} | Contingencia: S/ {total_cont:,.0f} ({total_cont/total_base:.1%}) | "
      f"Costo con contingencia: S/ {total_base + total_cont:,.0f}")

largo = cont.reset_index().melt(id_vars="nivel_riesgo", value_vars=["costo_base", "contingencia"],
                                var_name="Concepto", value_name="Soles")
px.bar(largo, x="nivel_riesgo", y="Soles", color="Concepto", barmode="stack",
       category_orders={"nivel_riesgo": ["Bajo", "Medio", "Alto"]},
       title="Costo base y reserva de contingencia por nivel de riesgo",
       labels={"nivel_riesgo": "Nivel de riesgo", "Soles": "Soles (S/)"}).show()
