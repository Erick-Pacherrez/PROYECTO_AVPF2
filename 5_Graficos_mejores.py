# Paso 5: gráfico 3D interactivo y comparación por tipo de proyecto
import plotly.express as px
from datos import cargar, COSTO, DURACION, COSTO_M2

df = cargar()

fig3d = px.scatter_3d(
    df, x="area_m2", y=DURACION, z=COSTO,
    color="complejidad_estructural", color_continuous_scale="Viridis", opacity=0.85,
    hover_data=["id_proyecto", "tipo_proyecto", "pisos"],
    title="Área, duración y costo según la complejidad estructural",
)
fig3d.update_traces(marker={"size": 5})
fig3d.update_layout(
    scene={"xaxis_title": "Área construida (m²)", "yaxis_title": "Duración (días)",
           "zaxis_title": "Costo planificado (S/)",
           "camera": {"eye": {"x": 1.6, "y": 1.6, "z": 1.2}}},
    coloraxis_colorbar={"title": "Complejidad (0-1)"},
)
fig3d.show()

fig_caja = px.box(df, x="tipo_proyecto", y=COSTO_M2, color="tipo_proyecto", points="all",
                  title="Costo por m² según el tipo de proyecto",
                  labels={"tipo_proyecto": "Tipo de proyecto", COSTO_M2: "Costo por m² (S/)"})
fig_caja.update_layout(showlegend=False)
fig_caja.show()
