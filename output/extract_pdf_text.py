import pdfplumber

with pdfplumber.open('uploads/HD Dekko 3-7.pdf') as pdf, open('output/pdf_text.txt', 'w', encoding='utf-8') as f:
    for page in pdf.pages:
        text = page.extract_text() or ''
        f.write(text + '\n') 