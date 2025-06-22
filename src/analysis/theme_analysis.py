from nltk.corpus import wordnet
from collections import defaultdict
import numpy as np

def identify_main_themes(global_top, threshold=0.01):
    """
    Identifica temas principales dinámicamente usando:
    - Agrupación semántica
    - Expansión de sinónimos
    - Frecuencia relativa
    """
    total_words = sum(count for _, count in global_top)
    word_freq = dict(global_top)
    
    # Temas base con palabras clave iniciales
    base_themes = {
        'Misterio': ['mystery', 'strange', 'secret', 'unknown', 'puzzle', 'weird'],
        'Peligro': ['danger', 'threat', 'monster', 'attack', 'safe', 'kill', 'death'],
        'Familia': ['family', 'son', 'daughter', 'child', 'mother', 'father', 'parent'],
        'Supervivencia': ['survive', 'food', 'water', 'shelter', 'resource', 'supply', 'hunger'],
        'Locación': ['town', 'forest', 'house', 'road', 'tree', 'building', 'place', 'location'],
        'Emociones': ['fear', 'hope', 'trust', 'angry', 'scared', 'confused', 'feel']
    }
    
    # Expansión de temas con sinónimos
    expanded_themes = defaultdict(list)
    for theme, keywords in base_themes.items():
        for keyword in keywords:
            if keyword in word_freq:
                expanded_themes[theme].append(keyword)
            # Buscar sinónimos
            for syn in wordnet.synsets(keyword):
                for lemma in syn.lemmas():
                    synonym = lemma.name().replace('_', ' ').lower()
                    if synonym in word_freq and synonym not in expanded_themes[theme]:
                        expanded_themes[theme].append(synonym)
    
    # Calcular frecuencia de temas
    theme_freq = defaultdict(int)
    theme_words = defaultdict(list)
    
    for word, count in word_freq.items():
        for theme, keywords in expanded_themes.items():
            if word in keywords:
                theme_freq[theme] += count
                theme_words[theme].append((word, count))
    
    # Filtrar temas significativos (al menos 1% del total)
    significant_themes = {}
    for theme, freq in theme_freq.items():
        if freq / total_words >= threshold:
            # Ordenar palabras del tema por frecuencia
            theme_words[theme].sort(key=lambda x: x[1], reverse=True)
            significant_themes[theme] = {
                'frequency': freq,
                'top_words': theme_words[theme][:5]  # Top 5 palabras
            }
    
    # Ordenar temas por frecuencia
    sorted_themes = sorted(significant_themes.items(), 
                          key=lambda x: x[1]['frequency'], 
                          reverse=True)
    
    return sorted_themes