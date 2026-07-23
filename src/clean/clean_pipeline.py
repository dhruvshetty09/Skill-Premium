import json
import pandas as pd
from pathlib import Path

from src.clean.salary_parser import parse_salary, parse_lakh_salary, parse_experience
from src.clean.skill_extractor import load_skill_map, extract_skills
from src.clean.dedupe import flag_duplicates
from src.clean.html_strip import strip_html

RAW_FILES = [
    "data/raw/timesjobs_postings.jsonl",
    "data/raw/foundit_postings.jsonl",
    "data/raw/adzuna_postings.jsonl",
]
OUT_FILE = Path("data/interim/cleaned_postings.parquet")

def load_raw_jsonl(paths):
    rows=[]
    for path in paths:
        p=Path(path)
        if not p.exists():
            print(f"skipping {path}, file doesn't exist")
            continue
        with open(p, encoding="utf-8") as f:
            for line in f:
                line= line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows

def resolve_salary(row):
    raw_salary= row.get("salary")
    source=row.get("source")

    if source =="timesjobs" and raw_salary and "lac" in str(raw_salary).lower():
        return parse_lakh_salary(raw_salary)
    return parse_salary(raw_salary)

def clean_all():
    rows= load_raw_jsonl(RAW_FILES)
    print(f"loaded {len(rows)} raw postings across all sources")

    skill_map=load_skill_map()

    for row in rows:
        row["description"]= strip_html(row.get("description"))

        salary= resolve_salary(row)
        row["salary_min_inr"]= salary["min"]
        row["salary_max_inr"]= salary["max"]
        row["salary_mid_inr"]= salary["mid"]
        row["has_salary_disclosed"]= salary["mid"] is not None
        row["salary"] = str(row.get("salary")) if row.get("salary") is not None else None

        exp_min, exp_max= parse_experience(row.get("experience"))
        row["exp_min_years"]=exp_min
        row["exp_max_years"]=exp_max

        skills_found= extract_skills(row.get("description"),skill_map)
        row["skills"]= sorted(skills_found)

    print("dedup pass...")
    rows= flag_duplicates(rows, threshold=85)
    before= len(rows)
    rows= [r for r in rows if not r.get("is_duplicate")]
    print(f"removed {before - len(rows)} duplicates, {len(rows)} unqiue postings remain")

    df= pd.DataFrame(rows)

    print("\n---data quality snapshot---")
    print(f"total rows: {len(df)}")
    print(f"by source:\n{df['source'].value_counts()}")
    print(f"salary disclosed: {df['has_salary_disclosed'].sum()} ({df['has_salary_disclosed'].mean()*100:.1f}%)")
    print(f"rows with at least 1 skill found: {(df['skills'].apply(len)>0).sum()}")
    print(f"rows missing city{df['city'].isna().sum()}")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(OUT_FILE, index=False)
    print(f"\nsaved cleaned data to {OUT_FILE}")

    return df

if __name__ =="__main__":
    clean_all()