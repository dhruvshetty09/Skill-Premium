CREATE TABLE IF NOT EXISTS dim_company (
    company_id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    company_name_canonical VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_city (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    tier INT,
    UNIQUE(city_name, state)
);

CREATE TABLE IF NOT EXISTS dim_skill (
    skill_id SERIAL PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS dim_role (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(150) NOT NULL,
    role_canonical VARCHAR(150),
    seniority_level VARCHAR(50),
    UNIQUE(role_canonical, seniority_level)
);

CREATE TABLE IF NOT EXISTS fact_postings (
    posting_id SERIAL PRIMARY KEY,
    company_id INT NOT NULL REFERENCES dim_company(company_id),
    city_id INT REFERENCES dim_city(city_id),
    role_id INT NOT NULL REFERENCES dim_role(role_id),
    job_title VARCHAR(255),
    job_description TEXT,
    job_url VARCHAR(500) UNIQUE,
    source_site VARCHAR(50),
    salary_min_inr INT CHECK (salary_min_inr IS NULL OR salary_min_inr > 0),
    salary_max_inr INT CHECK (salary_max_inr IS NULL OR salary_max_inr > 0),
    salary_mid_inr NUMERIC(12, 2),
    has_salary_disclosed BOOLEAN,
    exp_min_years INT CHECK (exp_min_years IS NULL OR exp_min_years >= 0),
    exp_max_years INT CHECK (exp_max_years IS NULL OR exp_max_years >= 0),
    scraped_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (salary_max_inr IS NULL OR salary_min_inr IS NULL OR salary_min_inr <= salary_max_inr),
    CHECK (exp_max_years IS NULL OR exp_min_years IS NULL OR exp_min_years <= exp_max_years)
);

CREATE TABLE IF NOT EXISTS bridge_posting_skills (
    posting_id INT NOT NULL REFERENCES fact_postings(posting_id) ON DELETE CASCADE,
    skill_id INT NOT NULL REFERENCES dim_skill(skill_id),
    PRIMARY KEY (posting_id, skill_id)
);

CREATE INDEX IF NOT EXISTS idx_postings_company ON fact_postings(company_id);
CREATE INDEX IF NOT EXISTS idx_postings_city ON fact_postings(city_id);
CREATE INDEX IF NOT EXISTS idx_postings_role ON fact_postings(role_id);
CREATE INDEX IF NOT EXISTS idx_postings_source ON fact_postings(source_site);
CREATE INDEX IF NOT EXISTS idx_postings_has_salary ON fact_postings(has_salary_disclosed);
CREATE INDEX IF NOT EXISTS idx_bridge_skill ON bridge_posting_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_bridge_posting ON bridge_posting_skills(posting_id);

INSERT INTO dim_city (city_name, state, tier) VALUES
    ('Bangalore', 'Karnataka', 1),
    ('Mumbai', 'Maharashtra', 1),
    ('Delhi', 'Delhi', 1),
    ('Pune', 'Maharashtra', 2),
    ('Hyderabad', 'Telangana', 1),
    ('Chennai', 'Tamil Nadu', 1),
    ('Gurgaon', 'Haryana', 1),
    ('Noida', 'Uttar Pradesh', 2),
    ('Kolkata', 'West Bengal', 2),
    ('Ahmedabad', 'Gujarat', 2)
ON CONFLICT DO NOTHING;