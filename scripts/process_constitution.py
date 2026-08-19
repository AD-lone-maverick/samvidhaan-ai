from pathlib import Path
import json
import re

from pypdf import PdfReader


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

PDF_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "constitution_of_india_2026.pdf"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "constitution_articles.json"
)

CLEAN_OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "constitution_clean.json"
)



# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    pages = []

    for page in reader.pages:
        text = page.extract_text()

        if text:
            pages.append(text)

    return "\n".join(pages)


# --------------------------------------------------
# BASIC CLEANING
# --------------------------------------------------

def clean_text(text):
    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Fix excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Fix excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


# --------------------------------------------------
# FIND PREAMBLE
# --------------------------------------------------

def get_constitution_start(text):
    marker = "WE, THE PEOPLE OF INDIA"

    index = text.find(marker)

    if index == -1:
        raise ValueError("Could not find the Preamble.")

    return text[index:]


# --------------------------------------------------
# DETECT PARTS
# --------------------------------------------------

PART_PATTERN = re.compile(
    r"^\s*(PART\s+[IVXLCDM]+)\s*$",
    re.MULTILINE
)


def find_parts(text):
    matches = list(PART_PATTERN.finditer(text))

    parts = []

    for match in matches:
        start = match.start()
        part_number = match.group(1).strip()

        # Look at the next few lines for the Part title
        after = text[match.end():]

        lines = after.splitlines()

        title = ""

        for line in lines[:5]:
            line = line.strip()

            if line:
                title = line
                break

        parts.append({
            "part": part_number,
            "title": title,
            "position": start
        })

    return parts


# --------------------------------------------------
# ARTICLE DETECTION
# --------------------------------------------------

ARTICLE_START_PATTERN = re.compile(
    r"^\s*(?:(?:\d{1,2}\s*)?\[\s*)?(\d{1,3}[A-Z]?)\.\s+(.+)"
)


# Lines that look like numbered footnotes rather than articles
FOOTNOTE_PREFIXES = (
    "Subs.",
    "Ins.",
    "Rep.",
    "Omitted",
    "Inserted",
    "Substituted"
)


def is_footnote_line(line):
    line = line.strip()

    for prefix in FOOTNOTE_PREFIXES:
        if re.match(rf"^\d+\.\s+{re.escape(prefix)}", line):
            return True

    return False


# --------------------------------------------------
# FIND PART FOR AN ARTICLE
# --------------------------------------------------

def get_current_part(article_position, parts):

    current_part = {
        "part": None,
        "title": None
    }

    for part in parts:

        if part["position"] <= article_position:
            current_part = {
                "part": part["part"],
                "title": part["title"]
            }
        else:
            break

    return current_part

def article_sort_key(article_number):
    """
    Convert article numbers such as:
    21   -> (21, "")
    21A  -> (21, "A")
    31C  -> (31, "C")
    """
    match = re.fullmatch(r"(\d+)([A-Z]?)", article_number)

    if not match:
        return None

    number = int(match.group(1))
    suffix = match.group(2)

    return number, suffix

def normalize_article_number(raw_number, last_article_key):

    # Normal case: 33, 34, 51A, 243A, etc.
    key = article_sort_key(raw_number)

    if key is None:
        return None

    # If there is no previous article, keep the number.
    if last_article_key is None:
        return raw_number

    last_number, last_suffix = last_article_key

    number, suffix = key

    # Handle PDF footnote marker stuck to the article number.
    #
    # Example:
    # PDF text: 132A
    # Actual:   32A
    #
    # because the leading "1" is a superscript footnote marker.

    if number > last_number + 1:

        raw = raw_number

        if len(raw) >= 2:

            possible_number = raw[1:]

            possible_key = article_sort_key(
                possible_number
            )

            if possible_key is not None:

                possible_num, possible_suffix = possible_key

                if (
                    possible_num == last_number
                    and possible_suffix
                ):
                    return possible_number

    return raw_number

def clean_article_text(raw_text, article_number):

    text = raw_text.strip()

    # Remove common PDF footnote markers that appear
    # immediately before article numbers.
    text = re.sub(
        rf"^\d+\s*\[\s*{re.escape(article_number)}\.",
        f"{article_number}.",
        text
    )

    # Handle superscript footnote digits that become
    # attached to the article number during PDF extraction.
    text = re.sub(
        rf"^1{re.escape(article_number)}\.",
        f"{article_number}.",
        text
    )

    # Remove closing bracket occasionally left after
    # an amendment marker.
    text = re.sub(
        rf"^{re.escape(article_number)}\.\s*\]",
        f"{article_number}.",
        text
    )

    # Normalize excessive whitespace.
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize repeated blank lines.
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    return text.strip()

def extract_article_title(article_text):

    # Remove article number
    text = re.sub(
        r"^\d{1,3}[A-Z]?\.\s*",
        "",
        article_text
    )

    # The em dash generally separates the title
    # from the actual constitutional provision.
    if "—" in text:

        title = text.split("—", 1)[0]

    elif " - " in text:

        title = text.split(" - ", 1)[0]

    else:

        # Fallback if no separator is available.
        first_line = text.split("\n", 1)[0]
        title = first_line

    # Remove PDF brackets used around omitted provisions
    title = re.sub(r"^\[\s*", "", title)
    title = re.sub(r"\s*\]$", "", title)

    # Normalize whitespace
    title = re.sub(r"\s+", " ", title)

    return title.strip()

def detect_article_status(article_text):

    text = article_text.strip()

    # Remove article number from the beginning
    text = re.sub(
        r"^\d{1,3}[A-Z]?\.\s*",
        "",
        text
    )

    # Look only at the beginning of the article.
    # This prevents words such as "omitted" inside
    # later amendment footnotes from affecting status.
    first_500_chars = text[:500]

    if re.search(
        r"—\s*Omitted\b",
        first_500_chars,
        re.IGNORECASE
    ):
        return "omitted"

    return "active"

def structure_article(article):

    raw_text = article["raw_text"]

    cleaned_text = clean_article_text(
        raw_text,
        article["article_number"]
    )

    title = extract_article_title(
        cleaned_text
    )

    status = detect_article_status(
        cleaned_text
    )

    return {
        "article_number": article["article_number"],
        "part": article["part"],
        "part_title": article["part_title"],
        "article_title": title,
        "article_text": cleaned_text,
        "status": status,
        "source": "Constitution of India",
        "version": "2026"
    }
# --------------------------------------------------
# PARSE ARTICLES
# --------------------------------------------------

def parse_articles(text):

    parts = find_parts(text)

    lines = text.splitlines()

    articles = []

    current_position = 0
    last_article_key = None
    current_article = None

    for line in lines:

        stripped = line.strip()

        # ---------------------------------------------
        # STOP BEFORE THE SCHEDULES
        # ---------------------------------------------

        if stripped == "THE FIRST SCHEDULE":
            break

        # ---------------------------------------------
        # CHECK WHETHER THIS LINE STARTS AN ARTICLE
        # ---------------------------------------------

        match = ARTICLE_START_PATTERN.match(line)

        if match:

            raw_article_number = match.group(1)
            if raw_article_number == "132A":
                print(
                    "DEBUG:",
                    "raw =", raw_article_number,
                    "last =", last_article_key
                )

            article_number = normalize_article_number(
                raw_article_number,
                last_article_key
            )
            if raw_article_number == "132A":
                print(
                    "NORMALIZATION RESULT:",
                    raw_article_number,
                    "->",
                    article_number
                )

            key = article_sort_key(article_number)

            if key is not None:

                number, suffix = key

                valid_candidate = True

                # Article numbers should be within the
                # known constitutional article range.
                if number < 1 or number > 395:
                    valid_candidate = False

                # -----------------------------------------
                # SEQUENCE VALIDATION
                # -----------------------------------------

                if last_article_key is not None:

                    last_number, last_suffix = last_article_key

                    # Reject backward jumps caused by
                    # numbered footnotes.
                    if number < last_number:
                        valid_candidate = False

                    # Same number:
                    # allow 21 -> 21A -> 21B
                    elif number == last_number:

                        if suffix <= last_suffix:
                            valid_candidate = False

                if valid_candidate:

                    # Finish previous article
                    if current_article is not None:

                        current_article["raw_text"] = (
                            current_article["raw_text"].strip()
                        )

                        articles.append(current_article)

                    # Find metadata for this article
                    current_part = get_current_part(
                        current_position,
                        parts
                    )


                    current_article = {
                        "article_number": article_number,
                        "part": current_part["part"],
                        "part_title": current_part["title"],
                        "raw_text": line
                    }

                    last_article_key = key

                    current_position += len(line) + 1

                    continue

        # ---------------------------------------------
        # NORMAL ARTICLE CONTENT
        # ---------------------------------------------

        if current_article is not None:

            current_article["raw_text"] += "\n" + line

        current_position += len(line) + 1

    # ---------------------------------------------
    # ADD LAST ARTICLE
    # ---------------------------------------------

    if current_article is not None:

        current_article["raw_text"] = (
            current_article["raw_text"].strip()
        )

        articles.append(current_article)

    print("\nDetected article numbers:")
    print([
        article["article_number"]
        for article in articles
    ])

    return articles


# --------------------------------------------------
# SAVE JSON
# --------------------------------------------------

def save_json(data, output_path):

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=4
        )


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("Reading Constitution PDF...")

    text = extract_text_from_pdf(PDF_PATH)

    print(f"Characters extracted: {len(text):,}")

    print("Cleaning text...")

    text = clean_text(text)

    print("Finding Constitution starting point...")

    text = get_constitution_start(text)

    print("Parsing Parts and Articles...")

    articles = parse_articles(text)
    structured_articles = [
    structure_article(article)
    for article in articles
]
    print("\n" + "=" * 60)
    print("STRUCTURED ARTICLE VALIDATION")
    print("=" * 60)

    for number in ["10", "21A", "32A", "33", "243A"]:

        matches = [
            article
            for article in structured_articles
            if article["article_number"] == number
        ]

        print(f"\n--- ARTICLE {number} ---")

        if matches:

            article = matches[0]

            print("Title:", article["article_title"])
            print("Status:", article["status"])
            print("Text:")
            print(article["article_text"][:500])

        else:

            print("NOT FOUND")
    dataset = {
        "source": "Constitution of India",
        "version": "2026",
        "language": "English",
        "articles": structured_articles
    }

    save_json(
        dataset,
        OUTPUT_PATH
    )
    save_json(
    dataset,
    CLEAN_OUTPUT_PATH
    )

    print()
    print("=" * 60)
    print("PROCESSING COMPLETE")
    print("=" * 60)

    print(f"Output: {OUTPUT_PATH}")
    print(f"Articles: {len(articles)}")


if __name__ == "__main__":
    main()