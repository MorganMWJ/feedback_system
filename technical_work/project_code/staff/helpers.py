from PyPDF2 import PdfFileReader

def get_pdf_pages(f):
    info = {"title": None, "author": None, "pageCount": None}
    pdf = PdfFileReader(f)
    allInfo = pdf.getDocumentInfo()
    info["title"] = allInfo.title
    info["author"] = allInfo.author
    info["pageCount"] = pdf.getNumPages()
    return info["pageCount"]
