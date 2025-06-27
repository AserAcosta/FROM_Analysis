import re
import os
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from functools import lru_cache
import logging

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def download_nltk_resources():
    resources = {
        'punkt': 'tokenizers/punkt',
        'wordnet': 'corpora/wordnet',
        'stopwords': 'corpora/stopwords',
        'averaged_perceptron_tagger': 'taggers/averaged_perceptron_tagger',
        'omw-1.4': 'corpora/omw-1.4'
    }
    
    for resource, path in resources.items():
        try:
            nltk.data.find(path)
        except LookupError:
            nltk.download(resource, quiet=True)

# Llama a la función al inicio
download_nltk_resources()

lemmatizer = WordNetLemmatizer()
stopwords = set(nltk.corpus.stopwords.words('english'))

# Cargar stopwords adicionales
def load_custom_stopwords():
    """Carga stopwords personalizadas"""
    custom_stopwords = set()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    stopwords_file = os.path.join(script_dir, "stopwords.txt")
    
    if os.path.exists(stopwords_file):
        try:
            with open(stopwords_file, 'r', encoding='utf-8') as f:
                custom_stopwords = set(line.strip() for line in f if line.strip())
        except Exception as e:
            logger.error(f"Error loading stopwords: {str(e)}")
    
    # Añadir palabras específicas de series
    tv_stopwords = {'im', 'dont', 'youre', 'hes', 'shes', 'thats', 'whats', 'theres', 'ill', 'ive', 'theyre', 'wanna', 'gonna', 'gotta'}
    return stopwords.union(custom_stopwords).union(tv_stopwords)

# Precarga en memoria
STOP_WORDS = load_custom_stopwords()
logger.info(f"Loaded {len(STOP_WORDS)} stopwords")

# Regex precompiladas - SOLO PALABRAS ALFABÉTICAS
WORD_PATTERN = re.compile(r"\b[a-zA-Z']{3,}\b")  # Palabras de 3+ letras (con apóstrofes)

# Mapeo POS mejorado
def get_wordnet_pos(treebank_tag):
    """Obtiene POS tag simplificado para lematización"""
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # Por defecto sustantivo

# Lematización con caché y POS tagging
@lru_cache(maxsize=10000)
def cached_lemmatize(word, pos=wordnet.NOUN):
    """Lematización con POS tagging"""
    # Excluir palabras numéricas
    if word.isdigit():
        return None
    
    try:
        lemma = lemmatizer.lemmatize(word.lower(), pos)
        # Asegurar que el lema sea alfabético
        if lemma.isalpha():
            return lemma
        return None
    except:
        return None

# Tokenización y lematización mejorada
def tokenize_and_lemmatize(text):
    """Procesamiento de texto con POS tagging y filtrado numérico"""
    # Tokenización segura
    try:
        tokens = nltk.word_tokenize(text)
        pos_tags = nltk.pos_tag(tokens)
    except Exception as e:
        logger.error(f"Tokenization error: {str(e)}")
        # Fallback: tokenización simple
        tokens = re.findall(r"\b[a-zA-Z']{3,}\b", text)
        pos_tags = [(token, '') for token in tokens]
    
    lemmatized = []
    for word, tag in pos_tags:
        word_lower = word.lower()
        
        # Filtros clave: stopwords, palabras cortas, números, no alfabéticas
        if (word_lower in STOP_WORDS or 
            len(word) < 3 or 
            word.isdigit() or 
            not word.isalpha() or 
            not WORD_PATTERN.match(word_lower)):
            continue
        
        # Lematizar con POS específico
        wn_pos = get_wordnet_pos(tag)
        lemma = cached_lemmatize(word_lower, wn_pos)
        
        # Filtrar lemas no válidos (None o no alfabéticos)
        if lemma and lemma.isalpha() and len(lemma) > 2:
            lemmatized.append(lemma)
    
    return lemmatized

# Función para procesar archivos .srt
def process_srt_file(file_path):
    """Procesa un archivo .srt y devuelve estadísticas"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Extraer textos de subtítulos
        full_text = ' '.join(re.findall(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}\n([^\n]+)', content))
        
        if not full_text:
            return {
                'file': os.path.basename(file_path),
                'total_words': 0,
                'unique_words': 0,
                'lexical_density': 0.0,
                'content': ""
            }
        
        # Procesamiento de texto
        processed_words = tokenize_and_lemmatize(full_text)
        unique_count = len(set(processed_words))
        total_count = len(processed_words)
        
        return {
            'file': os.path.basename(file_path),
            'total_words': total_count,
            'unique_words': unique_count,
            'lexical_density': unique_count / total_count if total_count else 0.0,
            'content': ' '.join(processed_words)
        }
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return {
            'file': os.path.basename(file_path),
            'total_words': 0,
            'unique_words': 0,
            'lexical_density': 0.0,
            'content': ""
        }

# Procesamiento por lotes
def process_srt_directory(directory):
    """Procesa todos los archivos .srt en un directorio"""
    results = []
    for filename in os.listdir(directory):
        if filename.lower().endswith('.srt'):
            file_path = os.path.join(directory, filename)
            results.append(process_srt_file(file_path))
    
    # Generar reporte
    logger.info(f"Processed {len(results)} files")
    return results