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
