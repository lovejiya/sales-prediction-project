import pandas as pd
from db import engine
from mapping import auto_mapping,auto_manual_mapping,main_col,extra_col

def dataframe_updation(df,manual_mapping=None):
    expected = main_col+extra_col
    df.columns = df.columns.str.lower()

    df = auto_manual_mapping(df,manual_mapping)

    df = auto_mapping(df)

    for col in main_col:
        if col not in df.columns:
            raise ValueError(f"Missing Required Columns{col}")
        
    for col in extra_col:
        if col not in df.columns:
            df[col] = 0


    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['promo'] = df['promo'].fillna(0)
    df['StateHoliday'] = df['StateHoliday'].fillna(0)
    df['SchoolHoliday'] = df['SchoolHoliday'].fillna(0)

    return df

def sales_ingest(manual_mapping=None):
    df = pd.read_csv('/Users/jiyajain/Desktop/ML/data/train.csv')

    df = dataframe_updation(df,manual_mapping)

    df.to_sql("sales_data",engine,if_exists = "replace",index = False)
    print(df.shape)
    print("sales data appended!")

def ingest_stores(engine):
    df_stores = pd.read_csv('/Users/jiyajain/Desktop/ML/data/store.csv')  

    df_stores.columns = [col.lower() for col in df_stores.columns]


    df_stores.to_sql("stores_agg", engine, if_exists="replace", index=False)
    print(df_stores.shape)

    print("store data appended!")


if __name__ == "__main__":
    sales_ingest()
    ingest_stores(engine)
