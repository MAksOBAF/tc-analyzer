from fpdf import FPDF

def export_to_pdf(text, path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=10)
    clean = text.encode('ascii', 'ignore').decode('ascii')
    for line in clean.split('\n'):
        pdf.cell(0, 8, txt=line, ln=True)
    pdf.output(path)
