import streamlit as st
import os
import pandas as pd
import math
import matplotlib.pyplot as plt
from lexical_analysis import process_episodes


# Configuración
st.set_page_config(layout="wide")
st.title("ANÁLISIS LÉXICO: 'FROM' - TEMPORADA 1")

# Cargar datos
data_folder = os.path.join(os.path.dirname(__file__), 'data')
results, global_top = process_episodes(data_folder)
df = pd.DataFrame(results)

# Sidebar
selected_episode = st.sidebar.selectbox(
    "Seleccionar episodio", 
    options=sorted(df['episode'].unique()),
    index=0
)

# Métricas principales
st.header("Resumen de la Temporada")
cols = st.columns(4)
cols[0].metric("Total de palabras", df['total_words'].sum())
cols[1].metric("Palabras únicas", df['unique_words'].sum())
cols[2].metric("Densidad léxica promedio", f"{df['lexical_density'].mean():.4f}")
cols[3].metric("Episodio más denso", f"Episodio {df.loc[df['lexical_density'].idxmax(), 'episode']}")

# Análisis por episodio
ep_data = df[df['episode'] == selected_episode].iloc[0]
st.header(f"Análisis del Episodio {selected_episode}")

# Top palabras
st.subheader("Top 10 Palabras")
if ep_data['top_words']:
    col1, col2 = st.columns(2)
    
    with col1:
        words, counts = zip(*ep_data['top_words'])
        fig, ax = plt.subplots()
        ax.bar(words, counts, color='#8B0000')
        ax.set_ylabel("Frecuencia")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)
    
else:
    st.warning("No se encontraron palabras significativas")

# Análisis global
st.header("Análisis de Toda la Temporada")
st.subheader("Top 50 Palabras Más Frecuentes")

if global_top:
    cols_count = 5
    rows = math.ceil(len(global_top) / cols_count)
    
    for i in range(rows):
        columns = st.columns(cols_count)
        for j in range(cols_count):
            idx = i * cols_count + j
            if idx < len(global_top):
                word, count = global_top[idx]
                with columns[j]:
                    st.metric(word, count)
else:
    st.warning("No se encontraron datos globales")