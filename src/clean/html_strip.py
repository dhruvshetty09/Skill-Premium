import re

TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


def strip_html(text):
    if not text:
        return ""

    no_tags = TAG_PATTERN.sub(" ", text)
    collapsed = WHITESPACE_PATTERN.sub(" ", no_tags)
    return collapsed.strip()


if __name__ == "__main__":
    sample = "<p><strong>Role:</strong> Data Analyst</p><ul><li>SQL</li><li>Power BI</li></ul>"
    print(strip_html(sample))