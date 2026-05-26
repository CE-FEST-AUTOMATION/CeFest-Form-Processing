import json
import urllib.request
import pandas as pd
import numpy as np
import re

#endpoint for uploading 
ENDPOINT = "https://inpro-participants-submit-3avzbu5vaa-as.a.run.app" #<- CHANGE HERE WHEN USING 

#pathing to file on computer 
path = "C:\\Users\\xuan2\\Downloads\\_CE Fest 2026 Participant Sign-up Form!(1-3).xlsx" #<- CHANGE HERE WHEN USING 

def main():
    renamed_df = rename(mapping, pd.read_excel(path))
    filtered = renamed_df[~(renamed_df['PDPA'] == 'I disagree')] 
    for _, row in filtered.iterrows():
        payload = process_row(row)
        #upload_data(payload) #REAL UPLOAD LINE, UNCOMMENT FOR ACTUAL USE


'''Stuff for renaming''' #<- CHANGE HERE based on different form submissions
mapping = {"Completion time":"created_at",
           "What is your Telegram Handle? (eg. @ilovecefest)\n": "tele_handle",
           "What is your full name?": "full_name",
           "What house are you from ? ": "house",
           "I am currently... (in AY26/27)" : "year",
            "Email": "student_email",
            "What is your gender ? ": "gender",
            "First Choice ": "trail_first_choice",
            "Second Choice ": "trail_second_choice",
            "Third Choice ": "trail_third_choice",
            'Why did you select your chosen trails ? (EG: T1 because .....) ': "writeup",
            '2' : 'PDPA'}

def normalize(s):
    s = '' if s is None else str(s)
    # remove BOM, zero-width, replace newlines & NBSP, collapse spaces
    s = s.replace('\ufeff', '').replace('\u200b','').replace('\xa0',' ')
    s = s.replace('\r',' ').replace('\n',' ')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def rename(mapping : dict, raw: pd.DataFrame):
    cols_norm = [normalize(c) for c in raw.columns] #normaliising the cols of df
    norm_map = {normalize(k): v for k, v in mapping.items()} #create updated mappings
    raw.columns = cols_norm
    raw = raw.rename(columns=norm_map)
    return raw


'''stuff for parsing into payload'''
def parse_numeric_from_string(v):
    if pd.isna(v):
        return None
    if isinstance(v, (int, float)):
        try:
            return int(v)
        except Exception:
            pass
    s = str(v)
    m = re.search(r'(\d+)', s)
    return int(m.group(1)) if m else s

def format_vals(init: dict) -> dict:
    if 'year' in init:
        init['year'] = parse_numeric_from_string(init['year'])
    for k in ('trail_first_choice', 'trail_second_choice', 'trail_third_choice'):
        if k in init:
            init[k] = parse_numeric_from_string(init[k])
    return init

def normalize_value(v):
    if pd.isna(v):
        return None
    if isinstance(v, pd.Timestamp):
        return v.to_pydatetime()
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v

def process_row(srs: pd.Series) -> dict:
    """Accepts a pandas Series (one row) and returns a JSON-serializable dict."""
    cols = ['created_at','tele_handle', 'full_name', 'house', 'student_email', 'gender', 'year', 'status', 'role', 'trail_first_choice', 'trail_second_choice', 'trail_third_choice', 'writeup'] #edit col names according to the final one
    d = {}
    for col_name in cols:
        if col_name == 'created_at':
            created_at = pd.to_datetime(srs.get('created_at'), errors='coerce')
            d['created_at'] = created_at.to_pydatetime() if not pd.isna(created_at) else None
            continue
        if col_name == 'role':
            val = srs.get('role')
            d['role'] = val if not pd.isna(val) else "Participant"
        elif col_name == 'status':
            val = srs.get('status')
            d['status'] = val if not pd.isna(val) else 'pending'
        else:
            d[col_name] = srs.get(col_name)
    d = format_vals(d)
    for k in list(d.keys()):
        d[k] = normalize_value(d[k])
    return d


'''function for uploading'''
def upload_data(payload : dict): #function to upload data onto firebase (DONT NEED TOUCH)
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        ENDPOINT,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = resp.read().decode()
            print(f"Status: {resp.status}")
            print(f"Response: {body}")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"Status: {e.code}")
        print(f"Error: {body}")

main()