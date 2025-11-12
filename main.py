from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

# Crear una capa con los textos
packet = BytesIO()
can = canvas.Canvas(packet, pagesize=letter)

# Escribir los textos donde falten (x, y)
# Puedes ajustar las coordenadas a ojo
can.setFont("Helvetica", 10)
can.drawString(120, 600, "Sin dato")
can.drawString(300, 580, "N/A")
can.drawString(450, 560, "Falta info")
can.save()

packet.seek(0)

# Combinar la capa con el PDF original
text_layer = PdfReader(packet)
existing_pdf = PdfReader(open("tabla_escaneada.pdf", "rb"))
output = PdfWriter()

page = existing_pdf.pages[0]
page.merge_page(text_layer.pages[0])
output.add_page(page)

with open("tabla_completada.pdf", "wb") as f:
    output.write(f)

print("✅ Listo. Se creó 'tabla_completada.pdf'")
