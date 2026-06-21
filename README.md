# CeFest Form Processing

Utility scripts for normalising form exports, converting rows to JSON payloads, and uploading them to an HTTP endpoint such as Firebase.

This repo is used as the upload entry point for CE Fest participant data before the backend allocation scripts process it.

**What This Repo Contains**

- [script.py](script.py): uploads the current AY26/27 participant Excel export using [newmapping.json](newmapping.json).
- [pastdata.py](pastdata.py): uploads older AY25/26 participant Excel data using [oldmapping.json](oldmapping.json).
- [test.py](test.py): dry-run script that reads test Excel data, converts rows, and stores payloads in an in-memory `fake_db`.
- [helpers.py](helpers.py): shared mapping, renaming, parsing, fallback, and upload helpers used by `script.py`, `pastdata.py`, and `test.py`.
- [oldmapping.json](oldmapping.json): raw form headers mapped to payload keys for the older form format.
- [newmapping.json](newmapping.json): raw form headers mapped to payload keys for the current form format.
- [onboarding.py](onboarding.py): CSV onboarding flow for EXCO data. This still uses its own inline mapping.
- [workings.ipynb](workings.ipynb): notebook scratchpad for earlier testing and troubleshooting.
- [requirements.txt](requirements.txt): Python dependencies.

**Getting Started**

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root. You can copy [`.env.example`](.env.example) if present, or create one manually.

Required variables:

- `ENDPOINT`: HTTP endpoint to POST converted JSON payloads to.
- `EXCEL_PATH`: Excel file used by `script.py` for current participant uploads.
- `PAST_PATH`: Excel file used by `pastdata.py` for older participant uploads.
- `TEST_PATH`: Excel file used by `test.py` for dry-run testing.
- `EXCO_PATH`: CSV file used by `onboarding.py` for EXCO onboarding.

Example `.env`:

```text
ENDPOINT=https://your-firebase-endpoint.example/submit
EXCEL_PATH=C:\Users\you\Downloads\current_form_export.xlsx
PAST_PATH=C:\Users\you\Downloads\past_form_export.xlsx
TEST_PATH=C:\Users\you\Downloads\test_form_export.xlsx
EXCO_PATH=C:\Users\you\Downloads\exco_form_export.csv
```

**Usage**

Dry-run without network upload:

```bash
python test.py
```

`test.py` reads `TEST_PATH`, loads [oldmapping.json](oldmapping.json), converts rows, appends payloads to `fake_db`, and prints test output. Use this to confirm mapping and payload shape before uploading.

Upload current participant data:

```bash
python script.py
```

`script.py` reads `EXCEL_PATH`, loads [newmapping.json](newmapping.json), filters out rows where `PDPA` equals `I disagree`, converts each row, and POSTs each payload to `ENDPOINT`.

Upload past participant data:

```bash
python pastdata.py
```

`pastdata.py` reads `PAST_PATH`, loads [oldmapping.json](oldmapping.json), applies the same PDPA filter, converts each row, and POSTs each payload to `ENDPOINT`.

Run the CSV onboarding flow:

```bash
python onboarding.py
```

`onboarding.py` reads `EXCO_PATH`, parses the CSV, and POSTs each row to `ENDPOINT`.

**Mapping Format**

Participant mappings now live in JSON files instead of Python dictionaries.

Each mapping entry follows this format:

```json
{
  "Raw form column header": "payload_key"
}
```

For example:

```json
{
  "What is your full name?": "full_name",
  "First Choice": "trail_first_choice",
  "2": "PDPA"
}
```

To support a changed form, edit the left side to match the exported form column header. The right side should stay as the payload field name expected by the backend.

Current mapping files:

- [newmapping.json](newmapping.json): used by `script.py` for AY26/27 participant uploads.
- [oldmapping.json](oldmapping.json): used by `pastdata.py` and `test.py` for AY25/26 or older-format participant uploads.

The loader normalises whitespace in column headers before renaming, so small differences like extra spaces or newlines are usually handled.

**Key Points**

- PDPA filter: `script.py`, `pastdata.py`, and `test.py` filter out rows where `PDPA == "I disagree"`. `onboarding.py` does not apply that filter.
- Fallback fields: [helpers.py](helpers.py) fills missing non-form fields with defaults: `role="Participant"`, `status="pending"`, `round=1`, and missing fourth/fifth trail choices as `None`.
- Numeric parsing: `year` and trail choice fields are converted from strings like `T1` or `Year 2` into numbers where possible.
- Date handling: `created_at` is converted to an ISO-formatted value before upload.
- Upload: `helpers.upload_data()` sends JSON with `Content-Type: application/json`.

**Development Notes**

- The notebook `workings.ipynb` contains my initial workings for tinkering with the different functions and troubleshooting before deriving the final iteration of the script
- Keep participant mapping changes in JSON where possible.
- Put shared parsing or upload changes in [helpers.py](helpers.py), since `script.py`, `pastdata.py`, and `test.py` all use it.
- Dependencies are minimal: `pandas`, `numpy`, and `openpyxl` for Excel reading.
