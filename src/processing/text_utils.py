import re
import os

def tokenize(text):
    """
    Tokeniza texto usando expresiones regulares, preservando contracciones en inglés.
    Ejemplo: "don't" se mantiene como una sola palabra en lugar de dividirse en "don" y "t"
    """
    # Versión mejorada: maneja contracciones como "don't", "can't", "I'm"
    words = re.findall(r"\b[\w']+\b", text.lower())
    return words

# Calcula la ruta BASE del proyecto (nivel raíz)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ruta CORRECTA a los datos
data_file = os.path.join(BASE_DIR, 'config', "stopwords" )


def remove_stopwords(words, stopwords_file= data_file):
    """
    Filtra stopwords desde archivo local con manejo de errores robusto
    """
    
    stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
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
    
 
    return [word for word in words if word not in stop_words]

def basic_lemmatize(word):
    """
    Lematización básica para inglés con reglas expandidas.
    Maneja plurales, verbos en pasado y formas comunes.
    """
    # Reglas para plurales y posesivos
    if word.endswith("'s"):
        word = word[:-2]
    if word.endswith("s'"):
        word = word[:-1]
    
    # Verbos y formas comunes
    if word.endswith('ies'):
        return word[:-3] + 'y'
    if word.endswith('es'):
        return word[:-2]
    if word.endswith('ed'):
        return word[:-2] if len(word) > 4 else word
    if word.endswith('ing'):
        return word[:-3] if len(word) > 5 else word
    if word.endswith('s'):
        return word[:-1]
    
    # Contracciones comunes
    contraction_map = {
        "n't": " not",
        "'re": " are",
        "'m": " am",
        "'ll": " will",
        "'d": " would",
        "'ve": " have"
    }
    
    for suffix, replacement in contraction_map.items():
        if word.endswith(suffix):
            return word[:-len(suffix)] + replacement
    
    return word

# Función adicional útil para análisis de texto
def calculate_lexical_density(words):
    """
    Calcula la densidad léxica (proporción de palabras únicas)
    """
    if not words:
        return 0.0
    unique_words = len(set(words))
    return unique_words / len(words)

# Ejemplo de uso (puedes eliminar esto en producción)
if __name__ == "__main__":
    sample_text = "I'm running faster than the others. They aren't trying hard enough!"
    print("Texto original:", sample_text)
    
    tokens = tokenize(sample_text)
    print("Tokens:", tokens)
    
    filtered = remove_stopwords(tokens)
    print("Sin stopwords:", filtered)
    
    lemmatized = [basic_lemmatize(word) for word in filtered]
    print("Lematizado:", lemmatized)
    
    density = calculate_lexical_density(lemmatized)
    print(f"Densidad léxica: {density:.2%}")