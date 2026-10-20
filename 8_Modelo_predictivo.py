# Paso 8: modelos de regresión para costo y duración.
# Se usa la columna "particion" del propio dataset: train / validation / test.
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from datos import cargar, x_logaritmico, COSTO, DURACION, PREDICTORES

df = cargar()
partes = {
    "entrenamiento": df[df["particion"] == "train"],
    "validación": df[df["particion"] == "validation"],
    "prueba": df[df["particion"] == "test"],
}
ent = partes["entrenamiento"]
print({k: len(v) for k, v in partes.items()})
print(f"Área máxima en prueba: {partes['prueba']['area_m2'].max():,.0f} m² "
      f"(en entrenamiento: {ent['area_m2'].max():,.0f} m²)")

# --- Modelo A: costo con regresión lineal simple en escala normal
costo_lineal = LinearRegression().fit(ent[PREDICTORES], ent[COSTO])
# --- Modelo B: costo con regresión lineal en escala logarítmica (log del área y del costo)
costo_log = LinearRegression().fit(x_logaritmico(ent), np.log(ent[COSTO]))
# --- Modelo C: duración con regresión lineal
duracion = LinearRegression().fit(ent[PREDICTORES], ent[DURACION])


def predecir_costo_log(d):
    return np.exp(costo_log.predict(x_logaritmico(d)))


def reporte(nombre, real, pred, unidad):
    print(f"  {nombre}: R² = {r2_score(real, pred):.3f} | error medio absoluto = {mean_absolute_error(real, pred):,.1f} {unidad}")


print("\n=== Costo planificado, modelo A (lineal) ===")
for nombre, d in partes.items():
    reporte(nombre, d[COSTO], costo_lineal.predict(d[PREDICTORES]), "S/")

print("\n=== Costo planificado, modelo B (logarítmico) ===")
for nombre, d in partes.items():
    reporte(nombre, d[COSTO], predecir_costo_log(d), "S/")

print("\n=== Duración (días), modelo C (lineal) ===")
for nombre, d in partes.items():
    reporte(nombre, d[DURACION], duracion.predict(d[PREDICTORES]), "días")

print("\nInfluencia en la duración (coeficientes, días por unidad):")
coef = pd.Series(duracion.coef_, index=PREDICTORES)
print(coef.reindex(coef.abs().sort_values(ascending=False).index).head(4).round(2))

# Predicción para un proyecto nuevo (puedes cambiar estos valores)
nuevo = pd.DataFrame([{
    "area_m2": 30000, "pisos": 8, "complejidad_estructural": 0.65, "capacidad_contratista": 0.76,
    "disponibilidad_recursos": 0.81, "madurez_gestion": 0.70, "exposicion_clima": 0.40,
    "exposicion_suministro": 0.40, "madurez_tecnologica": 0.65,
}])
print("\nProyecto nuevo de 30,000 m² y 8 pisos:")
print(f"Costo predicho (modelo B): S/ {predecir_costo_log(nuevo)[0]:,.0f}")
print(f"Duración predicha: {duracion.predict(nuevo)[0]:.0f} días")
