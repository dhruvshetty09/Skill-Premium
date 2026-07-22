import time
import json
import requests
from pathlib import Path
from datetime import datetime

SITE_NAME = "foundit"
API_URL = "https://www.foundit.in/home/api/searchResultsPage"
OUT_FILE = Path("data/raw/foundit_postings.jsonl")
DELAY_SECONDS = 4
PAGE_SIZE = 20


def new_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.foundit.in/",
        "Origin": "https://www.foundit.in",
    })
    return s


def fetch_page(session, start, query="data analyst"):
    params = {
        "start": start,
        "limit": PAGE_SIZE,
        "query": query,
        "queryDerived": "true",
        "countries": "India",
        "variantName": "DEFAULT",
    }
    try:
        resp = session.get(API_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"request failed at start={start} -> {e}")
        return None


def build_salary_string(job):
    low = (job.get("minimumSalary") or {}).get("absoluteValue", 0)
    high = (job.get("maximumSalary") or {}).get("absoluteValue", 0)
    if not low and not high:
        return None
    return f"{low}-{high}"


def build_experience_string(job):
    frm = (job.get("minimumExperience") or {}).get("years")
    to = (job.get("maximumExperience") or {}).get("years")
    if frm is None and to is None:
        return None
    return f"{frm}-{to} years"


def build_city_string(job):
    locations = job.get("locations") or []
    for loc in locations:
        if loc.get("city"):
            return loc["city"]
    return None


def normalize(job):
    description = job.get("description") or ""
    it_skills = [s.get("text", "") for s in (job.get("itSkills") or [])]
    skills = [s.get("text", "") for s in (job.get("skills") or [])]
    all_skills = ", ".join([s for s in it_skills + skills if s])
    full_description = f"{description} {all_skills}".strip()

    job_url = job.get("redirectUrl")
    if not job_url and job.get("jdUrl"):
        job_url = "https://www.foundit.in" + job["jdUrl"]

    return {
        "source": SITE_NAME,
        "job_url": job_url,
        "title": job.get("title"),
        "company": (job.get("company") or {}).get("name"),
        "city": build_city_string(job),
        "salary": build_salary_string(job),
        "experience": build_experience_string(job),
        "description": full_description,
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


def run(max_batches=40):
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    session = new_session()
    done_urls = already_scraped_urls()
    print(f"resuming, {len(done_urls)} jobs already saved")

    for batch in range(max_batches):
        start = batch * PAGE_SIZE
        data = fetch_page(session, start)

        if not data or "data" not in data:
            print(f"nothing came back at start={start}, stopping")
            break

        jobs = data["data"]
        if not jobs:
            print("empty batch, reached the end")
            break

        total = (data.get("meta") or {}).get("paging", {}).get("total")
        print(f"start={start} / total={total}: {len(jobs)} jobs")

        for raw_job in jobs:
            job = normalize(raw_job)
            if not job["job_url"] or job["job_url"] in done_urls:
                continue

            with open(OUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(job) + "\n")

            done_urls.add(job["job_url"])
            print(f"  saved: {job['title']}")

        time.sleep(DELAY_SECONDS)

    print(f"\ndone. total from foundit: {len(done_urls)}")


if __name__ == "__main__":
    run()