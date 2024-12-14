# Write the code for web scrap


from PyPDF2 import PdfReader

def load_pdf(file_path):
    try:
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            if len(reader.pages) == 0:
                raise Exception("PDF is empty.")
            text = ''
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error reading PDF: {e}")

# Example usage
file_path = "pdf_people/Usama Fayyad.pdf"
text = load_pdf(file_path)
if text:
    print(text)
