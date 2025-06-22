import re
import os
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
import nltk

# Descargar recursos necesarios
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

lemmatizer = WordNetLemmatizer()

def tokenize(text):
    words = re.findall(r"\b[\w']+\b", text.lower())
    return words

def remove_stopwords(words, stopwords_file=None):
    """
    Filtra stopwords desde archivo local con manejo de errores robusto
    """
    stop_words = set()
    default_stopwords = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
                         "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 
                         'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 
                         'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
                         'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 
                         'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 
                         'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 
                         'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
                         'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
                         'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 
                         'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 
                         'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 
                         'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', "don't", 'should', 
                         "should've", 'now', 'd', 'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 
                         'couldn', "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', 
                         "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', 
                         "mustn't", 'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', 
                         "wasn't", 'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"}
    
    # Determinar la ruta correcta para el archivo de stopwords
    if stopwords_file is None:
        # Obtener la ruta del directorio actual del script
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Construir la ruta al archivo de stopwords
        stopwords_file = os.path.join(current_dir, '..', 'config', 'stopwords', 'english.txt')
    
    try:
        if os.path.exists(stopwords_file):
            with open(stopwords_file, 'r', encoding='utf-8') as f:
                stop_words = set(f.read().splitlines())
        else:
            print(f"Advertencia: Archivo {stopwords_file} no encontrado. Usando stopwords por defecto.")
            stop_words = default_stopwords
    except Exception as e:
        print(f"Error cargando stopwords: {e}. Usando set por defecto")
        stop_words = default_stopwords
    
    return [word for word in words if word not in stop_words]

def advanced_lemmatize(word):
    """
    Lematización avanzada usando WordNet
    """
    pos_tags = [wordnet.NOUN, wordnet.VERB, wordnet.ADJ, wordnet.ADV]
    
    for tag in pos_tags:
        lemma = lemmatizer.lemmatize(word, tag)
        if lemma != word:
            return lemma
    return word

def calculate_lexical_density(words):
    """
    Calcula la densidad léxica (proporción de palabras únicas)
    """
    if not words:
        return 0.0
    unique_words = len(set(words))
    return unique_words / len(words)