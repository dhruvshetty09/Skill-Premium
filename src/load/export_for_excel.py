import os 
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()
engine= create_engine(os.getenv("DATABASE_URL"))

df= pd.read_sql("SELECT * FROM vw_posting_with_skills", engine)
print(df.columns.tolist())

df["skills_str"]= df["skills"].apply(lambda s: ", ".join(s) if s is not None else "")

top_skills= ["SQL", "Python", "Power BI", "Excel", "Machine Learning", "Data Visualization"]

for skill in top_skills:
    col_name= "has_" + skill.lower().replace(" ","_")
    df[col_name]= df["skills"].apply(lambda s:skill in s if s is not None else False)
print(df.columns.tolist())

output_cols= ["job_title", "city_name", "company_name", "role_canonical",
              "seniority_level", "exp_min_years", "salary_mid_inr", 
              "has_salary_disclosed"] + ["has_" + s.lower().replace(" ", "_") for s in top_skills]

df[output_cols].to_csv("data/processed/postings_for_excel.csv", index=False)

print(f"exported {len(df)} rows to data/processed/postings_for_excel.csv")