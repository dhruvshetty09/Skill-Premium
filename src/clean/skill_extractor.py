import re
import csv
from pathlib import Path


def load_skill_map(csv_path="config/skill_dictionary.csv"):
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"can't find {csv_path}")

    skill_map = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row or not row[0]:
                continue
            canonical = row[0].strip()
            aliases = [a.strip() for a in row[1:] if a.strip()]
            for alias in aliases:
                skill_map[alias.lower()] = canonical
            skill_map[canonical.lower()] = canonical

    return skill_map


def extract_skills(description, skill_map):
    if not description:
        return set()

    text = str(description).lower()
    found = set()

    for alias, canonical in skill_map.items():
        pattern = r"\b" + re.escape(alias) + r"\b"
        if re.search(pattern, text):
            found.add(canonical)

    return found


if __name__ == "__main__":
    skill_map = load_skill_map()
    print(f"loaded {len(skill_map)} aliases mapping to skills")

    sample_desc = (
        "Looking for a Data Analyst with strong SQL and Python skills. "
        "Experience with Power BI, Excel, and PySpark is a must. AWS knowledge is a plus."
    )
    found = extract_skills(sample_desc, skill_map)
    print("found skills:", found)