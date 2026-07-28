UPDATE fact_postings
SET city_id = (SELECT city_id FROM dim_city WHERE city_name = 'Bangalore')
WHERE city_id IN (
    SELECT city_id FROM dim_city
    WHERE city_name IN ('Bengaluru', 'Bengaluru / Bangalore', 'Bangalore / Bengaluru')
);

DELETE FROM dim_city
WHERE city_name IN ('Bengaluru', 'Bengaluru / Bangalore', 'Bangalore / Bengaluru')
AND city_id NOT IN (SELECT DISTINCT city_id FROM fact_postings WHERE city_id IS NOT NULL);

UPDATE fact_postings
SET city_id = NULL
WHERE city_id IN (
    SELECT city_id FROM dim_city
    WHERE city_name IN (
        'India',
        'United States of America (USA)',
        'USA',
        'United States',
        'UK',
        'United Kingdom',
        'Remote',
        'Not Specified'
    )
);

DELETE FROM dim_city
WHERE city_name IN (
    'India',
    'United States of America (USA)',
    'USA',
    'United States',
    'UK',
    'United Kingdom',
    'Remote',
    'Not Specified'
)
AND city_id NOT IN (SELECT DISTINCT city_id FROM fact_postings WHERE city_id IS NOT NULL);

UPDATE fact_postings
SET city_id = (SELECT city_id FROM dim_city WHERE city_name = 'Hyderabad')
WHERE city_id IN (
    SELECT city_id FROM dim_city
    WHERE city_name IN ('Hyderabad / Secunderabad, Telangana', 'Hyderabad/Secunderabad', 'Hyderabad / Secunderabad')
);

DELETE FROM dim_city
WHERE city_name IN ('Hyderabad / Secunderabad, Telangana', 'Hyderabad/Secunderabad', 'Hyderabad / Secunderabad')
AND city_id NOT IN (SELECT DISTINCT city_id FROM fact_postings WHERE city_id IS NOT NULL);

UPDATE fact_postings
SET city_id = (SELECT city_id FROM dim_city WHERE city_name = 'Gurgaon')
WHERE city_id IN (
    SELECT city_id FROM dim_city
    WHERE city_name IN ('Gurugram', 'Gurgaon / Gurugram', 'Gurugram / Gurgaon')
);

DELETE FROM dim_city
WHERE city_name IN ('Gurugram', 'Gurgaon / Gurugram', 'Gurugram / Gurgaon')
AND city_id NOT IN (SELECT DISTINCT city_id FROM fact_postings WHERE city_id IS NOT NULL);