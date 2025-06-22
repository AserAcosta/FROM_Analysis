import os
from utils.srt_parser import parse_srt
from utils.text_utils import tokenize, remove_stopwords, basic_lemmatize

def process_episodes(data_folder):
    results = []
    global_word_count = {}
    
    for filename in os.listdir(data_folder):
        if filename.endswith('.srt'):
            episode = filename.split('_')[1].split('.')[0]
            filepath = os.path.join(data_folder, filename)
            
            subtitles = parse_srt(filepath)
            full_text = ' '.join([sub['text'] for sub in subtitles])
            
            # Procesamiento de texto
            words = tokenize(full_text)
            filtered_words = remove_stopwords(words)
            lemmatized_words = [basic_lemmatize(word) for word in filtered_words]
            
            # Cálculo de métricas
            total_words = len(lemmatized_words)
            unique_words = len(set(lemmatized_words))
            lexical_density = unique_words / total_words if total_words > 0 else 0
            
            # Conteo de palabras
            word_count = {}
            for word in lemmatized_words:
                word_count[word] = word_count.get(word, 0) + 1
                global_word_count[word] = global_word_count.get(word, 0) + 1
            
            # Top 10 palabras
            top_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)[:10]
            
            results.append({
                'episode': episode,
                'total_words': total_words,
                'unique_words': unique_words,
                'lexical_density': lexical_density,
                'top_words': top_words
            })
    
    # Top 50 global
    global_top = sorted(global_word_count.items(), key=lambda x: x[1], reverse=True)[:50]
    
    return results, global_top