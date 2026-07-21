import os
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

SITE_NAME = "adzuna"
BASE_URL = "https://api.adzuna.com/v1/api/jobs/in/search"
OUT_FILE = Path("data/raw/adzuna_postings.jsonl")
DELAY_SECONDS = 2

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def search_page(page_number, query="data analyst", results_per_page=50):
    url = f"{BASE_URL}/{page_number}"
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": query,
        "content-type": "application/json",
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        print(f"adzuna request failed on page {page_number}: {e}")
        return None


def normalize(posting):
    company = posting.get("company") or {}
    location = posting.get("location") or {}
    return {
        "source": SITE_NAME,
        "job_url": posting.get("redirect_url"),
        "title": posting.get("title"),
        "company": company.get("display_name"),
        "city": location.get("area", [None])[-1] if location.get("area") else None,
        "salary": posting.get("salary_max") or posting.get("salary_min"),
        "experience": None,
        "description": posting.get("description"),
        "scraped_at": datetime.utcnow().isoformat(),
    }


def already_scraped_urls():
    urls = set()
    if not OUT_FILE.exists():
        return urls
    with open(OUT_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    urls.add(json.loads(line)["job_url"])
                except (json.JSONDecodeError, KeyError):
                    pass
    return urls


def run(max_pages=20):
    if not APP_ID or not APP_KEY:
        print("missing ADZUNA_APP_ID / ADZUNA_APP_KEY in .env")
        return

    done_urls = already_scraped_urls()
    print(f"resuming, {len(done_urls)} postings already saved")

    for page in range(1, max_pages + 1):
        data = search_page(page)
        if not data or "results" not in data:
            print(f"page {page} came back empty, stopping")
            break

        results = data["results"]
        if not results:
            print("no more results")
            break

        print(f"page {page}: {len(results)} postings")

        for raw in results:
            job = normalize(raw)
            if not job["job_url"] or job["job_url"] in done_urls:
                continue

            with open(OUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(job) + "\n")

            done_urls.add(job["job_url"])
            print(f"  saved: {job['title']}")

        time.sleep(DELAY_SECONDS)

    print(f"\ndone. total from adzuna: {len(done_urls)}")


if __name__ == "__main__":
    run()