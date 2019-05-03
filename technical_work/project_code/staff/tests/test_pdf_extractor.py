from django.test import TestCase
from staff.pdf_extractor import get_pdf_pages
from django.core.files import File
from PyPDF2.utils import PdfReadError

class TestGetPDFPages(TestCase):
    def test_get_pdf_pages_of_correct_file(self):
         page_count = 49
         f = open('assets/test_lecture.pdf', 'rb')
         pages_extarcted = get_pdf_pages(File(f))
         self.assertEqual(pages_extarcted, page_count)

    def test_get_pdf_pages_of_incorrect_file(self):
        try:
            f = open('assets/incorrect_file_example.txt', 'rb')
            pages_extarcted = get_pdf_pages(File(f))
            self.fail("Should only work with PDFs")
        except PdfReadError:
            pass

    def test_get_pdf_pages_incorrect_param_type(self):
        try:
            pages_extarcted = get_pdf_pages('Not a file object')
            self.fail("Only should except django.core.files.File objects")
        except TypeError:
            pass
