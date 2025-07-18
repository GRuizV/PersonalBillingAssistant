import pdfplumber

doc_path = r"C:\Users\USUARIO\OneDrive\Nima Cloud\02 Desarrollo de Producto\PBA\POCs\Extraccion de Data\Pruebas\Test PDFs\AvVillas\Visa\AV - VS - 02 - FEB-2025.pdf"

with pdfplumber.open(doc_path) as pdf:

    first_page = pdf.pages[0]
    text = first_page.extract_text()
    print(text)