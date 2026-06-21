import os
import pandas as pd
import helpers as h

mapping_path = "oldmapping.json"

def main():
    h.load_env_file()
    endpoint , path = read_env()
    mapping = h.load_mapping(mapping_path)
    renamed_df = h.rename(mapping, pd.read_excel(path))
    filtered = renamed_df[~(renamed_df['PDPA'] == 'I disagree')] 
    for _, row in filtered.iterrows():
        payload = h.process_row(row, mapping)
        h.upload_data(endpoint, payload) #REAL UPLOAD LINE, UNCOMMENT FOR ACTUAL USE

def read_env():
    endpoint = os.getenv("ENDPOINT") # endpoint for uploading
    if not endpoint:
        raise ValueError("ENDPOINT is not set. Add it to .env as ENDPOINT=...")
    # path to Excel file on computer — read from .env via `EXCEL_PATH`
    path = os.getenv("PAST_PATH")
    if not path:
        raise ValueError("PAST_PATH is not set. Add it to .env as PAST_PATH=C:\\path\\to\\file.xlsx")
    return endpoint, path

main()
