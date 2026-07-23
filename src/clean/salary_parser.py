import re

USD_TO_INR = 83

NOT_DISCLOSED_WORDS = ["not disclosed", "confidential", "negotiable", "as per industry", ""]


def parse_salary(raw):
    result = {"min": None, "max": None, "mid": None}

    if raw is None:
        return result

    text = str(raw).strip()
    if text.lower() in NOT_DISCLOSED_WORDS:
        return result

    is_usd = "$" in text
    multiplier = USD_TO_INR if is_usd else 1

    cleaned = text.replace("$", "").replace(" ", "")

    try:
        parts = cleaned.split("-")
        nums = [float(p) for p in parts if p.replace(".", "", 1).lstrip("-").isdigit()]
    except ValueError:
        nums = []

    if not nums or all(n == 0 for n in nums):
        return result

    if len(nums) == 1:
        result["min"] = int(nums[0] * multiplier)
        result["max"] = int(nums[0] * multiplier)
    else:
        result["min"] = int(min(nums[0], nums[-1]) * multiplier)
        result["max"] = int(max(nums[0], nums[-1]) * multiplier)

    result["mid"] = (result["min"] + result["max"]) / 2
    return result


def parse_lakh_salary(raw):
    result = {"min": None, "max": None, "mid": None}

    if raw is None:
        return result

    text = str(raw).strip()
    if text.lower() in NOT_DISCLOSED_WORDS:
        return result

    is_usd = "$" in text
    multiplier = USD_TO_INR if is_usd else 1

    cleaned = text.replace("₹", "").replace("$", "").replace("Rs.", "").replace("Rs", "")
    cleaned = cleaned.replace(",", "").strip()

    is_lac = "lac" in cleaned.lower() or "lakh" in cleaned.lower()
    is_crore = "crore" in cleaned.lower() or "cr" in cleaned.lower()

    numbers = re.findall(r"\d+\.?\d*", cleaned)
    if not numbers:
        return result

    nums = [float(n) for n in numbers]

    unit = 1
    if is_lac:
        unit = 100_000
    elif is_crore:
        unit = 10_000_000

    nums = [n * unit * multiplier for n in nums]

    if len(nums) == 1:
        result["min"] = int(nums[0])
        result["max"] = int(nums[0])
    else:
        result["min"] = int(min(nums[0], nums[-1]))
        result["max"] = int(max(nums[0], nums[-1]))

    result["mid"] = (result["min"] + result["max"]) / 2
    return result


def parse_experience(raw):
    if raw is None:
        return (None, None)

    text = str(raw).lower().strip()

    if "fresher" in text or "entry" in text:
        return (0, 1)

    numbers = re.findall(r"\d+", text)
    if not numbers:
        return (None, None)

    min_years = int(numbers[0])

    if "+" in text:
        return (min_years, None)

    if len(numbers) >= 2:
        return (min_years, int(numbers[1]))

    return (min_years, None)


if __name__ == "__main__":
    tests = [
        "400000-650000",
        "0-0",
        "$70000-90000",
        "",
    ]
    for t in tests:
        print(t, "->", parse_salary(t))

    lakh_tests = [
        "4-6 Lacs P.A.",
        "Rs 4,00,000 - 6,50,000",
        "Not Disclosed",
    ]
    for t in lakh_tests:
        print(t, "->", parse_lakh_salary(t))

    exp_tests = ["3-5 years", "5+ years", "Fresher", "2 years", "0-1 years"]
    for t in exp_tests:
        print(t, "->", parse_experience(t))