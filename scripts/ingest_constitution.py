from pathlib import Path
from pypdf import PdfReader


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PDF_PATH = PROJECT_ROOT / "data" / "raw" / "constitution_of_india_2026.pdf"


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    print(f"Total pages: {len(reader.pages)}")

    all_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text()

        if text:
            all_text.append(text)

        print(f"Processed page {page_number}/{len(reader.pages)}")

    return "\n".join(all_text)


if __name__ == "__main__":
    text = extract_text_from_pdf(PDF_PATH)

    print("=" * 60)
    print("TOTAL CHARACTERS")
    print("=" * 60)
    print(len(text))

    keyword = "WE, THE PEOPLE OF INDIA"

    start = 0
    occurrence = 1

    while True:
        index = text.find(keyword, start)

        if index == -1:
            break

        print("\n" + "=" * 60)
        print(f"OCCURRENCE {occurrence}")
        print("=" * 60)

        print(text[index:index + 3000])

        start = index + len(keyword)
        occurrence += 1