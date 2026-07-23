from rapidfuzz import fuzz


def make_key(row):
    title = str(row.get("title") or "").lower().strip()
    company = str(row.get("company") or "").lower().strip()
    city = str(row.get("city") or "").lower().strip()
    return f"{title} | {company} | {city}"


def flag_duplicates(rows, threshold=85):
    keys = [make_key(r) for r in rows]
    is_dup = [False] * len(rows)

    for i in range(len(rows)):
        if is_dup[i]:
            continue
        for j in range(i + 1, len(rows)):
            if is_dup[j]:
                continue
            score = fuzz.token_set_ratio(keys[i], keys[j])
            if score >= threshold:
                is_dup[j] = True

    for i, row in enumerate(rows):
        row["is_duplicate"] = is_dup[i]

    return rows


if __name__ == "__main__":
    sample = [
        {"title": "Data Analyst", "company": "Google", "city": "Bangalore"},
        {"title": "Data Analyst - Fresher", "company": "Google", "city": "Bangalore"},
        {"title": "Data Analyst", "company": "Amazon", "city": "Mumbai"},
        {"title": "Career Opportunities: Data Analyst (49640)", "company": "Incedo", "city": "Mexico"},
        {"title": "Career Opportunities: Data Analyst (49640)", "company": "Incedo", "city": "Mexico"},
    ]
    result = flag_duplicates(sample)
    for r in result:
        print(r)