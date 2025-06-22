import os
from collections import defaultdict
from processing.srt_parser import parse_srt
from processing.text_utils import tokenize, remove_stopwords, advanced_lemmatize
from analysis.theme_analysis import identify_main_themes

def process_episodes(data_folder):
    results = []
    global_word_count = defaultdict(int)
    episode_word_counts = []
    semantic_evolution = {}
    
    for filename in sorted(os.listdir(data_folder)):
        if filename.startswith('episode_') and filename.endswith('.srt'):
            episode = filename.split('_')[1].split('.')[0]
            filepath = os.path.join(data_folder, filename)
            
            subtitles = parse_srt(filepath)
            full_text = ' '.join([sub['text'] for sub in subtitles])
            
            # Procesamiento de texto
            words = tokenize(full_text)
            filtered_words = remove_stopwords(words)
            lemmatized_words = [advanced_lemmatize(word) for word in filtered_words]
            
            # Métricas del episodio
            total_words = len(lemmatized_words)
            unique_words = len(set(lemmatized_words))
            lexical_density = unique_words / total_words if total_words > 0 else 0
            
            # Conteo de palabras
            word_count = {}
            for word in lemmatized_words:
                word_count[word] = word_count.get(word, 0) + 1
                global_word_count[word] += 1
            
            # Top palabras del episodio
            top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:15]
            
            # Guardar conteo para análisis de evolución
            episode_word_counts.append((episode, word_count))
            
            results.append({
                'episode': episode,
                'total_words': total_words,
                'unique_words': unique_words,
                'lexical_density': lexical_density,
                'top_words': top_words
            })
    
    # Análisis de evolución semántica
    all_words = set(global_word_count.keys())
    semantic_evolution = analyze_semantic_evolution(episode_word_counts, all_words)
    
    # Top 100 global
    global_top = sorted(global_word_count.items(), key=lambda x: x[1], reverse=True)[:100]
    
    # Temas principales (usando la nueva función mejorada)
    main_themes = identify_main_themes(global_top)
    
    return results, global_top, semantic_evolution, main_themes

def analyze_semantic_evolution(episode_word_counts, vocabulary):
    """
    Analiza la evolución del uso de palabras clave a lo largo de los episodios
    """
    evolution = {}
    
    # Seleccionar palabras clave (las 50 más frecuentes globalmente)
    top_words = sorted(vocabulary, key=lambda w: sum(count for _, wc in episode_word_counts for count in [wc.get(w, 0)]), reverse=True)[:50]
    
    for word in top_words:
        word_evolution = []
        for episode, word_count in episode_word_counts:
            frequency = word_count.get(word, 0)
            word_evolution.append((episode, frequency))
        evolution[word] = word_evolution
    
    return evolution