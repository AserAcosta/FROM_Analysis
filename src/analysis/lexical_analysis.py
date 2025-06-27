import os
from collections import defaultdict
from processing.srt_parser import parse_srt
from processing.text_utils import tokenize_and_lemmatize
from analysis.theme_analysis import identify_main_themes
import logging

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def process_episodes(data_folder):
    results = []
    global_word_count = defaultdict(int)
    episode_word_counts = []
    
    # Procesar cada episodio
    for filename in sorted(os.listdir(data_folder)):
        if filename.startswith('episode_') and filename.endswith('.srt'):
            episode_num = filename.split('_')[1].split('.')[0]
            filepath = os.path.join(data_folder, filename)
            
            logger.info(f"Processing episode {episode_num}")
            subtitles = parse_srt(filepath)
            full_text = ' '.join(sub['text'] for sub in subtitles)
            
            # Procesamiento de texto
            lemmatized_words = tokenize_and_lemmatize(full_text)
            
            # Filtrar palabras no válidas (números, etc.)
            lemmatized_words = [word for word in lemmatized_words if word is not None]
            
            # Métricas del episodio
            total_words = len(lemmatized_words)
            unique_words = len(set(lemmatized_words))
            lexical_density = unique_words / total_words if total_words > 0 else 0
            
            # Conteo de palabras
            word_count = defaultdict(int)
            for word in lemmatized_words:
                word_count[word] += 1
                global_word_count[word] += 1
            
            # Top palabras del episodio
            top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:15]
            episode_word_counts.append((episode_num, word_count))
            
            results.append({
                'episode': episode_num,
                'total_words': total_words,
                'unique_words': unique_words,
                'lexical_density': lexical_density,
                'top_words': top_words
            })
    
    # Análisis de evolución semántica
    semantic_evolution = analyze_semantic_evolution(episode_word_counts)
    
    # Top 100 global
    global_top = sorted(global_word_count.items(), key=lambda x: x[1], reverse=True)[:100]
    
    # Temas principales
    main_themes = identify_main_themes(global_top)
    
    logger.info(f"Processed {len(results)} episodes")
    return results, global_top, semantic_evolution, main_themes

def analyze_semantic_evolution(episode_word_counts):
    """Analiza la evolución del uso de palabras clave"""
    evolution = {}
    
    # Seleccionar palabras clave (las 50 más frecuentes globalmente)
    global_count = defaultdict(int)
    for _, word_count in episode_word_counts:
        for word, count in word_count.items():
            global_count[word] += count
    
    top_words = sorted(global_count.items(), key=lambda x: x[1], reverse=True)[:50]
    
    for word, _ in top_words:
        word_evolution = []
        for episode, word_count in episode_word_counts:
            frequency = word_count.get(word, 0)
            word_evolution.append((episode, frequency))
        evolution[word] = word_evolution
    
    return evolution