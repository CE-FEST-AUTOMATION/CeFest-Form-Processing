import json
import os
import re
import urllib.request
from pathlib import Path
from datetime import date, datetime
import pandas as pd
import numpy as np
import openpyxl


fallback = {'role':'Participant', 
            'status' : 'pending', 
            'round' : 1 , 
            'trail_fourth_choice' : None, 
            'trail_fifth_choice' : None}

'''functions for loading variables'''
def load_mapping(mapping_path) -> dict:
    mapping_file = Path(mapping_path)
    if not mapping_file.exists():
        raise FileNotFoundError(f"Mapping file not found: {mapping_file}")
    with mapping_file.open(encoding="utf-8") as f:
        return json.load(f)
    
def load_env_file(env_path: str = ".env") -> None:
    env_file = Path(env_path)
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

'''functions for parsing '''
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
    for k in ('trail_first_choice', 'trail_second_choice', 'trail_third_choice', 'trail_fourth_choice', 'trail_fifth_choice'):
        if k in init and k != None:
            init[k] = parse_numeric_from_string(init[k])
    return init


'''function for formatting a row into a payload'''
def process_row(srs: pd.Series, mapping: dict) -> dict: #accepts a pandas Series (one row) and returns a JSON-serializable dict."""
    cols = mapping.values()
    non_form = fallback.keys()
    d = {}
    for col_name in cols:
        if col_name == 'created_at':
            created_at = pd.to_datetime(srs.get('created_at'), errors='coerce')
            d['created_at'] = created_at.to_pydatetime() if not pd.isna(created_at) else None
            continue
        if col_name in non_form:
            val = srs.get(col_name)
            d[col_name] = val if not pd.isna(val) else fallback[col_name]
        else:
            d[col_name] = srs.get(col_name)
    d = format_vals(d)
    for k in list(d.keys()):
        d[k] = normalize_value(d[k])
    return d



def normalize_value(v):
    if pd.isna(v):
        return None
    if isinstance(v, (datetime, date, pd.Timestamp)):
        return v.isoformat()
    if isinstance(v, str):
        v = v.replace('\ufeff', '').replace('\u200b', '').replace('\xa0', ' ')
        v = re.sub(r'\s+', ' ', v).strip()
        return v
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating,)):
        return float(v)
    if isinstance(v, (np.bool_,)):
        return bool(v)
    return v


'''function for uploading'''
def upload_data(endpt, payload : dict): #function to upload data onto firebase (DONT NEED TOUCH)
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        endpt,
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