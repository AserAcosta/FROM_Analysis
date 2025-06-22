from PIL import Image, ImageDraw, ImageFont
import random
import numpy as np

def generate_wordcloud(word_freq, width=800, height=400, background='black'):
    img = Image.new('RGB', (width, height), background)
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 15)
    except:
        font = ImageFont.load_default()
    
    # Ordenar palabras por frecuencia (mayor primero)
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    positions = []
    for word, freq in sorted_words:
        # Tamaño de fuente proporcional a la frecuencia
        font_size = int(15 + 40 * (freq / max(word_freq.values())))
        
        # Buscar posición que no colisione
        placed = False
        attempts = 0
        while not placed and attempts < 50:
            x = random.randint(0, width - 150)
            y = random.randint(0, height - 30)
            
            # Verificar colisiones
            collision = False
            for (x0, y0, w, h) in positions:
                if (x < x0 + w and x + font_size*len(word) > x0 and
                    y < y0 + h and y + font_size > y0):
                    collision = True
                    break
            
            if not collision:
                # Color con variación (tonalidades rojas)
                color = (random.randint(150, 255), 
                         random.randint(0, 100), 
                         random.randint(0, 100))
                
                draw.text((x, y), word, fill=color, font=font)
                positions.append((x, y, font_size*len(word), font_size))
                placed = True
                
            attempts += 1
    
    return img