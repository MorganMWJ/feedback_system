from PyPDF2 import PdfFileReader
 
 
def get_info(path):
    info = {"title": None, "author": None, "pageCount": None}
    with open(path, 'rb') as f:
        pdf = PdfFileReader(f)
        allInfo = pdf.getDocumentInfo()
        info["title"] = allInfo.title
        info["author"] = allInfo.author
        info["pageCount"] = pdf.getNumPages()
    return info   
 

relPath = "test_lecture.pdf"
info = get_info(relPath)
for key,val in info.items():
    print(str(key) + "=>" + str(val))
