# Paso 6: mapa de calor de correlaciones con todas las variables numéricas
import plotly.express as px
from datos import cargar, NUMERICAS

df = cargar()
corr = df[NUMERICAS].corr()

fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                aspect="auto", title="Correlación entre variables de gestión",
                labels={"color": "Correlación"})
fig.show()

print("Correlación con el costo planificado:")
print(corr["costo_planificado_soles"].drop("costo_planificado_soles").sort_values(ascending=False).round(2))
print("\nCorrelación con la duración:")
print(corr["duracion_dias"].drop("duracion_dias").sort_values(ascending=False).round(2))
