import numpy as np
from matplotlib import pyplot as plt
import pandas as pd

def list_of_JHUD_US_states():
    conf_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
    df = pd.read_csv(conf_url)
    res = df["Province_State"]
    return res.unique()    


#------------------------------------------------------
def load_JHU_Data_USA(st : str):
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


def list_of_JHU_countries():
    conf_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
    df = pd.read_csv(conf_url)
    countries = df["Country/Region"]
    return countries.unique()    


def load_JHU_Data_global(st : str):
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


def growth_pcnt(ser): 
    return (ser - ser.shift(1)) / ser * 100

class Country_COVID19_Stats:
    def __init__(self, Country: str):
        self.country_ = Country
        self.cv_data_ = load_JHU_Data_global(self.country_)
        self.confirmed_new_ = (self.cv_data_.Confirmed - self.cv_data_.Confirmed.shift(1)).dropna()
        self.deaths_new_ = (self.cv_data_.Dead - self.cv_data_.Dead.shift(1)).dropna()
        self.recovered_new_ = (self.cv_data_.Recovered - self.cv_data_.Recovered.shift(1)).dropna()
        self.deaths_new_pcnt_ = growth_pcnt(self.cv_data_.Dead)
        self.confirmed_new_pcnt_ = growth_pcnt(self.cv_data_.Confirmed)


    def added_new_cases(self):

        growth = pd.Series((self.confirmed_new_ - (self.deaths_new_ + self.recovered_new_)).array
                           , index=self.cv_data_.index[1:]).dropna()

        print(growth.tail(5))

        growth.plot(figsize=(14, 6)
                    , title=f'{self.country_} Added New Cases - full range'
                    , legend=True
                    , label="New Cases"
                    , style='.-')
        growth.rolling(30).mean().plot(grid=True, legend=True, label="30 days MA")
        plt.show()



        df_data = self.deaths_new_[60:].dropna()
        df_ma = self.deaths_new_[30:].rolling(30).mean().dropna()

        print("Deaths Per Day\n" + str(self.deaths_new_.tail()))
        
    def deaths_additions(self):
        plt.figure(figsize = (15,10))

        df = pd.DataFrame({"Daily Deaths Addition" :  self.deaths_new_}, index=self.deaths_new_.index)
        plt.figure(figsize = (15,10))

        print("Deaths Per Day\n" + str(df.tail()))
        df.plot(title = f'{self.country_} Daily Deaths Additions'
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkred"]
               )
        plt.show()
        df[-60:].plot(title = f'{self.country_} Daily Deaths Additions - last 60 days'
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkred"]
               )
        plt.show()

    def cases_additions(self):
        df = pd.DataFrame({"Daily Cases Addition" : self.confirmed_new_}, index=self.deaths_new_.index)
        print("New Cases Per Day\n" + str(df.tail()))
        df.plot(title = f"{self.country_} Daily Cases Addition"
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkblue"]
               )
        plt.show()

        df[-60:].plot(title = f"{self.country_} Daily Cases Addition - last 60 days"
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkblue"]
               )
        plt.show()

    def dynamics(self):
        df = pd.DataFrame({"Daily Deaths Addition (%)" : self.deaths_new_pcnt_
                              , "Daily Cases Addition (%)" : self.confirmed_new_pcnt_}
                          , index=self.deaths_new_pcnt_.index)['2020-03-01':]

        # df.plot(title = "COVID-19 Dynamics (%)"
        #         , grid = True
        #         , legend = True
        #         , style = '-o'
        #         , figsize=(14, 6)
        #         , color = ["darkred", "darkblue"]
        #        )

        # Last 90 days

        df = df[-90:]
        df.plot(title = f'{self.country_} COVID-19 Dynamics - last 90 days (%)'
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkred", "darkblue"]
               )
    
        

    def show(self):
        self.added_new_cases()
        self.deaths_additions()
        self.cases_additions()
        self.dynamics()
        

class USA_State_COVID19_Stats:
    def __init__(self, state: str):
        self.state_ = state 

    def show(self):
        cv_data = load_JHU_Data_USA(self.state_)
        confirmed_new = (cv_data.Confirmed - cv_data.Confirmed.shift(1)).dropna()
        dead_new = (cv_data.Dead - cv_data.Dead.shift(1)).dropna()

        plt.figure(figsize = (15,10))

        df = pd.DataFrame({"Daily Deaths Addition" :  dead_new}, index=dead_new.index)
        plt.figure(figsize = (15,10))

        print("Deaths Per Day\n" + str(df.tail()))
        df.plot(title = f"{self.state_} Daily Deaths Additions"
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkred"]
               )
        plt.show()
        df[-60:].plot(title = f"{self.state_} Daily Deaths Additions - last 60 days"
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkred"]
               )
        plt.show()

        df = pd.DataFrame({"Daily Cases Addition" : confirmed_new}, index=dead_new.index)
        print("New Cases Per Day\n" + str(df.tail()))
        df.plot(title = f"{self.state_} Daily Cases Addition"
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkblue"]
               )
        plt.show()

        df[-60:].plot(title = f"{self.state_} Daily Cases Addition - last 60 days"
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkblue"]
               )
        plt.show()
