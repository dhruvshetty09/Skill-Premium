# SkillPremium

Quantifying salary premiums by skill in India's tech job market. Scrapes live job postings from TimesJobs and Adzuna, cleans and loads them into a PostgreSQL warehouse, and analyzes which skills actually move the needle on pay.

## Stack
Python · PostgreSQL · SQL · pandas · statsmodels · Excel · Power BI

## Setup

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

psql -U postgres -c "CREATE DATABASE skillpremium;"
psql -U postgres -d skillpremium -f sql\01_schema.sql
```

Create `.env`:
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/skillpremium
ADZUNA_APP_ID=your_app_id
ADZUNA_APP_KEY=your_app_key

## Run

```powershell
python -m src.scrape.timesjobs
python -m src.api.adzuna
```

## Data sources
- **TimesJobs** — job listings, pulled from their internal API
- **Adzuna** — job listings, via their public REST API

## Status
- [x] Postgres schema
- [x] TimesJobs scraper
- [x] Adzuna API integration
- [ ] Foundit scraper
- [ ] Data cleaning
- [ ] SQL analysis
- [ ] Regression
- [ ] Excel benchmarker
- [ ] Power BI dashboard
