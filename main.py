from pdf_to_json import PdfToJson

def main():
    pdf_json = PdfToJson("engineering", "2020", "spring")
    pdf_json.save_json()

if __name__ == "__main__":
    main()
