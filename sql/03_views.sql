CREATE OR REPLACE VIEW vw_posting_with_skills AS
SELECT
    fp.posting_id,
    fp.job_title,
    dc.city_name,
    dcp.company_name,
    dr.role_canonical,
    dr.seniority_level,
    fp.salary_mid_inr,
    fp.has_salary_disclosed,
    fp.exp_min_years,
    fp.exp_max_years,
    fp.source_site,
    ARRAY_AGG(ds.skill_name) FILTER (WHERE ds.skill_name IS NOT NULL) AS skills
FROM fact_postings fp
LEFT JOIN dim_city dc ON fp.city_id = dc.city_id
LEFT JOIN dim_company dcp ON fp.company_id = dcp.company_id
LEFT JOIN dim_role dr ON fp.role_id = dr.role_id
LEFT JOIN bridge_posting_skills bps ON fp.posting_id = bps.posting_id
LEFT JOIN dim_skill ds ON bps.skill_id = ds.skill_id
GROUP BY fp.posting_id, fp.job_title, dc.city_name, dcp.company_name,
         dr.role_canonical, dr.seniority_level, fp.salary_mid_inr,
         fp.has_salary_disclosed, fp.exp_min_years, fp.exp_max_years, fp.source_site;


CREATE OR REPLACE VIEW vw_city_pay_index AS
WITH city_medians AS (
    SELECT
        dc.city_name,
        COUNT(*) AS postings_with_salary,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fp.salary_mid_inr) AS city_median_salary
    FROM fact_postings fp
    JOIN dim_city dc ON fp.city_id = dc.city_id
    WHERE fp.has_salary_disclosed = TRUE
    GROUP BY dc.city_name
    HAVING COUNT(*) >= 5
),
national AS (
    SELECT PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_mid_inr) AS national_median
    FROM fact_postings
    WHERE has_salary_disclosed = TRUE
)
SELECT
    cm.city_name,
    cm.postings_with_salary,
    cm.city_median_salary,
    n.national_median,
    ROUND(((cm.city_median_salary / n.national_median) * 100)::numeric, 1) AS pay_index
FROM city_medians cm
CROSS JOIN national n
ORDER BY pay_index DESC;


CREATE OR REPLACE VIEW vw_skill_demand AS
SELECT
    ds.skill_name,
    COUNT(DISTINCT bps.posting_id) AS postings_requiring,
    (SELECT COUNT(*) FROM fact_postings) AS total_postings,
    ROUND(
        COUNT(DISTINCT bps.posting_id) * 100.0 / NULLIF((SELECT COUNT(*) FROM fact_postings), 0),
        2
    ) AS demand_pct
FROM dim_skill ds
JOIN bridge_posting_skills bps ON ds.skill_id = bps.skill_id
GROUP BY ds.skill_name
ORDER BY postings_requiring DESC;


CREATE OR REPLACE VIEW vw_skill_salary_premium AS
SELECT
    ds.skill_name,
    COUNT(DISTINCT fp.posting_id) AS postings_with_salary,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY fp.salary_mid_inr) AS median_salary_with_skill
FROM dim_skill ds
JOIN bridge_posting_skills bps ON ds.skill_id = bps.skill_id
JOIN fact_postings fp ON bps.posting_id = fp.posting_id
WHERE fp.has_salary_disclosed = TRUE
GROUP BY ds.skill_name
HAVING COUNT(DISTINCT fp.posting_id) >= 5
ORDER BY median_salary_with_skill DESC;


CREATE OR REPLACE VIEW vw_posting_velocity AS
SELECT
    DATE_TRUNC('week', scraped_at) AS week_start,
    dr.role_canonical,
    COUNT(*) AS postings_count
FROM fact_postings fp
JOIN dim_role dr ON fp.role_id = dr.role_id
GROUP BY DATE_TRUNC('week', scraped_at), dr.role_canonical
ORDER BY week_start;