from nltk.corpus import wordnet
from collections import defaultdict
import logging

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def identify_main_themes(global_top, threshold=0.01):
    """Identifica temas principales usando agrupación semántica"""
    total_words = sum(count for _, count in global_top)
    word_freq = dict(global_top)
    
    # Temas base con palabras clave iniciales
    base_themes = {
        'Mystery': ['mystery', 'strange', 'secret', 'unknown', 'puzzle'],
        'Danger': ['danger', 'threat', 'monster', 'attack', 'death'],
        'Family': ['family', 'son', 'daughter', 'parent', 'home'],
        'Survival': ['survive', 'food', 'water', 'shelter', 'resource'],
        'Location': ['town', 'forest', 'house', 'road', 'building'],
        'Emotions': ['fear', 'hope', 'trust', 'angry', 'scared'],
        'Supernatural': ['ghost', 'spirit', 'supernatural', 'paranormal', 'haunted'],
        'Suspense': ['suspense', 'tension', 'anxiety', 'anticipation', 'uncertainty']
    }
    
    # Expansión de temas con sinónimos
    expanded_themes = defaultdict(list)
    for theme, keywords in base_themes.items():
        for keyword in keywords:
            # Añadir palabra base si existe
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
    
    # Filtrar temas significativos
    significant_themes = {}
    for theme, freq in theme_freq.items():
        if freq / total_words >= threshold:
            # Ordenar palabras del tema
            theme_words[theme].sort(key=lambda x: x[1], reverse=True)
            significant_themes[theme] = {
                'frequency': freq,
                'top_words': theme_words[theme][:5]  # Top 5 palabras
            }
    
    # Ordenar temas por frecuencia
    return sorted(significant_themes.items(), key=lambda x: x[1]['frequency'], reverse=True)