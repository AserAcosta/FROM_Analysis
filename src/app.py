import streamlit as st
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from analysis.lexical_analysis import process_episodes
from visualization.wordcloud_generator import generate_wordcloud
from collections import defaultdict
import seaborn as sns
import logging


import nltk
from nltk import data

# Forzar descarga de recursos si faltan
resources = [
    ('punkt', 'tokenizers/punkt'),
    ('wordnet', 'corpora/wordnet'),
    ('stopwords', 'corpora/stopwords'),
    ('averaged_perceptron_tagger', 'taggers/averaged_perceptron_tagger'),
    ('omw-1.4', 'corpora/omw-1.4')
]

for res_name, res_path in resources:
    try:
        data.find(res_path)
    except LookupError:
        nltk.download(res_name, quiet=True)

        

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Configuración de la página
st.set_page_config(layout="wide", page_title="ANÁLISIS LÉXICO: 'FROM'")
st.title("ANÁLISIS LÉXICO: 'FROM' - EVOLUCIÓN TEMPORADA 3")

# Cargar datos
@st.cache_resource
def load_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_folder = os.path.join(BASE_DIR, 'data')
    return process_episodes(data_folder)

try:
    results, global_top, semantic_evolution, main_themes = load_data()
    df = pd.DataFrame(results)
    total_words = df['total_words'].sum()
except Exception as e:
    st.error(f"Error cargando datos: {str(e)}")
    st.stop()

# Sidebar
st.sidebar.header("Opciones de Análisis")
selected_words = st.sidebar.multiselect(
    "Seleccionar palabras para seguimiento",
    options=list(semantic_evolution.keys()),
    default=list(semantic_evolution.keys())[:5]
)

# Funciones auxiliares
def analyze_correlations(semantic_evolution, selected_words):
    """Calcula correlaciones entre palabras seleccionadas"""
    corr_data = defaultdict(dict)
    
    for word in selected_words:
        for ep, freq in semantic_evolution[word]:
            corr_data[ep][word] = freq
    
    corr_df = pd.DataFrame.from_dict(corr_data, orient='index').fillna(0)
    return corr_df.corr()

def calculate_bigrams(results):
    """Calcula bigramas más frecuentes"""
    bigram_count = defaultdict(int)
    
    for episode in results:
        words = [word for word, _ in episode['top_words']]
        for i in range(len(words) - 1):
            bigram = (words[i], words[i+1])
            bigram_count[bigram] += 1
    
    return sorted(bigram_count.items(), key=lambda x: x[1], reverse=True)

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["Resumen Temporada", "Evolución Léxica", "Análisis Temático"])

with tab1:
    st.header("Resumen de la Temporada")
    
    # Métricas principales
    cols = st.columns(4)
    cols[0].metric("Total de palabras", total_words)
    cols[1].metric("Palabras únicas", df['unique_words'].sum())
    cols[2].metric("Densidad léxica promedio", f"{df['lexical_density'].mean():.4f}")
    
    top_word, top_count = global_top[0]
    top_percent = (top_count / total_words) * 100
    cols[3].metric("Palabra más frecuente", 
                  f"'{top_word}' ({top_count})",
                  f"{top_percent:.2f}% del total")
    
    # Gráfico de densidad léxica
    st.subheader("Evolución de la Densidad Léxica")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df, x='episode', y='lexical_density', 
                color='#8B0000', marker='o', linewidth=2.5, ax=ax)
    ax.set(xlabel="Episodio", ylabel="Densidad Léxica", 
          title="Variación de Riqueza Lingüística por Episodio")
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    
    # Nube de palabras
    st.subheader("Nube de Palabras de Toda la Temporada")
    wordcloud = generate_wordcloud(dict(global_top[:100]))
    if wordcloud:
        st.image(wordcloud, use_container_width=True)  # CAMBIO AQUÍ
    else:
        st.warning("No se pudo generar la nube de palabras")
    
    # Temas principales
    st.subheader("Temas Principales")
    
    if main_themes:
        cols = st.columns(min(3, len(main_themes)))
        for i, (theme, data) in enumerate(main_themes):
            with cols[i % 3]:
                with st.expander(f"**{theme}** (Frecuencia: {data['frequency']})"):
                    st.write("**Palabras clave:**")
                    for word, count in data['top_words']:
                        st.write(f"- {word} ({count})")
                    
                    max_freq = max(d['frequency'] for _, d in main_themes)
                    progress = data['frequency'] / max_freq
                    st.progress(progress)
                    st.caption(f"Frecuencia relativa: {progress:.1%}")
        
        # Gráfico de radar
        st.subheader("Distribución Relativa de Temas")
        themes = [t[0] for t in main_themes]
        freqs = [t[1]['frequency'] for t in main_themes]
        max_freq = max(freqs)
        normalized = [f / max_freq for f in freqs] + [freqs[0] / max_freq]
        
        angles = np.linspace(0, 2 * np.pi, len(themes), endpoint=False).tolist()
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'polar': True})
        ax.plot(angles, normalized, 'o-', linewidth=2, color='#1f77b4')
        ax.fill(angles, normalized, alpha=0.25, color='#1f77b4')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(themes, fontsize=10)
        ax.set_title("Distribución de Temas", size=14)
        ax.set_rgrids([0.2, 0.4, 0.6, 0.8], fontsize=8)
        st.pyplot(fig)
    else:
        st.warning("No se identificaron temas significativos")

with tab2:
    st.header("Evolución Léxica")
    
    # Evolución de palabras clave
    st.subheader("Evolución de Palabras Clave")
    if selected_words:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        for word in selected_words:
            episodes = []
            freqs = []
            for ep, count in semantic_evolution[word]:
                ep_data = next(x for x in results if x['episode'] == ep)
                rel_freq = count / ep_data['total_words'] if ep_data['total_words'] > 0 else 0
                episodes.append(ep)
                freqs.append(rel_freq)
            
            ax.plot(episodes, freqs, 'o-', label=word, linewidth=2)
        
        ax.set(xlabel="Episodio", ylabel="Frecuencia Relativa",
              title="Evolución de Palabras Clave")
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(alpha=0.3)
        st.pyplot(fig)
        
        # Correlaciones
        st.subheader("Correlaciones entre Palabras")
        if len(selected_words) > 1:
            corr_matrix = analyze_correlations(semantic_evolution, selected_words)
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f", ax=ax)
            ax.set_title("Correlación de Uso entre Palabras")
            st.pyplot(fig)
        else:
            st.info("Selecciona al menos 2 palabras para ver correlaciones")
    else:
        st.warning("Selecciona palabras para analizar su evolución")
    
    # Novedad léxica
    st.subheader("Cambio en el Vocabulario")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    all_words = set()
    novelty = []
    for episode in results:
        current_words = set(word for word, _ in episode['top_words'])
        new_words = current_words - all_words
        novelty.append(len(new_words) / len(current_words) if current_words else 0)
        all_words.update(current_words)
    
    novelty_df = pd.DataFrame({
        'Episodio': df['episode'],
        'Novedad Léxica': novelty
    })
    
    sns.lineplot(data=novelty_df, x='Episodio', y='Novedad Léxica', 
                color='#4daf4a', marker='o', linewidth=2.5, ax=ax)
    ax.set(xlabel="Episodio", ylabel="Porcentaje de Palabras Nuevas",
          title="Innovación Léxica por Episodio")
    ax.grid(alpha=0.3)
    st.pyplot(fig)

with tab3:
    st.header("Análisis Temático")
    
    # Heatmap de presencia
    st.subheader("Distribución de Palabras Clave por Episodio")
    top_words = [word for word, _ in global_top[:15]]
    
    heatmap_data = []
    episodes = []
    for ep in results:
        ep_words = set(word for word, _ in ep['top_words'])
        heatmap_data.append([1 if word in ep_words else 0 for word in top_words])
        episodes.append(f"Ep {ep['episode']}")
    
    heatmap_df = pd.DataFrame(heatmap_data, index=episodes, columns=top_words)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.heatmap(heatmap_df.T, annot=False, cmap="YlGnBu", cbar_kws={'label': 'Presencia'}, ax=ax)
    ax.set(xlabel="Episodio", ylabel="Palabra", title="Presencia de Palabras Clave")
    st.pyplot(fig)
    
    # Bigramas
    st.subheader("Pares de Palabras Más Frecuentes")
    bigrams = calculate_bigrams(results)[:20]
    
    if bigrams:
        bigram_df = pd.DataFrame(bigrams, columns=['Bigrama', 'Frecuencia'])
        bigram_df['Palabras'] = bigram_df['Bigrama'].apply(lambda x: f"{x[0]} + {x[1]}")
        
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(data=bigram_df, y='Palabras', x='Frecuencia', 
            hue='Palabras', palette="viridis", ax=ax, legend=False, dodge=False)
        ax.set(xlabel="Frecuencia", title="Pares de Palabras Más Comunes")
        st.pyplot(fig)
    else:
        st.warning("No se encontraron bigramas significativos")