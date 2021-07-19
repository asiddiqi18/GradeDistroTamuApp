from pdf_parser import *


# PdfParser.clean()
pdf_json = PdfParser("academic success center", 2019, 'summer', store_pdfs=True)

try:
    json_file = pdf_json.save_json()
    if (json_file.stat().st_size < 100):
        print("Json size is less than 100 bytes.")
except requests.exceptions.HTTPError:
    print("HTTP error: Could not locate PDF for this entry.")