import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")


def run_checks():
    engine = create_engine(DB_URL)
    failures = []

    with engine.connect() as conn:
        bad_salary = conn.execute(text(
            "SELECT COUNT(*) FROM fact_postings WHERE salary_min_inr < 0 OR salary_max_inr < 0"
        )).scalar()
        if bad_salary > 0:
            failures.append(f"found {bad_salary} rows with negative salary")

        dupe_urls = conn.execute(text(
            "SELECT job_url, COUNT(*) c FROM fact_postings GROUP BY job_url HAVING COUNT(*) > 1"
        )).fetchall()
        if dupe_urls:
            failures.append(f"found {len(dupe_urls)} duplicate job_url values")

        orphans = conn.execute(text("""
            SELECT COUNT(*) FROM bridge_posting_skills bps
            LEFT JOIN fact_postings fp ON bps.posting_id = fp.posting_id
            WHERE fp.posting_id IS NULL
        """)).scalar()
        if orphans > 0:
            failures.append(f"found {orphans} orphaned rows in bridge_posting_skills")

        total = conn.execute(text("SELECT COUNT(*) FROM fact_postings")).scalar()
        with_skills = conn.execute(text(
            "SELECT COUNT(DISTINCT posting_id) FROM bridge_posting_skills"
        )).scalar()
        coverage_pct = (with_skills / total * 100) if total else 0
        if coverage_pct < 50:
            failures.append(f"skill coverage only {coverage_pct:.1f}% (expected 50%+)")

        null_city = conn.execute(text(
            "SELECT COUNT(*) FROM fact_postings WHERE city_id IS NULL"
        )).scalar()
        null_city_pct = (null_city / total * 100) if total else 0
        if null_city_pct > 20:
            failures.append(f"{null_city_pct:.1f}% of postings missing city (expected under 20%)")

        bad_range = conn.execute(text(
            "SELECT COUNT(*) FROM fact_postings WHERE salary_min_inr > salary_max_inr"
        )).scalar()
        if bad_range > 0:
            failures.append(f"found {bad_range} rows where salary_min > salary_max")

    print(f"total postings in db: {total}")
    print(f"skill coverage: {coverage_pct:.1f}%")
    print(f"missing city: {null_city_pct:.1f}%")

    if failures:
        print("\nFAILED checks:")
        for f in failures:
            print(f"  - {f}")
        return False
    else:
        print("\nall checks passed")
        return True


if __name__ == "__main__":
    ok = run_checks()
    exit(0 if ok else 1)