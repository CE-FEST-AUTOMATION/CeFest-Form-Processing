import os
import pandas as pd
import helpers as h
 
mapping_path = "newmapping.json"
required_fields = (
    "round",
    "trail_first_choice",
    "trail_second_choice",
    "trail_third_choice",
)

def main():
    h.load_env_file()
    endpoint , path = read_env()
    mapping = h.load_mapping(mapping_path)
    renamed_df = h.rename(mapping, pd.read_excel(path))
    filtered = renamed_df[~(renamed_df['PDPA'] == 'I disagree')] 
    failed_uploads = []
    n_successful = 0
    for index, row in filtered.iterrows():
        payload = h.process_row(row, mapping)
        missing = h.missing_required_fields(payload, required_fields)
        if missing:
            name = payload.get("full_name") or f"Excel row {index + 2}"
            failed_uploads.append(f"{payload.get("full_name")} ({payload.get("tele_handle")}) failed upload : missing required fields{missing}")
            print(f"Skipping {name}: missing required fields: {missing}")
            continue
        n_successful+=1
        h.upload_data(endpoint, payload) #REAL UPLOAD LINE, UNCOMMENT FOR ACTUAL US
    h.print_diagnostics(failed_uploads, n_successful)

def read_env():
    endpoint = os.getenv("ENDPOINT") # endpoint for uploading
    if not endpoint:
        raise ValueError("ENDPOINT is not set. Add it to .env as ENDPOINT=...")
    # path to Excel file on computer — read from .env via `EXCEL_PATH`
    path = os.getenv("EXCEL_PATH")
    if not path:
        raise ValueError("EXCEL_PATH is not set. Add it to .env as EXCEL_PATH=C:\\path\\to\\file.xlsx")
    return endpoint, path


main()
