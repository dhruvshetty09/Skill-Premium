import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

CLEANED_FILE = "data/interim/cleaned_postings.parquet"


def get_or_create_company(conn, name):
    if name is None or pd.isna(name):
        name = "Unknown"
    canonical = str(name).strip().lower()

    result = conn.execute(
        text("SELECT company_id FROM dim_company WHERE company_name_canonical = :c"),
        {"c": canonical}
    ).fetchone()
    if result:
        return result[0]

    result = conn.execute(
        text("""INSERT INTO dim_company (company_name, company_name_canonical)
                 VALUES (:name, :canonical) RETURNING company_id"""),
        {"name": str(name), "canonical": canonical}
    ).fetchone()
    return result[0]


def get_or_create_city(conn, city_name):
    if city_name is None or pd.isna(city_name) or not str(city_name).strip():
        return None

    city_name = str(city_name).strip()

    result = conn.execute(
        text("SELECT city_id FROM dim_city WHERE city_name = :c"),
        {"c": city_name}
    ).fetchone()
    if result:
        return result[0]

    result = conn.execute(
        text("INSERT INTO dim_city (city_name, tier) VALUES (:c, NULL) RETURNING city_id"),
        {"c": city_name}
    ).fetchone()
    return result[0]


def get_or_create_role(conn, title):
    if title is None or pd.isna(title):
        title = ""
    title_lower = str(title).lower()

    if "senior" in title_lower or "sr." in title_lower or "sr " in title_lower or "lead" in title_lower:
        seniority = "Senior"
    elif "fresher" in title_lower or "entry" in title_lower or "junior" in title_lower or "intern" in title_lower or "trainee" in title_lower:
        seniority = "Entry-Level"
    else:
        seniority = "Mid-Level"

    if "data analyst" in title_lower or "data analysis" in title_lower:
        canonical = "data_analyst"
    elif "machine learning" in title_lower or "ml engineer" in title_lower:
        canonical = "ml_engineer"
    elif "data engineer" in title_lower:
        canonical = "data_engineer"
    elif "business analyst" in title_lower:
        canonical = "business_analyst"
    else:
        canonical = "other"

    result = conn.execute(
        text("""SELECT role_id FROM dim_role
                 WHERE role_canonical = :canonical AND seniority_level = :seniority"""),
        {"canonical": canonical, "seniority": seniority}
    ).fetchone()
    if result:
        return result[0]

    result = conn.execute(
        text("""INSERT INTO dim_role (role_name, role_canonical, seniority_level)
                 VALUES (:role_name, :canonical, :seniority) RETURNING role_id"""),
        {"role_name": str(title), "canonical": canonical, "seniority": seniority}
    ).fetchone()
    return result[0]


def get_or_create_skill(conn, skill_name):
    result = conn.execute(
        text("SELECT skill_id FROM dim_skill WHERE skill_name = :s"),
        {"s": skill_name}
    ).fetchone()
    if result:
        return result[0]

    result = conn.execute(
        text("INSERT INTO dim_skill (skill_name) VALUES (:s) RETURNING skill_id"),
        {"s": skill_name}
    ).fetchone()
    return result[0]


def to_none_if_nan(value):
    if pd.isna(value):
        return None
    return value


def load():
    engine = create_engine(DB_URL)
    df = pd.read_parquet(CLEANED_FILE)
    print(f"loading {len(df)} rows into postgres...")

    inserted = 0
    skipped = 0

    with engine.begin() as conn:
        for _, row in df.iterrows():
            job_url = row.get("job_url")

            existing = conn.execute(
                text("SELECT posting_id FROM fact_postings WHERE job_url = :u"),
                {"u": job_url}
            ).fetchone()
            if existing:
                skipped += 1
                continue

            company_id = get_or_create_company(conn, row.get("company"))
            city_id = get_or_create_city(conn, row.get("city"))
            role_id = get_or_create_role(conn, row.get("title"))

            result = conn.execute(
                text("""
                    INSERT INTO fact_postings
                        (company_id, city_id, role_id, job_title, job_description,
                         job_url, source_site, salary_min_inr, salary_max_inr,
                         salary_mid_inr, has_salary_disclosed, exp_min_years,
                         exp_max_years, scraped_at)
                    VALUES
                        (:company_id, :city_id, :role_id, :title, :description,
                         :job_url, :source, :sal_min, :sal_max, :sal_mid,
                         :has_salary, :exp_min, :exp_max, :scraped_at)
                    RETURNING posting_id
                """),
                {
                    "company_id": company_id,
                    "city_id": city_id,
                    "role_id": role_id,
                    "title": row.get("title"),
                    "description": row.get("description"),
                    "job_url": job_url,
                    "source": row.get("source"),
                    "sal_min": to_none_if_nan(row.get("salary_min_inr")),
                    "sal_max": to_none_if_nan(row.get("salary_max_inr")),
                    "sal_mid": to_none_if_nan(row.get("salary_mid_inr")),
                    "has_salary": bool(row.get("has_salary_disclosed")),
                    "exp_min": to_none_if_nan(row.get("exp_min_years")),
                    "exp_max": to_none_if_nan(row.get("exp_max_years")),
                    "scraped_at": row.get("scraped_at"),
                }
            )
            posting_id = result.fetchone()[0]

            skills = row.get("skills")
            if skills is not None and len(skills) > 0:
                for skill_name in skills:
                    skill_id = get_or_create_skill(conn, skill_name)
                    conn.execute(
                        text("""INSERT INTO bridge_posting_skills (posting_id, skill_id)
                                 VALUES (:p, :s) ON CONFLICT DO NOTHING"""),
                        {"p": posting_id, "s": skill_id}
                    )

            inserted += 1

    print(f"done. inserted {inserted} new postings, skipped {skipped} already-loaded ones")


if __name__ == "__main__":
    load()