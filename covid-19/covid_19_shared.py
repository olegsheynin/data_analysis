import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

def list_of_JHUD_US_states():
    conf_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
    df = pd.read_csv(conf_url)
    res = df["Province_State"]
    return res.unique()    


#------------------------------------------------------
def loadJHUData_USA(st : str):
    class Settings:
        from datetime import datetime

        conf_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
        deaths_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"

        state = st

        dt = datetime.now().strftime("%Y-%m-%d")
        save_file_name = f'./{state}.{dt}.covid-19.csv'


    confirmed = pd.read_csv(Settings.conf_url)
    deaths = pd.read_csv(Settings.deaths_url)


    for df in [deaths, confirmed]:
        # Filter Country
        df.drop(df[ df["Province_State"] != Settings.state].index, inplace=True)
        # Drop Unused Columns:
        columns_to_delete = range(0, 11)
        df.drop(df.columns[columns_to_delete], axis=1, inplace=True)
        if 'Population' in df:
            del df['Population']
        df.reset_index()
    
    
    confirmed_ser = confirmed.sum()
    confirmed_ser.index.names = ["Date"]
    confirmed_ser.index = pd.to_datetime(confirmed_ser.index)

    deaths_ser = deaths.sum()
    deaths_ser.index.names = ["Date"]
    deaths_ser.index = pd.to_datetime(deaths_ser.index)
    
    df = pd.DataFrame({
        "Confirmed" : confirmed_ser
        , "Dead" : deaths_ser
                      }
    )
    return df


def list_of_JHUD_countries():
    conf_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    df = pd.read_csv(conf_url)
    countries = df["Country/Region"]
    return countries.unique()    


def load_JHUD_global(st : str):
    class Settings:
        from datetime import datetime

        conf_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
        rcvrd_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
        deaths_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

        country = st

        dt = datetime.now().strftime("%Y-%m-%d")
        save_file_name = f'./{country}.{dt}.covid-19.csv'


    confirmed = pd.read_csv(Settings.conf_url)
    deaths = pd.read_csv(Settings.deaths_url)
    recs = pd.read_csv(Settings.rcvrd_url)


    for df in [deaths, confirmed, recs]:
        # Filter Country
        df.drop(df[ df["Country/Region"] != Settings.country].index, inplace=True)
        # Drop Unused Columns:
        columns_to_delete = range(0, 5)
        df.drop(df.columns[columns_to_delete], axis=1, inplace=True)
        df.reset_index()
    
    
    confirmed_ser = confirmed.sum()
    confirmed_ser.index.names = ["Date"]
    confirmed_ser.index = pd.to_datetime(confirmed_ser.index)

    deaths_ser = deaths.sum()
    deaths_ser.index.names = ["Date"]
    deaths_ser.index = pd.to_datetime(deaths_ser.index)
    
    rec_ser = recs.sum()
    rec_ser.index.names = ["Date"]
    rec_ser.index = pd.to_datetime(deaths_ser.index)

    df = pd.DataFrame({
        "Confirmed" : confirmed_ser
        , "Dead" : deaths_ser
        , "Recovered" : rec_ser
                      }
    )
    return df



