
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# Importa los colores definidos en colors.py
from colors import BACKGROUND_COLOR, TITLE_COLOR

st.set_page_config(
    page_title="Dashboard Fashion Products",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Carga y aplica el CSS base de styles.css
def load_local_css(file_name: str):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"No se encontró el archivo {file_name}. Verifica la ruta.")

load_local_css("styles.css")

# Aplica los colores desde colors.py al fondo y a los títulos
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {BACKGROUND_COLOR};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {TITLE_COLOR};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🧵 Dashboard de Fashion Products")

# Carga de datos
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
    return pd.read_csv(candidates[0])

df = load_data()

# Normaliza nombres esperados según tu CSV
COL_BRAND   = "Brand"        if "Brand"        in df.columns else None
COL_CAT     = "Category"     if "Category"     in df.columns else None
COL_PRICE   = "Price"        if "Price"        in df.columns else None
COL_RATING  = "Rating"       if "Rating"       in df.columns else None
COL_COLOR   = "Color"        if "Color"        in df.columns else None
COL_SIZE    = "Size"         if "Size"         in df.columns else None
COL_PNAME   = "Product Name" if "Product Name" in df.columns else None

# Tipos
if COL_PRICE is not None:
    df[COL_PRICE] = pd.to_numeric(df[COL_PRICE], errors="coerce")
if COL_RATING is not None:
    df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors="coerce")

# Filtros
st.markdown("### Filtros generales")

df_filt = df.copy()

c1, c2 = st.columns(2)

# Filtro de Marca
if COL_BRAND:
    brands = sorted(df[COL_BRAND].dropna().unique().tolist())
    sel_brands = c1.multiselect("Marca", brands)
    if sel_brands:
        df_filt = df_filt[df_filt[COL_BRAND].isin(sel_brands)]

# Filtro de Categoría
if COL_CAT:
    cats = sorted(df[COL_CAT].dropna().unique().tolist())
    sel_cats = c2.multiselect("Categoría", cats)
    if sel_cats:
        df_filt = df_filt[df_filt[COL_CAT].isin(sel_cats)]

st.markdown("---")

# KPIs
k1, k2, k3, k4 = st.columns(4)

# KPI 1: Total de productos
k1.metric("Productos (filtrados)", f"{len(df_filt):,}")

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

# KPI 4: Nº de marcas
if COL_BRAND:
    n_brands = df_filt[COL_BRAND].nunique(dropna=True)
    k4.metric("Marcas distintas", f"{n_brands:,}")
else:
    k4.metric("Marcas distintas", "—")

st.markdown("---")

# Pestañas de gráficas
tab1, tab2, tab3 = st.tabs([
    "🏷️ Top marcas (conteo)",
    "📦 Precio por categoría (box)",
    "💸 Precio vs Rating (scatter)"
])

#  Top marcas
with tab1:
    st.subheader("Top marcas por número de productos")

    if COL_BRAND:
        all_brands = df_filt[COL_BRAND].dropna().unique()

        if len(all_brands) == 0:
            st.info("No hay datos para las marcas con los filtros actuales.")
        elif len(all_brands) == 1:
            # Solo una marca: no usamos slider
            top_brand = (
                df_filt.groupby(COL_BRAND, dropna=True)
                      .size()
                      .reset_index(name="Productos")
                      .sort_values("Productos", ascending=False)
            )
            st.info("Solo hay una marca con los filtros actuales.")
            fig1 = px.bar(
                top_brand, x="Productos", y=COL_BRAND,
                orientation="h",
                text="Productos",
                title="Única marca disponible (por conteo de productos)"
            )
            fig1.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=450
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            # 2+ marcas: ahora sí usamos slider
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
                top_brand, x="Productos", y=COL_BRAND,
                orientation="h",
                text="Productos",
                title=f"Top {top_n} marcas (por conteo de productos)"
            )
            fig1.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                height=450
            )
            st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No se encontró la columna de marca (Brand).")


# Boxplot precio por categoría
with tab2:
    st.subheader("Distribución de precio por categoría (Box Plot)")
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
                    tmp, x=COL_CAT, y=COL_PRICE, points="suspectedoutliers",
                    title="Precio por categoría"
                )
                fig2.update_layout(
                    xaxis_title="Categoría",
                    yaxis_title="Precio",
                    height=480
                )
                st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Se necesita 'Price' numérica y 'Category' para esta gráfica.")

# Scatter Precio vs Rating
with tab3:
    st.subheader("Relación Precio vs. Rating")

    if (COL_PRICE and COL_RATING and
        pd.api.types.is_numeric_dtype(df_filt[COL_PRICE]) and
        pd.api.types.is_numeric_dtype(df_filt[COL_RATING])):

        pmin, pmax = float(df_filt[COL_PRICE].min()), float(df_filt[COL_PRICE].max())
        rmin, rmax = float(df_filt[COL_RATING].min()), float(df_filt[COL_RATING].max())

        c3, c4 = st.columns(2)
        price_range = c3.slider(
            "Rango de precio (para este gráfico)",
            min_value=float(round(pmin, 2)),
            max_value=float(round(pmax, 2)),
            value=(float(round(pmin, 2)), float(round(pmax, 2)))
        )
        rating_range = c4.slider(
            "Rango de rating (para este gráfico)",
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
                df_scatter, x=COL_PRICE, y=COL_RATING,
                color=color_by,
                hover_data=hover,
                title="Precio vs Rating (color por categoría o marca)"
            )
            fig3.update_layout(
                xaxis_title="Precio",
                yaxis_title="Rating",
                height=480
            )
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Se necesitan columnas numéricas 'Price' y 'Rating' para el scatter.")

# Tabla y descarga
with st.expander("🔽 Ver datos filtrados"):
    st.dataframe(df_filt, use_container_width=True, height=380)
    csv = df_filt.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Descargar CSV filtrado",
        data=csv,
        file_name="fashion_products_filtrado.csv",
        mime="text/csv"
    )
