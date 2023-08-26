# Israel Pasaca

import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import random
import seaborn as sns

categoria_venta = "RECARGAS"

st.title("Análisis de Ventas ")
st.sidebar.title("Análisis de Ventas")

st.markdown("Se muestra el análisis de ventas")
st.sidebar.markdown("Se muestra el análisis de ventas")


@st.cache_data(persist=True)
def cargar_datos():
    global categoria_venta
    ventas_url = "./ventasPreProcessed.csv"
    pdvs_url = "./pdvsPreProcessed.csv"
    creditos_url = "./creditosPreProcessed.csv"
    # data_ventas = pd.read_csv(ventas_url)
    p = 0.009
    data_ventas = pd.read_csv(
        ventas_url, header=0, skiprows=lambda i: i > 0 and random.random() > p
    )
    data_ventas = data_ventas.dropna()
    data_ventas["fecha"] = pd.to_datetime(data_ventas["fecha"], format="%Y%m%d")
    data_ventas = data_ventas.sort_values(by="fecha")

    data_pdvs = pd.read_csv(pdvs_url)
    data_creditos = pd.read_csv(creditos_url)

    # Parametros: RECARGAS, RECAUDACION, TVPAGA
    data_ventas2 = data_ventas[data_ventas["categoria"] == categoria_venta]
    Q1 = data_ventas2["ventas"].quantile(0.25)
    Q3 = data_ventas2["ventas"].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers_df = data_ventas2[
        (data_ventas2["ventas"] < lower_bound) | (data_ventas2["ventas"] > upper_bound)
    ]
    outliers_count = outliers_df["idmerchant"].value_counts()
    top_outliers_merchants = outliers_count.head(50).index
    top_merchants_info = data_pdvs[data_pdvs["idmerchant"].isin(top_outliers_merchants)]
    return data_ventas, data_pdvs, data_creditos, top_merchants_info


def ventasXtiempo():
    mean_sales = data_ventas["ventas"].mean()
    std_sales = data_ventas["ventas"].std()
    upper_limit = mean_sales + 2 * std_sales  # se trabaja con 95%
    outliers = data_ventas[data_ventas["ventas"] > upper_limit]
    figure = plt.figure(figsize=(20, 20))
    plt.plot(data_ventas["fecha"], data_ventas["ventas"], label="Ventas", color="blue")
    plt.scatter(
        outliers["fecha"], outliers["ventas"], color="red", label="Ventas Inusuales"
    )
    plt.axhline(y=mean_sales, color="green", linestyle="--", label="Media de Ventas")
    plt.axhline(y=upper_limit, color="orange", linestyle="--", label="Límite Superior")
    plt.title("Ventas a lo largo del tiempo")
    plt.xlabel("fecha")
    plt.ylabel("ventas")
    plt.legend()
    return figure


def ventasXcategoria():
    categorias = data_ventas["categoria"].unique()
    sns.set(style="whitegrid")
    colores = sns.color_palette("Set2", n_colors=len(categorias))
    figure = plt.figure(figsize=(20, 20))
    sns.boxplot(x="categoria", y="ventas", data=data_ventas, order=categorias)
    plt.xticks(rotation=45)
    plt.title("Distribución de Ventas por Categoría")
    plt.xlabel("Categoría")
    plt.ylabel("Ventas")
    return figure


def ciudadyactividadXrecargas():
    global categoria_venta
    figure = plt.figure(figsize=(15, 15))
    sns.set(style="whitegrid")
    sns.countplot(data=top_merchants_info, x="ciudad", hue="actividad")
    plt.xticks(rotation=45)
    plt.title("Relación entre Ciudad y Categoría - " + categoria_venta)
    plt.xlabel("Ciudad")
    plt.ylabel("Cantidad")
    plt.legend(title="Actividad")
    plt.tight_layout()
    return figure


def ciudadXcanal():
    sns.set(style="whitegrid")
    figure = plt.figure(figsize=(15, 15))
    sns.countplot(x="ciudad", hue="canal", data=top_merchants_info)
    plt.xticks(rotation=45)
    plt.title("Relación entre Ciudad y Canal")
    plt.xlabel("Ciudad")
    plt.ylabel("Cantidad")
    plt.legend(title="Canal")
    return figure


data_ventas, data_pdvs, data_creditos, top_merchants_info = cargar_datos()
# print(data_ventas.head(), data_creditos.head(), data_pdvs.head())

st.sidebar.subheader("Seleccione el tipo de gráfica")
radio_options = (
    "Ventas por Tiempo",
    "Ventas por Categoría",
    "Relación entre Ciudad y Categoría",
    "Relación entre Ciudad y Canal",
)
opcion = st.sidebar.radio("Seleccione uno", radio_options, key=0)

if (len(opcion)) > 0:
    index = radio_options.index(opcion)
    if index == 0:
        st.pyplot(ventasXtiempo())
    elif index == 1:
        st.pyplot(ventasXcategoria())
    elif index == 2:
        categoria_opciones = ("RECARGAS", "RECAUDACION", "TVPAGA")
        cat_opcion = st.sidebar.radio(
            "Seleccione un tipo de categoría", categoria_opciones, key=1
        )
        st.pyplot(ciudadyactividadXrecargas())
    elif index == 3:
        st.pyplot(ciudadXcanal())
    else:
        st.pyplot(ventasXtiempo())

    # st.pyplot(ventasXtiempo())


# data_opcion = data[data.airline.isin(opcion)]
