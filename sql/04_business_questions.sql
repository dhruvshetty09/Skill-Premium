SELECT skill_name, postings_requiring, demand_pct
FROM vw_skill_demand
LIMIT 15;


SELECT skill_name, postings_with_salary, median_salary_with_skill
FROM vw_skill_salary_premium
LIMIT 15;


SELECT * FROM vw_city_pay_index;


SELECT
    CASE
        WHEN exp_min_years IS NULL THEN 'unknown'
        WHEN exp_min_years <= 1 THEN '0-1 years'
        WHEN exp_min_years <= 3 THEN '1-3 years'
        WHEN exp_min_years <= 5 THEN '3-5 years'
        ELSE '5+ years'
    END AS experience_band,
    COUNT(*) AS postings,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_mid_inr) AS median_salary
FROM fact_postings
WHERE has_salary_disclosed = TRUE
GROUP BY experience_band
ORDER BY MIN(exp_min_years);


SELECT dcp.company_name, COUNT(*) AS postings
FROM fact_postings fp
JOIN dim_company dcp ON fp.company_id = dcp.company_id
JOIN dim_role dr ON fp.role_id = dr.role_id
WHERE dr.role_canonical = 'data_analyst' AND dr.seniority_level = 'Entry-Level'
GROUP BY dcp.company_name
HAVING COUNT(*) >= 2
ORDER BY postings DESC
LIMIT 10;


SELECT
    ds1.skill_name AS skill_a,
    ds2.skill_name AS skill_b,
    COUNT(*) AS times_together
FROM bridge_posting_skills bps1
JOIN bridge_posting_skills bps2
    ON bps1.posting_id = bps2.posting_id AND bps1.skill_id < bps2.skill_id
JOIN dim_skill ds1 ON bps1.skill_id = ds1.skill_id
JOIN dim_skill ds2 ON bps2.skill_id = ds2.skill_id
GROUP BY ds1.skill_name, ds2.skill_name
ORDER BY times_together DESC
LIMIT 10;


SELECT
    COUNT(*) FILTER (WHERE dr.seniority_level = 'Entry-Level' AND fp.exp_min_years >= 2) AS scam_postings,
    COUNT(*) FILTER (WHERE dr.seniority_level = 'Entry-Level') AS total_entry_level,
    ROUND(
        COUNT(*) FILTER (WHERE dr.seniority_level = 'Entry-Level' AND fp.exp_min_years >= 2) * 100.0
        / NULLIF(COUNT(*) FILTER (WHERE dr.seniority_level = 'Entry-Level'), 0),
        1
    ) AS pct_asking_too_much
FROM fact_postings fp
JOIN dim_role dr ON fp.role_id = dr.role_id;


SELECT
    CASE WHEN job_title ILIKE '%remote%' THEN 'remote' ELSE 'on-site / unspecified' END AS work_mode,
    COUNT(*) AS postings,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_mid_inr) AS median_salary
FROM fact_postings
WHERE has_salary_disclosed = TRUE
GROUP BY work_mode;


SELECT week_start, role_canonical, postings_count
FROM vw_posting_velocity
ORDER BY week_start;


SELECT job_title, city_name, skills[1] AS top_skill, COUNT(*) AS occurrences
FROM vw_posting_with_skills
WHERE skills IS NOT NULL
GROUP BY job_title, city_name, skills[1]
ORDER BY occurrences DESC
LIMIT 5;