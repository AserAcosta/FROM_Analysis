from PIL import Image, ImageDraw, ImageFont
import random
import math
import re
import logging

# Configurar logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def generate_wordcloud(word_freq, width=800, height=600, background_color=(255, 255, 255)):
    """
    Genera una nube de palabras mejorada con:
    - Filtrado de números y palabras cortas
    - Algoritmo de colocación mejorado
    - Manejo de errores robusto
    """
    try:
        # Filtrar palabras no deseadas (números y palabras cortas)
        filtered_freq = {
            word: freq for word, freq in word_freq.items() 
            if not re.match(r'^\d+$', word) and len(word) > 2
        }
        
        if not filtered_freq:
            logger.warning("No valid words for word cloud after filtering")
            return None
        
        # Crear imagen con fondo sólido
        img = Image.new('RGB', (width, height), background_color)
        draw = ImageDraw.Draw(img)
        
        # Función para obtener tamaño de texto
        def get_text_size(text, font):
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                return bbox[2] - bbox[0], bbox[3] - bbox[1]
            except Exception as e:
                logger.error(f"Error getting text size: {str(e)}")
                return (100, 40)  # Tamaño por defecto
        
        # Fuentes escalables
        fonts = []
        try:
            # Intentar cargar varias fuentes comunes
            for size in range(20, 71, 5):
                try:
                    fonts.append(ImageFont.truetype("arial.ttf", size))
                except:
                    try:
                        fonts.append(ImageFont.truetype("DejaVuSans.ttf", size))
                    except:
                        fonts.append(ImageFont.truetype("LiberationSans-Regular.ttf", size))
        except:
            fonts = [ImageFont.load_default()]
        
        # Paleta de colores mejorada (accesible)
        colors = [
            (0, 82, 147),    # Azul oscuro
            (213, 0, 50),     # Rojo
            (0, 132, 61),     # Verde
            (126, 49, 141),   # Púrpura
            (243, 119, 53),   # Naranja
            (0, 155, 166),    # Turquesa
            (165, 42, 42),    # Marrón
        ]
        
        # Calcular frecuencias
        freqs = list(filtered_freq.values())
        min_freq = min(freqs) if freqs else 1
        max_freq = max(freqs) if freqs else 1
        freq_range = max(1, max_freq - min_freq)
        
        # Posiciones y tamaños
        positions = []
        center_x, center_y = width // 2, height // 2
        max_radius = min(width, height) // 3
        
        # Ordenar palabras por frecuencia
        sorted_words = sorted(filtered_freq.items(), key=lambda x: x[1], reverse=True)
        
        # Espiral para colocación
        spiral_step = 0.05
        spiral_radius = 0
        
        for word, freq in sorted_words:
            # Tamaño proporcional a la frecuencia
            size_ratio = (freq - min_freq) / freq_range
            font_idx = min(int(len(fonts) * size_ratio), len(fonts) - 1)
            font = fonts[font_idx]
            
            # Obtener tamaño del texto
            text_width, text_height = get_text_size(word, font)
            
            # Intentar colocar la palabra
            placed = False
            attempts = 0
            
            while not placed and attempts < 100:
                attempts += 1
                
                # Usar espiral para colocación
                angle = spiral_step * attempts
                spiral_radius = min(spiral_radius + 0.3, max_radius)
                
                x = center_x + int(spiral_radius * math.cos(angle)) - text_width // 2
                y = center_y + int(spiral_radius * math.sin(angle)) - text_height // 2
                
                # Verificar límites
                if x < 10 or y < 10 or x + text_width > width - 10 or y + text_height > height - 10:
                    continue
                
                # Verificar colisiones
                collision = False
                new_box = (x-5, y-5, x + text_width + 5, y + text_height + 5)
                
                for existing_box in positions:
                    if (new_box[0] < existing_box[2] and 
                        new_box[2] > existing_box[0] and 
                        new_box[1] < existing_box[3] and 
                        new_box[3] > existing_box[1]):
                        collision = True
                        break
                
                if not collision:
                    # Seleccionar color
                    color = colors[len(positions) % len(colors)]
                    
                    # Dibujar texto
                    draw.text((x, y), word, fill=color, font=font)
                    positions.append(new_box)
                    placed = True
        
        if not placed:
            logger.warning(f"Could not place word: {word}")
        
        return img
    
    except Exception as e:
        logger.error(f"Error generating word cloud: {str(e)}")
        # Crear imagen de error
        img = Image.new('RGB', (width, height), (240, 240, 240))
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
            draw.text((50, height//2), "Error generating word cloud", fill=(255, 0, 0), font=font)
        except:
            pass
        return img