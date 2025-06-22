import re
import chardet

def parse_srt(file_path):
    """
    Parsea archivos SRT sin detección de personajes
    """
    # Detectar encoding
    with open(file_path, 'rb') as f:
        rawdata = f.read()
    encoding = chardet.detect(rawdata)['encoding'] or 'utf-8'
    
    # Leer contenido
    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
        content = f.read()

    # Patrón regex
    pattern = re.compile(
        r'(\d+)\s*\n'  # Número de subtítulo
        r'(\d{2}:\d{2}:\d{2},\d{3})'  # Inicio
        r'\s*-->\s*'  # Separador
        r'(\d{2}:\d{2}:\d{2},\d{3})\s*\n'  # Fin
        r'([\s\S]*?)(?=\n\n|\Z)',  # Texto
        re.MULTILINE
    )
    
    subtitles = []
    
    for match in pattern.finditer(content):
        sub_id = int(match.group(1))
        start = match.group(2)
        end = match.group(3)
        text = match.group(4).strip()
        
        # Limpiar texto
        text = re.sub(r'<[^>]+>', '', text)  # HTML tags
        text = re.sub(r'\{\\an?\d\}', '', text)  # Marcadores
        text = re.sub(r'\s+', ' ', text).strip()  # Espacios
        
        # Calcular duración
        def time_to_seconds(t):
            h, m, s = t.split(':')
            s = s.replace(',', '.')
            return int(h)*3600 + int(m)*60 + float(s)
        
        start_sec = time_to_seconds(start)
        end_sec = time_to_seconds(end)
        duration = round(end_sec - start_sec, 3)
        
        subtitles.append({
            'id': sub_id,
            'start': start,
            'end': end,
            'text': text,
            'duration': duration
        })
    
    return subtitles