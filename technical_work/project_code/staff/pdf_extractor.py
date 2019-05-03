from PyPDF2 import PdfFileReader
from django.core.files import File
from django.db.models.fields.files import FieldFile

def get_pdf_pages(f):
    if type(f) not in [File, FieldFile]:
        raise TypeError
    info = {"title": None, "author": None, "pageCount": None}
    pdf = PdfFileReader(f)
    allInfo = pdf.getDocumentInfo()
    info["title"] = allInfo.title
    info["author"] = allInfo.author
    info["pageCount"] = pdf.getNumPages()
    return info["pageCount"]
