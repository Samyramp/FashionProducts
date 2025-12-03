
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# Aquí defino el color principal de la app tomando como referencia el rojo de las barras
COLOR_PRIMARY = "#F63366"
COLOR_SEQUENCE = ["#F63366", "#FF6B8B", "#FF8FA3", "#C2185B", "#880E4F"]

# Aquí defino la configuración general de la página para que se vea en formato ancho
st.set_page_config(
    page_title="Fashion Analytics Studio",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aquí pongo la URL del fondo, pensando en un moodboard de moda
URL_IMAGEN_FONDO = "https://audaces.com/wp-content/uploads/2022/12/fashion-product-mix-pyramid.jpg"

# Aquí construyo el CSS para darle un estilo más editorial y mantener el mismo color protagonista
page_bg_img = f"""
<style>
/* Fondo general con imagen y degradado suave para que el texto se lea bien */
[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(135deg, rgba(255,222,233,0.92), rgba(236,240,255,0.96)),
        url("{URL_IMAGEN_FONDO}") no-repeat center center fixed;
    background-size: cover;
}}

/* Contenedor principal con efecto glassmorphism */
[data-testid="stAppViewContainer"] > .main {{
    background-color: transparent;
}}

.main .block-container {{
    background-color: rgba(255, 255, 255, 0.88);
    padding: 2rem 2.6rem;
    border-radius: 26px;
    box-shadow: 0 18px 46px rgba(0,0,0,0.16);
    backdrop-filter: blur(14px);
    max-width: 1250px;
}}

/* Estilo de la barra lateral con look más nocturno y elegante */
section[data-testid="stSidebar"], [data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #141218, #3f1230);
    color: #fceff9;
}}

section[data-testid="stSidebar"] * {{
    color: #fceff9 !important;
}}

section[data-testid="stSidebar"] .stSlider > div > div {{
    color: #fceff9 !important;
}}

/* Métricas en formato de tarjetas suaves */
div[data-testid="stMetric"] {{
    background-color: rgba(255,255,255,0.96);
    border-radius: 18px;
    padding: 1rem 1.2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.10);
    border: 1px solid rgba(255,192,203,0.7);
}}

/* Tabs con estilo de pastillas tipo menú de colección */
div[data-baseweb="tab-list"] {{
    gap: 0.75rem;
}}

button[role="tab"] {{
    border-radius: 999px;
    padding: 0.4rem 1.3rem;
    font-weight: 600;
    border: 1px solid rgba(0,0,0,0.06);
}}

/* Aquí hago que el tab seleccionado use el mismo rojo que la barra y texto blanco */
button[role="tab"][aria-selected="true"] {{
    background: linear-gradient(135deg, {COLOR_PRIMARY}, #ffb3c6);
    color: #ffffff !important;
    border-color: {COLOR_PRIMARY};
}}
button[role="tab"][aria-selected="true"] * {{
    color: #ffffff !important;
}}

/* Contenedor de las gráficas para que parezcan tarjetas */
.stPlotlyChart {{
    background-color: rgba(255,255,255,0.97);
    padding: 1rem;
    border-radius: 20px;
    box-shadow: 0 16px 40px rgba(0,0,0,0.12);
}}

/* Estilo del expander de la tabla para que vaya con el resto del diseño */
.streamlit-expanderHeader {{
    font-weight: 600;
    font-size: 0.95rem;
}}

</style>
"""

# Aquí inyecto el CSS en la app para que se apliquen los estilos
st.markdown(page_bg_img, unsafe_allow_html=True)

# Aquí creo un encabezado central usando el mismo rojo como color principal
st.markdown(
    f"""
    <div style="text-align:center; padding-bottom: 0.5rem;">
        <h1 style="
            font-size: 2.6rem;
            background: linear-gradient(120deg,{COLOR_PRIMARY},#ff6b8b,#ffb3c6);
            -webkit-background-clip: text;
            color: transparent;
            margin-bottom: 0.15rem;">
            Fashion Analytics Studio
        </h1>
        <p style="font-size: 0.95rem; color:#4a4a4a; margin-top:0.1rem;">
            Analizo cómo se comportan las marcas, precios y ratings dentro del catálogo de moda
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Aquí cargo los datos de la base de fashion products que ya tengo lista
@st.cache_data(show_spinner=True)
def load_data():
    candidates = [
        "/content/fashion_products.csv",
        "/mnt/data/fashion_products.csv",
        "fashion_products.csv"
    ]
    for p in candidates:
        if Path(p).exists():
            return pd.read_csv(p)
    # Si por alguna razón no encuentra nada, intento con el primero para forzar error visible
    return pd.read_csv(candidates[0])

df = load_data()

# Aquí normalizo los nombres de las columnas según el CSV que estoy usando
COL_BRAND   = "Brand"        if "Brand"        in df.columns else None
COL_CAT     = "Category"     if "Category"     in df.columns else None
COL_PRICE   = "Price"        if "Price"        in df.columns else None
COL_RATING  = "Rating"       if "Rating"       in df.columns else None
COL_COLOR   = "Color"        if "Color"        in df.columns else None
COL_SIZE    = "Size"         if "Size"         in df.columns else None
COL_PNAME   = "Product Name" if "Product Name" in df.columns else None

# Aquí me aseguro de que precio y rating sean numéricos
if COL_PRICE is not None:
    df[COL_PRICE] = pd.to_numeric(df[COL_PRICE], errors="coerce")
if COL_RATING is not None:
    df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors="coerce")

# Aquí hago una fila con filtros y un pequeño moodboard del estado filtrado
st.markdown("### Filtros generales")

df_filt = df.copy()

c1, c2, c3 = st.columns([1.2, 1.2, 1])

# Filtro de marca
if COL_BRAND:
    brands = sorted(df[COL_BRAND].dropna().unique().tolist())
    sel_brands = c1.multiselect("Marca", brands, placeholder="Selecciono una o varias marcas")
    if sel_brands:
        df_filt = df_filt[df_filt[COL_BRAND].isin(sel_brands)]

# Filtro de categoría
if COL_CAT:
    cats = sorted(df[COL_CAT].dropna().unique().tolist())
    sel_cats = c2.multiselect("Categoría", cats, placeholder="Elijo el tipo de moda")
    if sel_cats:
        df_filt = df_filt[df_filt[COL_CAT].isin(sel_cats)]

# Aquí genero un mini resumen tipo moodboard con el filtro actual
with c3:
    st.markdown("#### Moodboard filtrado")
    if not df_filt.empty:
        top_brand = df_filt[COL_BRAND].value_counts().idxmax() if COL_BRAND else "N/A"
        top_color = df_filt[COL_COLOR].value_counts().idxmax() if COL_COLOR else "N/A"
        avg_price = df_filt[COL_PRICE].mean() if COL_PRICE else np.nan
        st.markdown(
            f"""
            <p style="font-size:0.9rem; margin-bottom:0.2rem;"><strong>Marca protagonista:</strong> {top_brand}</p>
            <p style="font-size:0.9rem; margin-bottom:0.2rem;"><strong>Color dominante:</strong> {top_color}</p>
            <p style="font-size:0.9rem; margin-bottom:0.2rem;"><strong>Ticket promedio:</strong> ${avg_price:,.2f}</p>
            """,
            unsafe_allow_html=True
        )
    else:
        st.write("Sin resultados con estos filtros")

st.markdown("---")

# Aquí construyo los KPIs principales para ver el estado general del catálogo filtrado
k1, k2, k3, k4 = st.columns(4)

# KPI 1: Total de productos
k1.metric("Productos filtrados", f"{len(df_filt):,}")

# KPI 2: Precio promedio
if COL_PRICE and pd.api.types.is_numeric_dtype(df_filt[COL_PRICE]):
    avg_price = np.nanmean(df_filt[COL_PRICE])
    k2.metric("Precio promedio", f"${avg_price:,.2f}")
else:
    k2.metric("Precio promedio", "—")

# KPI 3: Rating promedio
if COL_RATING and pd.api.types.is_numeric_dtype(df_filt[COL_RATING]):
    avg_rating = np.nanmean(df_filt[COL_RATING])
    k3.metric("Rating promedio", f"{avg_rating:,.2f}")
else:
    k3.metric("Rating promedio", "—")

# KPI 4: Número de marcas
if COL_BRAND:
    n_brands = df_filt[COL_BRAND].nunique(dropna=True)
    k4.metric("Marcas distintas", f"{n_brands:,}")
else:
    k4.metric("Marcas distintas", "—")

st.markdown("---")

# Aquí organizo las gráficas en pestañas, como si fueran secciones de un lookbook de datos
tab1, tab2, tab3 = st.tabs([
    "Top marcas",
    "Precio por categoría",
    "Precio vs Rating"
])

# Pestaña 1: Top marcas por conteo de productos
with tab1:
    st.subheader("Top marcas por número de productos")

    if COL_BRAND:
        all_brands = df_filt[COL_BRAND].dropna().unique()

        if len(all_brands) == 0:
            st.info("No hay datos para las marcas con los filtros actuales.")
        elif len(all_brands) == 1:
            top_brand = (
                df_filt.groupby(COL_BRAND, dropna=True)
                      .size()
                      .reset_index(name="Productos")
                      .sort_values("Productos", ascending=False)
            )
            st.info("Solo hay una marca con los filtros actuales.")
            fig1 = px.bar(
                top_brand,
                x="Productos",
                y=COL_BRAND,
                orientation="h",
                text="Productos",
                title="Única marca disponible por conteo de productos",
                color_discrete_sequence=[COLOR_PRIMARY]
            )
            fig1.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=450
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            max_n = min(20, len(all_brands))
            top_n = st.slider(
                "Número de marcas a mostrar",
                min_value=2,
                max_value=max_n,
                value=min(10, max_n)
            )

            top_brand = (
                df_filt.groupby(COL_BRAND, dropna=True)
                      .size()
                      .reset_index(name="Productos")
                      .sort_values("Productos", ascending=False)
                      .head(top_n)
            )
            fig1 = px.bar(
                top_brand,
                x="Productos",
                y=COL_BRAND,
                orientation="h",
                text="Productos",
                title=f"Top {top_n} marcas por número de productos",
                color_discrete_sequence=[COLOR_PRIMARY]
            )
            fig1.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=450
            )
            st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No se encontró la columna de marca Brand.")

# Pestaña 2: Boxplot de precio por categoría
with tab2:
    st.subheader("Distribución de precio por categoría")

    if COL_PRICE and COL_CAT and pd.api.types.is_numeric_dtype(df_filt[COL_PRICE]):

        cat_counts = df_filt[COL_CAT].value_counts(dropna=True)
        all_cats = cat_counts.index.tolist()

        if len(all_cats) == 0:
            st.info("No hay categorías con los filtros actuales.")
        else:
            default_cats = all_cats[:8]
            sel_cats_tab = st.multiselect(
                "Categorías a mostrar",
                options=all_cats,
                default=default_cats
            )

            if sel_cats_tab:
                tmp = df_filt[df_filt[COL_CAT].isin(sel_cats_tab)].copy()
            else:
                tmp = df_filt.copy()

            if tmp.empty:
                st.info("No hay datos para las categorías seleccionadas.")
            else:
                fig2 = px.box(
                    tmp,
                    x=COL_CAT,
                    y=COL_PRICE,
                    points="suspectedoutliers",
                    title="Precio por categoría",
                    color_discrete_sequence=[COLOR_PRIMARY]
                )
                fig2.update_layout(
                    xaxis_title="Categoría",
                    yaxis_title="Precio",
                    height=480
                )
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Se necesita Price numérica y Category para esta gráfica.")

# Pestaña 3: Scatter Precio vs Rating
with tab3:
    st.subheader("Relación entre precio y rating")

    if (COL_PRICE and COL_RATING and
        pd.api.types.is_numeric_dtype(df_filt[COL_PRICE]) and
        pd.api.types.is_numeric_dtype(df_filt[COL_RATING])):

        pmin, pmax = float(df_filt[COL_PRICE].min()), float(df_filt[COL_PRICE].max())
        rmin, rmax = float(df_filt[COL_RATING].min()), float(df_filt[COL_RATING].max())

        c3, c4 = st.columns(2)
        price_range = c3.slider(
            "Rango de precio para este gráfico",
            min_value=float(round(pmin, 2)),
            max_value=float(round(pmax, 2)),
            value=(float(round(pmin, 2)), float(round(pmax, 2)))
        )
        rating_range = c4.slider(
            "Rango de rating para este gráfico",
            min_value=float(round(rmin, 1)),
            max_value=float(round(rmax, 1)),
            value=(float(round(rmin, 1)), float(round(rmax, 1)))
        )

        df_scatter = df_filt[
            (df_filt[COL_PRICE] >= price_range[0]) &
            (df_filt[COL_PRICE] <= price_range[1]) &
            (df_filt[COL_RATING] >= rating_range[0]) &
            (df_filt[COL_RATING] <= rating_range[1])
        ].copy()

        if df_scatter.empty:
            st.info("No hay datos dentro de los rangos seleccionados.")
        else:
            color_by = None
            if COL_CAT:
                color_by = COL_CAT
            elif COL_BRAND:
                color_by = COL_BRAND

            hover = [c for c in [COL_PNAME, COL_BRAND, COL_CAT, COL_COLOR, COL_SIZE] if c in df_scatter.columns]
            fig3 = px.scatter(
                df_scatter,
                x=COL_PRICE,
                y=COL_RATING,
                color=color_by,
                hover_data=hover,
                title="Precio vs Rating con color por categoría o marca",
                color_discrete_sequence=COLOR_SEQUENCE
            )
            fig3.update_layout(
                xaxis_title="Precio",
                yaxis_title="Rating",
                height=480
            )
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Se necesitan columnas numéricas Price y Rating para el scatter.")

# Aquí muestro la tabla filtrada y doy opción de descargarla
with st.expander("Ver datos filtrados"):
    st.dataframe(df_filt, use_container_width=True, height=380)
    csv = df_filt.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar CSV filtrado",
        data=csv,
        file_name="fashion_products_filtrado.csv",
        mime="text/csv"
    )
