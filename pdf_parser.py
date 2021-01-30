from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

def read_pdf(file):
    parsed_pages = []
    output_string = StringIO()
    resource_manager = PDFResourceManager()
    device = TextConverter(resource_manager, output_string, laparams=LAParams())
    interpreter = PDFPageInterpreter(resource_manager, device)
    for page in PDFPage.get_pages(file):
        interpreter.process_page(page)
        parsed_pages.append(output_string.getvalue())
        output_string.truncate(0)
        output_string.seek(0)
    return parsed_pages
