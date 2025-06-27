import re
import chardet
import logging
from datetime import timedelta
from typing import List, Dict
import os

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def time_to_seconds(time_str: str) -> float:
    """Convierte tiempo en formato HH:MM:SS,mmm a segundos"""
    try:
        parts = time_str.replace(',', ':').split(':')
        if len(parts) == 4:  # HH:MM:SS:mmm
            h, m, s, ms = map(int, parts)
            return h*3600 + m*60 + s + ms/1000.0
        elif len(parts) == 3:  # HH:MM:SS
            return int(parts[0])*3600 + int(parts[1])*60 + float(parts[2])
        else:
            raise ValueError(f"Formato de tiempo no reconocido: {time_str}")
    except (ValueError, TypeError) as e:
        logger.error(f"Error parsing time string '{time_str}': {str(e)}")
        return 0.0

def parse_srt(file_path: str, min_duration: float = 0.1) -> List[Dict]:
    """Parsea archivos SRT con detección de encoding y limpieza avanzada"""
    # Detectar encoding
    encoding = 'utf-8'
    try:
        with open(file_path, 'rb') as f:
            rawdata = f.read(10000)
            encoding_info = chardet.detect(rawdata)
            if encoding_info['confidence'] > 0.7:
                encoding = encoding_info['encoding']
    except Exception as e:
        logger.error(f"Error detecting encoding: {str(e)}")
    
    # Leer contenido
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}")
        return []
    
    # Patrón regex mejorado
    pattern = re.compile(
        r'(\d+)\s*\n'  # ID
        r'(\d{1,2}:\d{2}:\d{2}[,.:]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}:\d{2}[,.:]\d{1,3})\s*\n'  # Tiempos
        r'((?:.+[\r\n]+)*.+)'  # Texto (puede tener múltiples líneas)
    )
    
    subtitles = []
    errors = 0
    
    for match in pattern.finditer(content):
        try:
            sub_id = int(match.group(1))
            start = match.group(2).replace('.', ',')
            end = match.group(3).replace('.', ',')
            text = match.group(4).strip()
            
            # Calcular duración
            start_sec = time_to_seconds(start)
            end_sec = time_to_seconds(end)
            duration = end_sec - start_sec
            
            # Filtrar subtítulos muy cortos
            if duration < min_duration:
                continue
            
            # Limpieza avanzada de texto
            text = re.sub(r'<[^>]+>', '', text)  # HTML tags
            text = re.sub(r'\{[^}]+\}', '', text)  # Marcadores
            text = re.sub(r'\s+', ' ', text).strip()  # Espacios
            
            # Eliminar números (nuevo filtro)
            text = re.sub(r'\b\d+\b', '', text)  # Elimina números sueltos
            
            # Calcular palabras por minuto
            word_count = len(text.split())
            wpm = int((word_count / duration) * 60) if duration > 0 else 0
            
            subtitles.append({
                'id': sub_id,
                'start': start,
                'end': end,
                'text': text,
                'duration': round(duration, 3),
                'start_sec': start_sec,
                'end_sec': end_sec,
                'word_count': word_count,
                'wpm': wpm
            })
        except Exception as e:
            errors += 1
            logger.warning(f"Error parsing subtitle: {str(e)}")
    
    logger.info(f"Parsed {len(subtitles)} subtitles with {errors} errors")
    return subtitles

def format_timestamp(seconds: float) -> str:
    """Formatea segundos a formato SRT (HH:MM:SS,mmm)"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{milliseconds:03d}"

def save_srt(subtitles: List[Dict], output_path: str):
    """Guarda subtítulos en formato SRT"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, sub in enumerate(subtitles, 1):
                start_str = format_timestamp(sub.get('start_sec', 0))
                end_str = format_timestamp(sub.get('end_sec', 0))
                f.write(f"{i}\n{start_str} --> {end_str}\n{sub['text']}\n\n")
        logger.info(f"Saved {len(subtitles)} subtitles")
    except Exception as e:
        logger.error(f"Error saving SRT: {str(e)}")