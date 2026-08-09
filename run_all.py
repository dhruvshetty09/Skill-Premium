import sys
from pathlib import Path

from src.clean.clean_pipeline import clean_all
from src.load.to_postgres import load
from src.checks.data_quality_checks import run_checks


def step(name, fn):
    print(f"\n{'='*50}")
    print(f"STEP: {name}")
    print('='*50)
    fn()


def main():
    step("clean + parse + dedupe", clean_all)
    step("load into postgres", load)
    step("run data quality checks", lambda: run_checks())

    print("\npipeline finished.")


if __name__ == "__main__":
    main()