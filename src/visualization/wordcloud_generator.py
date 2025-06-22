from PIL import Image, ImageDraw, ImageFont
import random
import math

def generate_wordcloud(word_freq, width=800, height=600, background_color=(255, 255, 255)):
    """
    Genera una nube de palabras sin transparencia
    """
    # Crear imagen con fondo sólido
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)
    
    # Función para obtener tamaño de texto
    def get_text_size(text, font):
        try:
            # Método moderno (Pillow >=8.0.0)
            bbox = draw.textbbox((0, 0), text, font=font)
            return bbox[2] - bbox[0], bbox[3] - bbox[1]
        except AttributeError:
            # Método antiguo (Pillow <8.0.0)
            return draw.textsize(text, font=font)
    
    # Fuente base
    try:
        font_path = "arial.ttf"
        base_font = ImageFont.truetype(font_path, 20)
    except:
        base_font = ImageFont.load_default()
    
    # Paleta de colores vibrantes (RGB)
    colors = [
        (228, 26, 28),    # Rojo
        (55, 126, 184),   # Azul
        (77, 175, 74),    # Verde
        (152, 78, 163),   # Púrpura
        (255, 127, 0),    # Naranja
        (166, 86, 40),    # Marrón
        (247, 129, 191),  # Rosa
    ]
    
    # Calcular frecuencias mínima y máxima
    freqs = list(word_freq.values())
    min_freq = min(freqs) if freqs else 1
    max_freq = max(freqs) if freqs else 1
    freq_range = max(1, max_freq - min_freq)  # Evitar división por cero
    
    # Posiciones y tamaños
    positions = []
    center_x, center_y = width // 2, height // 2
    max_radius = min(width, height) // 3
    
    # Ordenar palabras por frecuencia (más frecuentes primero)
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    for word, freq in sorted_words:
        # Tamaño proporcional a la frecuencia
        size_ratio = (freq - min_freq) / freq_range
        font_size = int(20 + 50 * size_ratio)  # Rango 20-70px
        
        try:
            font = ImageFont.truetype(font_path, font_size)
        except:
            font = base_font
        
        # Obtener tamaño del texto
        text_width, text_height = get_text_size(word, font)
        
        # Intentar colocar la palabra
        placed = False
        for _ in range(100):  # 100 intentos por palabra
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0.1, 0.8) * max_radius
            
            x = center_x + int(distance * math.cos(angle)) - text_width // 2
            y = center_y + int(distance * math.sin(angle)) - text_height // 2
            
            # Verificar límites
            if x < 10 or y < 10 or x + text_width > width - 10 or y + text_height > height - 10:
                continue
            
            # Verificar colisiones
            collision = False
            for (x0, y0, w0, h0) in positions:
                if (x < x0 + w0 + 5 and x + text_width + 5 > x0 and
                    y < y0 + h0 + 5 and y + text_height + 5 > y0):
                    collision = True
                    break
            
            if not collision:
                # Seleccionar color
                color = random.choice(colors)
                # Dibujar texto
                draw.text((x, y), word, fill=color, font=font)
                positions.append((x, y, text_width, text_height))
                placed = True
                break
    
    return img