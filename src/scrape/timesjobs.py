import time
import json
import requests
from pathlib import Path
from datetime import datetime

SITE_NAME = "timesjobs"
API_URL = "https://tjapi.timesjobs.com/search/api/v1/search/jobs/list"
OUT_FILE = Path("data/raw/timesjobs_postings.jsonl")
DELAY_SECONDS = 4
PAGE_SIZE = 25

OUT_FILE.parent.mkdir(parents=True, exist_ok=True)


def new_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer":"https://www.timesjobs.com/",
        "Origin":"https://www.timesjobs.com/",
    })
    return s


def fetch_page(session, page, query="data analyst"):
    jsonbody = {
        "keyword": f'"{query}"',
        "location": "",
        "experience": "",
        "page": str(page),
        "size": str(PAGE_SIZE),
        "company": "",
        "functionAreaId": "",
        "industry": "",
        "jobFunction": "",
        "jobFunctions": [],
    }
    try:
        resp = session.post(API_URL, json=jsonbody, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
        print(f"request failed on page {page} -> {e}")
        return None


def build_salary_string(job):
    low = job.get("lowSalary", -1)
    high = job.get("highSalary", -1)
    if low == -1 and high == -1:
        return None
    return f"{low}-{high}"


def build_experience_string(job):
    frm = job.get("experienceFrom")
    to = job.get("experienceTo")
    if frm is None and to is None:
        return None
    return f"{frm}-{to} years"


def normalize(job):
    description = job.get("description") or ""
    skills = job.get("skills") or ""
    full_description = f"{description} {skills}".strip()

    return {
        "source": SITE_NAME,
        "job_url": job.get("jobDetailUrl"),
        "title": job.get("title"),
        "company": job.get("company"),
        "city": job.get("location"),
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


def run(max_pages=40):
    session = new_session()
    done_urls = already_scraped_urls()
    print(f"resuming, {len(done_urls)} jobs already saved")

    for page in range(1, max_pages + 1):
        data = fetch_page(session, page)

        if not data or "jobs" not in data:
            print(f"page {page} came back empty, stopping")
            break

        jobs = data["jobs"]
        if not jobs:
            print("no more jobs, stopping")
            break

        total_pages = data.get("totalPages")
        print(f"page {page} / {total_pages}: {len(jobs)} jobs")

        for raw in jobs:
            job = normalize(raw)
            if not job["job_url"] or job["job_url"] in done_urls:
                continue

            with open(OUT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(job) + "\n")

            done_urls.add(job["job_url"])
            print(f"  saved: {job['title']}")

        time.sleep(DELAY_SECONDS)

        if total_pages and page >= total_pages:
            print("reached last page")
            break

    print(f"\ndone. total from timesjobs: {len(done_urls)}")


if __name__ == "__main__":
    run()