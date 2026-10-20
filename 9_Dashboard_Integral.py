# Paso 9: dashboard con Streamlit  ->  python -m streamlit run 9_Dashboard_Integral.py
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots
from sklearn.linear_model import LinearRegression

from datos import (cargar, x_logaritmico, factores_riesgo, COSTO, DURACION, COSTO_M2,
                   PREDICTORES, NUMERICAS, CONTINGENCIA)

st.set_page_config(page_title="Gestión de proyectos de construcción", layout="wide")
ORDEN = ["Bajo", "Medio", "Alto"]
COLOR_RIESGO = {"Bajo": "#2a9d8f", "Medio": "#e9c46a", "Alto": "#e63946"}


@st.cache_data
def datos():
    return cargar()


todos = datos()
st.title("Gestión de proyectos de construcción: costo, plazo y riesgo")

# Filtros laterales
tipos = st.sidebar.multiselect("Tipo de proyecto", sorted(todos["tipo_proyecto"].unique()),
                               default=sorted(todos["tipo_proyecto"].unique()))
niveles = st.sidebar.multiselect("Nivel de riesgo", ORDEN, default=ORDEN)
df = todos[todos["tipo_proyecto"].isin(tipos) & todos["nivel_riesgo"].isin(niveles)]
if df.empty:
    st.warning("No hay proyectos con los filtros elegidos.")
    st.stop()
st.sidebar.download_button("Descargar datos filtrados (CSV)", df.to_csv(index=False).encode("utf-8"),
                           file_name="proyectos_filtrados.csv")

t_res, t_dist, t_costo, t_riesgo, t_corr, t_modelo = st.tabs(
    ["Resumen", "Distribución", "Costos", "Riesgos", "Correlaciones", "Predicción"])

with t_res:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Proyectos", len(df))
    c2.metric("Presupuesto total", f"S/ {df[COSTO].sum()/1e6:,.0f} M")
    c3.metric("Costo por m²", f"S/ {df[COSTO_M2].mean():,.0f}")
    c4.metric("Duración promedio", f"{df[DURACION].mean():.0f} días")
    c5.metric("Riesgo promedio", f"{df['indice_riesgo'].mean():.2f}")
    st.info(f"{int(df['critica_relativa'].sum())} proyectos superan en más de 20 % el costo por m² promedio de su tipo.")
    st.dataframe(df.head(15), width="stretch")

with t_dist:
    variable = st.selectbox("Variable", [DURACION, COSTO_M2, COSTO, "costo_por_dia_soles", "indice_riesgo"])
    st.plotly_chart(px.histogram(df, x=variable, nbins=20, color="tipo_proyecto",
                                 title=f"Distribución: {variable}"), width="stretch")

with t_costo:
    k1, k2, k3 = st.columns(3)
    k1.metric("Presupuesto base", f"S/ {df[COSTO].sum()/1e6:,.0f} M")
    k2.metric("Contingencia por riesgo", f"S/ {df['contingencia_soles'].sum()/1e6:,.0f} M")
    k3.metric("Costo con contingencia", f"S/ {df['costo_con_contingencia'].sum()/1e6:,.0f} M")
    st.caption("Contingencia: " + " · ".join(f"{n} {CONTINGENCIA[n]:.0%}" for n in ORDEN)
               + " del costo, según el nivel de riesgo (supuesto del grupo, editable en datos.py).")

    pres = df.groupby("tipo_proyecto")[COSTO].sum().reset_index().sort_values(COSTO, ascending=False)
    st.plotly_chart(px.bar(pres, x="tipo_proyecto", y=COSTO, title="Presupuesto por tipo de proyecto"),
                    width="stretch")

    ord_ = df.sort_values(COSTO, ascending=False).reset_index(drop=True)
    ord_["acum"] = ord_[COSTO].cumsum() / ord_[COSTO].sum() * 100
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_bar(x=ord_["id_proyecto"], y=ord_[COSTO], name="Costo (S/)")
    fig.add_scatter(x=ord_["id_proyecto"], y=ord_["acum"], name="% acumulado", mode="lines",
                    line={"color": "red"}, secondary_y=True)
    fig.update_layout(title="Pareto del presupuesto por proyecto")
    fig.update_yaxes(range=[0, 100], secondary_y=True)
    st.plotly_chart(fig, width="stretch")

    st.plotly_chart(px.scatter(df, x="area_m2", y=COSTO, color="tipo_proyecto", size="pisos",
                               hover_data=["id_proyecto", "complejidad_estructural"],
                               title="Área construida vs costo planificado"), width="stretch")
    st.plotly_chart(px.box(df, x="tipo_proyecto", y=COSTO_M2, color="tipo_proyecto", points="all",
                           title="Costo por m² por tipo"), width="stretch")
    st.subheader("Obras críticas respecto a su propio tipo de proyecto")
    st.dataframe(df[df["critica_relativa"]].sort_values("desviacion_vs_tipo", ascending=False)
                 [["id_proyecto", "tipo_proyecto", COSTO_M2, "desviacion_vs_tipo", "nivel_riesgo"]],
                 width="stretch")

with t_riesgo:
    st.caption("Índice de riesgo = promedio de exposición climática, exposición de suministro y las "
               "deficiencias de contratista, recursos, gestión y tecnología (0 = bajo, 1 = alto). "
               "Los niveles Bajo / Medio / Alto son los terciles de la cartera.")
    st.plotly_chart(px.histogram(df, x="tipo_proyecto", color="nivel_riesgo", barnorm="percent",
                                 category_orders={"nivel_riesgo": ORDEN}, color_discrete_map=COLOR_RIESGO,
                                 title="Niveles de riesgo por tipo de proyecto"), width="stretch")
    rm, cm = df["indice_riesgo"].mean(), df[COSTO_M2].mean()
    fig = px.scatter(df, x="indice_riesgo", y=COSTO_M2, color="tipo_proyecto", hover_data=["id_proyecto"],
                     title="Matriz de riesgo: riesgo vs costo por m²")
    fig.add_vline(x=rm, line_dash="dash", line_color="gray")
    fig.add_hline(y=cm, line_dash="dash", line_color="gray")
    st.plotly_chart(fig, width="stretch")
    f = factores_riesgo(df)
    f["tipo_proyecto"] = df["tipo_proyecto"]
    st.plotly_chart(px.imshow(f.groupby("tipo_proyecto").mean().round(2), text_auto=".2f",
                              color_continuous_scale="YlOrRd", aspect="auto",
                              title="Factores de riesgo por tipo de proyecto"), width="stretch")
    st.subheader("Proyectos con mayor riesgo")
    st.dataframe(df.nlargest(10, "indice_riesgo")[["id_proyecto", "tipo_proyecto", "indice_riesgo",
                                                    "nivel_riesgo", COSTO_M2, DURACION]], width="stretch")

with t_corr:
    st.plotly_chart(px.imshow(df[NUMERICAS].corr(), text_auto=".2f", color_continuous_scale="RdBu_r",
                              zmin=-1, zmax=1, aspect="auto"), width="stretch")
    st.caption("La correlación mide asociación lineal; no demuestra causalidad.")

with t_modelo:
    ent = todos[todos["particion"] == "train"]
    m_costo = LinearRegression().fit(x_logaritmico(ent), np.log(ent[COSTO]))
    m_dur = LinearRegression().fit(ent[PREDICTORES], ent[DURACION])
    st.write("Ingresa las características de un proyecto nuevo:")
    valores = {}
    cols = st.columns(3)
    for i, v in enumerate(PREDICTORES):
        mn, mx, md = float(todos[v].min()), float(todos[v].max()), float(todos[v].median())
        valores[v] = cols[i % 3].number_input(v, mn, mx, md)
    fila = pd.DataFrame([valores])
    costo = float(np.exp(m_costo.predict(x_logaritmico(fila))[0]))
    st.success(f"Costo predicho: S/ {costo:,.0f}")
    st.success(f"Duración predicha: {m_dur.predict(fila)[0]:.0f} días")
