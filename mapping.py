from rapidfuzz import process

main_col = ['store_id','sales','date']

extra_col = [
    'promo',
    "StateHoliday",
    "SchoolHoliday"
]
expected = main_col + extra_col

def auto_mapping(df):
    mapping = {}

    for col in df.columns:
        match,score,_ = process.extractOne(col.lower(),expected)

        if score > 70 and col != match:
            mapping[col] = match
    df = df.rename(columns = mapping) 
    return df

def auto_manual_mapping(df,manual_mapping = None):
    if not manual_mapping:
        return df
    reverse = {v.lower(): k for k, v in manual_mapping.items()}
    df = df.rename(columns = reverse)
    return df


    
