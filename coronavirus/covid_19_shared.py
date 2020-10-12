import numpy as np
from matplotlib import pyplot as plt
import pandas as pd


def loadJHUData(cntr : str, to_save : bool):
    from datetime import datetime
    class Settings:
        from datetime import datetime

        conf_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
        rcvrd_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
        deaths_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

        country=cntr
        
        dt = datetime.now().strftime("%Y-%m-%d")
        save_file_name = f'./{cntr}.{dt}.covid-19.csv'


    # default is not to save
    if to_save is None:
        to_save = False
        
    confirmed = pd.read_csv(Settings.conf_url)
    recovered = pd.read_csv(Settings.rcvrd_url)
    deaths = pd.read_csv(Settings.deaths_url)


    for df in [confirmed, recovered, deaths]:
        # Filter Country
        df.drop(df[ df["Country/Region"] != Settings.country].index, inplace=True)
        # Drop Unused Columns:
        columns_to_delete = [0,1,2,3]
        df.drop(df.columns[columns_to_delete], axis=1, inplace=True) 

    deaths["Category"] = pd.Series(["Dead"], index=deaths.index)
    confirmed["Category"] = pd.Series(["Confirmed"], index=confirmed.index)
    recovered["Category"] = pd.Series(["Recovered"], index=recovered.index)


    df = confirmed
    df = df.append(recovered)
    df = df.append(deaths)

    df = df.set_index("Category")
    df.index.names = ['']
    df = df.transpose()
    df.index.names = ["Date"]
    df.index = pd.to_datetime(df.index)
    
    if to_save:
        df.to_csv(Settings.save_file_name, index=True)
    return df

#------------------------------------------------------
#------------------------------------------------------
#------------------------------------------------------
def loadJHUData_USA(st : str):
    class Settings:
        from datetime import datetime

        conf_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
        deaths_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"

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
