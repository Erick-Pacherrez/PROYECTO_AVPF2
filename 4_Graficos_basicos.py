# Paso 4: histogramas con media, mediana y moda
import plotly.express as px
from datos import cargar, DURACION, COSTO_M2

df = cargar()


def histograma(columna, titulo, etiqueta, color):
    media, mediana, moda = df[columna].mean(), df[columna].median(), df[columna].mode().iloc[0]
    fig = px.histogram(df, x=columna, nbins=20, title=titulo, color_discrete_sequence=[color],
                       labels={columna: etiqueta})
    fig.add_vline(x=media, line_dash="dash", line_color="red",
                  annotation_text=f"Media: {media:,.1f}", annotation_position="top right")
    fig.add_vline(x=mediana, line_dash="dot", line_color="black",
                  annotation_text=f"Mediana: {mediana:,.1f}", annotation_position="top")
    fig.add_vline(x=moda, line_dash="dashdot", line_color="green",
                  annotation_text=f"Moda: {moda:,.1f}", annotation_position="top left")
    fig.add_annotation(text=f"Desv. estándar: {df[columna].std():,.1f}", xref="paper",
                       yref="paper", x=1, y=1.12, showarrow=False)
    fig.update_layout(yaxis_title="Cantidad de proyectos")
    return fig


histograma(DURACION, "Distribución de la duración planificada", "Duración (días)", "steelblue").show()
histograma(COSTO_M2, "Distribución del costo por m²", "Costo por m² (S/)", "darkorange").show()
