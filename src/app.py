import streamlit as st  # Importa Streamlit para crear la interfaz web
import os  # Importa os para manejo de rutas y archivos
import pandas as pd  # Importa pandas para manipulación de datos tabulares
import matplotlib.pyplot as plt  # Importa matplotlib para gráficos
import numpy as np  # Importa numpy para operaciones numéricas
from analysis.lexical_analysis import process_episodes  # Importa función de análisis léxico
from visualization.wordcloud_generator import generate_wordcloud  # Importa función para nubes de palabras
from collections import defaultdict  # Importa defaultdict para diccionarios con valores por defecto

# Configuración de la página de Streamlit
st.set_page_config(layout="wide")  # Define el layout ancho para la app
st.title("ANÁLISIS LÉXICO: 'FROM' - EVOLUCIÓN TEMPORADA 3")  # Título principal

# Cargar datos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Obtiene el directorio base del proyecto
data_folder = os.path.join(BASE_DIR, 'data')  # Define la ruta a la carpeta de datos

@st.cache_data  # Cachea la función para evitar recargar datos innecesariamente
def load_data():
    return process_episodes(data_folder)  # Procesa los episodios y retorna resultados

results, global_top, semantic_evolution, main_themes = load_data()  # Carga los datos procesados
df = pd.DataFrame(results)  # Convierte los resultados a un DataFrame de pandas

# Calcular total de palabras
total_words = df['total_words'].sum()  # Suma el total de palabras de todos los episodios

# Sidebar
st.sidebar.header("Opciones de Análisis")  # Título del sidebar
selected_words = st.sidebar.multiselect(
    "Seleccionar palabras para seguimiento",  # Etiqueta del selector múltiple
    options=list(semantic_evolution.keys()),  # Opciones: palabras clave detectadas
    default=list(semantic_evolution.keys())[:5]  # Por defecto, las primeras 5 palabras
)

# Función para calcular bigramas
def calculate_bigrams(results):
    """Calcula los bigramas más frecuentes en toda la temporada"""
    bigram_count = {}  # Diccionario para contar bigramas
    
    for episode in results:
        # Obtener las palabras más frecuentes del episodio
        words = [word for word, _ in episode['top_words']]
        
        # Generar bigramas con estas palabras
        for i in range(len(words) - 1):
            bigram = (words[i], words[i+1])
            bigram_count[bigram] = bigram_count.get(bigram, 0) + 1
    
    # Ordena los bigramas por frecuencia descendente
    return sorted(bigram_count.items(), key=lambda x: x[1], reverse=True)

# Pestañas principales de la app
tab1, tab2, tab3 = st.tabs(["Resumen Temporada", "Evolución Léxica", "Análisis Temático"])

with tab1:
    st.header("Resumen de la Temporada")  # Encabezado de la pestaña
    
    # Métricas principales
    cols = st.columns(4)  # Divide en 4 columnas
    cols[0].metric("Total de palabras", total_words)  # Muestra total de palabras
    cols[1].metric("Palabras únicas", df['unique_words'].sum())  # Muestra palabras únicas
    cols[2].metric("Densidad léxica promedio", f"{df['lexical_density'].mean():.4f}")  # Densidad léxica promedio
    cols[3].metric("Palabra más frecuente", f"'{global_top[0][0]}' ({global_top[0][1]} veces)")  # Palabra más frecuente
    
    # Gráfico de evolución de densidad léxica
    st.subheader("Evolución de la Densidad Léxica")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['episode'], df['lexical_density'], 'o-', color='#8B0000')
    ax.set_xlabel("Episodio")
    ax.set_ylabel("Densidad Léxica")
    ax.set_title("Variación de Riqueza Lingüística por Episodio")
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    
    # Nube de palabras global
    st.subheader("Nube de Palabras de Toda la Temporada")
    wordcloud = generate_wordcloud(dict(global_top[:100]))  # Genera la nube con las 100 palabras más frecuentes
    st.image(wordcloud, use_container_width=True)  # Muestra la imagen de la nube
    
    # Temas principales
    st.subheader("Temas Principales")
    
    if main_themes:
        # Mostrar tarjetas de temas
        cols = st.columns(3)  # Divide en 3 columnas para los temas
        for i, (theme, data) in enumerate(main_themes):
            with cols[i % 3]:
                with st.expander(f"**{theme}** (Frecuencia: {data['frequency']})"):
                    st.write(f"**Palabras clave:**")
                    words = ", ".join([f"{word} ({count})" for word, count in data['top_words']])
                    st.write(words)
                    # Progreso relativo (máximo 10% del total para escalar)
                    max_freq = max([d['frequency'] for _, d in main_themes])
                    progress_value = data['frequency'] / max_freq
                    st.progress(progress_value)
        
        # Gráfico de radar para distribución de temas
        st.subheader("Distribución Relativa de Temas")
        
        themes = [t[0] for t in main_themes]
        freqs = [t[1]['frequency'] for t in main_themes]
        max_freq = max(freqs)
        normalized_freqs = [f / max_freq for f in freqs]
        
        angles = np.linspace(0, 2 * np.pi, len(themes), endpoint=False).tolist()
        angles += angles[:1]  # Cerrar el círculo
        normalized_freqs += normalized_freqs[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'polar': True})
        ax.plot(angles, normalized_freqs, 'o-', linewidth=2)
        ax.fill(angles, normalized_freqs, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(themes)
        ax.set_title("Distribución de Temas", size=14)
        ax.set_rlabel_position(30)
        st.pyplot(fig)
    else:
        st.warning("No se identificaron temas significativos")  # Mensaje si no hay temas

with tab2:
    st.header("Evolución Léxica")  # Encabezado de la pestaña
    
    # Evolución de palabras seleccionadas
    st.subheader("Evolución de Palabras Clave")
    if selected_words:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Normalizar frecuencias para mejor visualización
        max_freqs = {}
        for word in selected_words:
            freqs = [freq for _, freq in semantic_evolution[word]]
            max_freqs[word] = max(freqs) if freqs else 1
        
        for word in selected_words:
            episodes, freqs = zip(*semantic_evolution[word])
            # Normalizar por la frecuencia máxima de cada palabra
            normalized_freqs = [freq / max_freqs[word] for freq in freqs]
            ax.plot(episodes, normalized_freqs, 'o-', label=word)
        
        ax.set_xlabel("Episodio")
        ax.set_ylabel("Frecuencia Relativa")
        ax.set_title("Evolución de Palabras Clave Normalizada")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    else:
        st.warning("Selecciona palabras para analizar su evolución")
    
    # Cambio en vocabulario
    st.subheader("Cambio en el Vocabulario")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Calcular porcentaje de palabras nuevas por episodio
    all_words = set()
    novelty_percentage = []
    
    for idx, episode in enumerate(results):
        current_words = set(dict(episode['top_words']).keys())
        new_words = current_words - all_words
        novelty = len(new_words) / len(current_words) if current_words else 0
        novelty_percentage.append(novelty)
        all_words.update(current_words)
    
    ax.plot(df['episode'], novelty_percentage, 'o-', color='#4daf4a')
    ax.set_xlabel("Episodio")
    ax.set_ylabel("Porcentaje de Palabras Nuevas")
    ax.set_title("Innovación Léxica por Episodio")
    ax.grid(alpha=0.3)
    st.pyplot(fig)

with tab3:
    st.header("Análisis Temático")  # Encabezado de la pestaña
    
    # Visualización alternativa para relaciones entre palabras
    st.subheader("Distribución de Palabras Clave por Episodio")
    st.write("Top 15 palabras más frecuentes y su presencia en cada episodio")
    
    # Seleccionar las 15 palabras más frecuentes
    top_words = [word for word, _ in global_top[:15]]
    
    # Crear una tabla de presencia
    presence_data = []
    
    for episode in results:
        ep_data = {"Episodio": episode['episode']}
        episode_words = set(dict(episode['top_words']).keys())
        
        for word in top_words:
            ep_data[word] = "✅" if word in episode_words else "❌"
        
        presence_data.append(ep_data)
    
    # Convertir a DataFrame
    presence_df = pd.DataFrame(presence_data)
    
    # Mostrar tabla con estilo
    def color_presence(val):
        return 'color: green; font-weight: bold' if val == "✅" else 'color: red'
    
    styled_df = presence_df.style.applymap(color_presence, subset=top_words)
    st.dataframe(styled_df, height=800)
    
    # Análisis de bigramas
    st.subheader("Pares de Palabras Más Frecuentes")
    st.write("Estas combinaciones de palabras revelan conceptos recurrentes")
    
    bigrams = calculate_bigrams(results)[:20]  # Top 20 bigramas
    if bigrams:
        bigram_words, bigram_freqs = zip(*bigrams)
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.barh([f"{w1} + {w2}" for w1, w2 in bigram_words], bigram_freqs, color='#ff7f00')
        ax.set_xlabel("Frecuencia")
        ax.set_title("Pares de Palabras Más Comunes")
        st.pyplot(fig)
    else:
        st.warning("No se encontraron bigramas significativos")  # Mensaje si no hay bigramas