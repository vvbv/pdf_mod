from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
import pdf2image
import pytesseract

# =====================================================
# CONFIGURACIÓN: Aquí defines qué escribir por código CUM
# =====================================================
# La clave es el código CUM (tal como aparece en el PDF)
# El valor es el código de cliente a escribir en esa fila
codigos_por_cum = {
    "45906-13": "MD123456",
    "20034621-2": "MD789012",
    "20057384-4": "MD555555",
    "19931778-24": "MD345678"
}

print("🔍 Buscando códigos CUM en el PDF...")

# Convertir PDF a imagen para OCR
images = pdf2image.convert_from_path("doc.pdf", dpi=300)
image = images[0]

# Realizar OCR para obtener las posiciones del texto
ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, lang='spa')

# Buscar las posiciones de los códigos CUM
cum_encontrados = {}
for i, text in enumerate(ocr_data['text']):
    text_limpio = text.strip()
    # Buscar si este texto coincide con algún CUM que buscamos
    for cum_buscado, codigo_cliente in codigos_por_cum.items():
        # Comparar sin espacios y guiones para mayor flexibilidad
        cum_sin_guion = cum_buscado.replace('-', '')
        texto_sin_guion = text_limpio.replace('-', '').replace(' ', '')
        
        if cum_sin_guion in texto_sin_guion or text_limpio == cum_buscado:
            x = ocr_data['left'][i]
            y = ocr_data['top'][i]
            cum_encontrados[cum_buscado] = {
                'x': x,
                'y': y,
                'codigo': codigo_cliente
            }
            print(f"✓ Encontrado CUM '{cum_buscado}' en posición: ({x}, {y})")
            break

if not cum_encontrados:
    print("⚠️  No se encontraron códigos CUM. Intentando búsqueda más flexible...")
    # Búsqueda alternativa: buscar solo la parte numérica
    for i, text in enumerate(ocr_data['text']):
        if text.strip() and any(char.isdigit() for char in text):
            for cum_buscado, codigo_cliente in codigos_por_cum.items():
                # Buscar coincidencia parcial
                if cum_buscado in text or text in cum_buscado:
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    if cum_buscado not in cum_encontrados:
                        cum_encontrados[cum_buscado] = {
                            'x': x,
                            'y': y,
                            'codigo': codigo_cliente
                        }
                        print(f"✓ Encontrado CUM '{cum_buscado}' (parcial: '{text}') en: ({x}, {y})")

# Convertir coordenadas de imagen (píxeles) a coordenadas PDF (puntos)
dpi = 300
page_height_pt = 792  # Letter size en puntos

def pixel_to_pdf_coords(x_px, y_px):
    x_pt = (x_px / dpi) * 72
    y_pt = page_height_pt - ((y_px / dpi) * 72)
    return x_pt, y_pt

# Crear una capa con los textos
packet = BytesIO()
can = canvas.Canvas(packet, pagesize=letter)
can.setFont("Helvetica", 8)

print(f"\n📝 Escribiendo {len(cum_encontrados)} códigos de cliente...")

# Escribir cada código en la posición del CUM correspondiente
for cum, info in cum_encontrados.items():
    # Convertir coordenadas de píxeles a puntos PDF
    # La columna "Código Cliente" está a la izquierda del CUM
    # Ajustamos: -60px a la izquierda (300/5) y +20px hacia abajo
    x_pdf, y_pdf = pixel_to_pdf_coords(info['x'] + 290, info['y'] + 30)
    
    codigo = info['codigo']
    
    # Calcular ancho del rectángulo según el texto
    texto_ancho = can.stringWidth(codigo, "Helvetica", 8)
    rect_ancho = texto_ancho + 10
    rect_alto = 13
    
    # Dibujar fondo blanco con borde negro
    can.setFillColorRGB(1, 1, 1)
    can.setStrokeColorRGB(0, 0, 0)
    can.setLineWidth(0.5)
    can.rect(x_pdf - 2, y_pdf - 2, rect_ancho, rect_alto, fill=1, stroke=1)
    
    # Escribir el texto
    can.setFillColorRGB(0, 0, 0)
    can.drawString(x_pdf + 3, y_pdf + 1, codigo)
    
    print(f"  ✓ CUM '{cum}' → Código '{codigo}' en ({x_pdf:.1f}, {y_pdf:.1f})")

can.save()

packet.seek(0)

# Combinar la capa con el PDF original
text_layer = PdfReader(packet)
existing_pdf = PdfReader(open("doc.pdf", "rb"))
output = PdfWriter()

page = existing_pdf.pages[0]
page.merge_page(text_layer.pages[0])
output.add_page(page)

with open("tabla_completada.pdf", "wb") as f:
    output.write(f)

print("✅ Listo. Se creó 'tabla_completada.pdf'")
