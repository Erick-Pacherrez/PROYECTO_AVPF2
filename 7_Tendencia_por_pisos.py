# Paso 7: el dataset no tiene variable de tiempo (fechas), así que en lugar de la serie
# temporal se estudia cómo cambian los indicadores según el número de pisos.
import pandas as pd
import plotly.express as px
from datos import cargar, DURACION, COSTO_M2

df = cargar()

df["rango_pisos"] = pd.cut(df["pisos"], bins=[0, 5, 10, 15, 30],
                           labels=["1-5", "6-10", "11-15", "16 o más"])
tendencia = (df.groupby("rango_pisos", observed=True)[[DURACION, COSTO_M2, "indice_riesgo"]]
             .mean().round(2).reset_index())
print(tendencia)

largo = tendencia.melt(id_vars="rango_pisos", var_name="Indicador", value_name="Promedio")
fig = px.line(largo, x="rango_pisos", y="Promedio", facet_row="Indicador", markers=True,
              title="Indicadores promedio según el número de pisos",
              labels={"rango_pisos": "Número de pisos"})
fig.update_yaxes(matches=None)
fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
fig.show()
