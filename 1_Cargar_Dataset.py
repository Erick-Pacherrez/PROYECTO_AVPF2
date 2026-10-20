# Paso 1: cargar el dataset y revisar su estructura
from datos import cargar

df = cargar(limpio=False, calculadas=False)

print(df.head())
df.info()
print(df.shape)
print(df["tipo_proyecto"].value_counts())
print(df["particion"].value_counts())
