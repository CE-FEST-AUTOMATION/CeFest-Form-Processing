# CeFest Form Processing

Small utility scripts for normalising form exports (Excel/CSV), converting rows to JSON payloads, and uploading them to an HTTP endpoint (e.g. Firebase).

**What this repo contains**
- **Files:** [script.py](script.py), [onboarding.py](onboarding.py), [test.py](test.py), [workings.ipynb](workings.ipynb), [requirements.txt](requirements.txt)
- **Purpose:** read a form export, rename columns via a `mapping` dict, normalise types/strings, and POST each row as JSON to an endpoint.

Getting started
- **Install dependencies:**

  ```bash
  pip install -r requirements.txt
  ```

- **Create a `.env` file** in the project root with at least the endpoint and path variables:

  - `ENDPOINT` — HTTP endpoint to POST converted JSON to.
  - `EXCEL_PATH` — path to the Excel file used by `script.py` and `test.py` (e.g. `C:\path\to\file.xlsx`).
  - `EXCO_PATH` — path to the CSV file used by `onboarding.py` (e.g. `C:\path\to\file.csv`).

  Example `.env`:

  ```text
  ENDPOINT=https://your-firebase-endpoint.example/submit
  EXCEL_PATH=C:\Users\you\Downloads\form_export.xlsx
  EXCO_PATH=C:\Users\you\Downloads\form_export.csv
  ```

Usage
- Quick test (no network): run `test.py` — it reads `EXCEL_PATH`, converts rows, and appends payloads to an in-memory `fake_db` then prints them. This is the safest way to confirm mapping and payload shape.

  ```bash
  python test.py
  ```

- Upload mode (Excel): `script.py` reads `EXCEL_PATH`, filters out rows where PDPA column equals `I disagree`, converts rows and POSTs them to `ENDPOINT`.

  ```bash
  python script.py
  ```

- CSV onboarding flow: `onboarding.py` reads `EXCO_PATH` (CSV) and posts each row to `ENDPOINT`.

  ```bash
  python onboarding.py
  ```

Key points / customization
- Column mapping: each script contains a `mapping` dict at the top mapping the raw form header (left) to the desired JSON key (right). Edit this to match your export headers.
- PDPA filter: `script.py` and `test.py` filter out rows where normalized `PDPA` == `I disagree`. `onboarding.py` does not apply that filter — change as needed.
- Date handling: the scripts convert `created_at` to ISO strings (or Python datetimes in some paths) and normalise numeric fields via `parse_numeric_from_string`.
- Upload: the `upload_data` function performs a POST with `Content-Type: application/json`. If you want to dry-run, replace or comment the call and use `sim_upload` (as in `test.py`).

Development notes
- The notebook `workings.ipynb` contains an exploratory version of the same logic and examples for inspecting a single row.
- Dependencies are minimal: `pandas`, `numpy`, `openpyxl` (for Excel reading).

If you want I can:
- run the `test.py` flow with a sample file (if you provide one),
- or open a PR that renames env keys to be consistent across scripts (e.g. use `EXCEL_PATH` everywhere).
