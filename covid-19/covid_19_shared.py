import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import datetime

plt.rcParams.update({'figure.max_open_warning': 0})   # get rid of warning

def list_of_JHUD_US_states():
    conf_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
    df = pd.read_csv(conf_url)
    res = df["Province_State"]
    return res.unique()    

def list_of_USA_state_counties(state: str):
    conf_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
    df = pd.read_csv(conf_url)
    df.drop(df[ df["Province_State"] != state].index, inplace=True)
    res = df['Admin2']
 
    return res



class USA_Data:
    def __init__(self):
        conf_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
        deaths_url = "https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_US.csv"

        self.confirmed_ = pd.read_csv(conf_url)
        self.deaths_ = pd.read_csv(deaths_url)
        self.recovered_ = None
    
#------------------------------------------------------
def usa_state_data(state : str, usa_data = None):
    
    if usa_data is None:
        usa_data = USA_Data()
    confirmed = usa_data.confirmed_.copy()
    deaths = usa_data.deaths_.copy()
    


    for df in [deaths, confirmed]:
        # Filter Country
        df.drop(df[ df["Province_State"] != state].index, inplace=True)
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

def usa_state_county_data(state : str, county: str, usa_data = None):
    
    if usa_data is None:
        usa_data = USA_Data()
    confirmed = usa_data.confirmed_.copy()
    deaths = usa_data.deaths_.copy()
    


    for df in [deaths, confirmed]:
        # Filter Country
        df.drop(df[ df["Province_State"] != state].index, inplace=True)
        df.drop(df[ df["Admin2"] != county].index, inplace=True)
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



class Global_Data:
    def __init__(self):
        conf_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
        rcvrd_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv"
        deaths_url="https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"

        self.confirmed_ = pd.read_csv(conf_url)
        self.deaths_ = pd.read_csv(deaths_url)
        self.recovered_ = pd.read_csv(rcvrd_url)


# def load_JHU_Data_global(st : str):
def country_data(country : str, global_data = None):
    if global_data is None:
        global_data = Global_Data()

    confirmed = global_data.confirmed_.copy()
    deaths = global_data.deaths_.copy()
    recs = global_data.recovered_.copy()
    
    for df in [deaths, confirmed, recs]:
        # Filter Country
        df.drop(df[ df["Country/Region"] != country].index, inplace=True)
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

def USA_population():
    url = "http://www2.census.gov/programs-surveys/popest/datasets/2010-2019/national/totals/nst-est2019-alldata.csv"

    df = pd.read_csv(url)
    df = df[df.STATE != 0]
    df = pd.DataFrame({"Name" : df.NAME, "Population" : df.CENSUS2010POP}).set_index("Name")
    return df.Population


#---------------------------------------------------------------------


class COVID_19_Stats:
    def __init__(self, region: str, region_data : pd.DataFrame):
        self.region_ = region
        self.cv_data_ = region_data
        
        self.confirmed_new_ = (self.cv_data_.Confirmed - self.cv_data_.Confirmed.shift(1)).dropna()
        self.deaths_new_ = (self.cv_data_.Dead - self.cv_data_.Dead.shift(1)).dropna()
        def growth_pcnt(ser): 
            return (ser - ser.shift(1)) / ser * 100
        self.deaths_new_pcnt_ = growth_pcnt(self.cv_data_.Dead)
        self.confirmed_new_pcnt_ = growth_pcnt(self.cv_data_.Confirmed)

       
    def added_new_cases(self):
        if "Recovered" not in self.cv_data_:
            return
        self.recovered_new_ = (self.cv_data_.Recovered - self.cv_data_.Recovered.shift(1)).dropna()

        growth = pd.Series((self.confirmed_new_ - (self.deaths_new_ + self.recovered_new_)).array
                           , index=self.cv_data_.index[1:]).dropna()

        print(growth.tail(5))

        growth.plot(figsize=(14, 6)
                    , title=f'{self.region_} Added New Cases - full range'
                    , legend=True
                    , label="New Cases"
                    , style='.-')
        growth.rolling(30).mean().plot(grid=True, legend=True, label="30 days MA")
        plt.show()


        df_data = self.deaths_new_[60:].dropna()
        df_ma = self.deaths_new_[30:].rolling(30).mean().dropna()

#         print("Deaths Per Day\n" + str(self.deaths_new_.tail(8)))

    def deaths_additions(self):
        plt.figure(figsize = (15,10))

        df = pd.DataFrame({"Daily Deaths Addition" :  self.deaths_new_}, index=self.deaths_new_.index)
        plt.figure(figsize = (15,10))

        print("Deaths Per Day\n" + str(df.tail(8)))
        df.plot(title = f'{self.region_} Daily Deaths Additions'
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkred"]
               )
        plt.show()
        df[-60:].plot(title = f'{self.region_} Daily Deaths Additions - last 60 days'
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkred"]
               )
        plt.show()
        
        # yesterday data was the last recieved - base weekly data on that dow
        dow = (datetime.datetime.now() - datetime.timedelta(1)).strftime("%a")
        resample_fmt = f"W-{dow}"
        for df2 in (df, df[-120:]):
            df2 = pd.DataFrame({"Weekly Deaths" : df2.assign(Date=df2.index).resample(resample_fmt)["Daily Deaths Addition"].sum()})
            df2.plot(title = f'{self.region_} Weekly Deaths - last {len(df2.index)} weeks'
                    , kind = 'bar'
                    , grid = True
                    , legend = True
                    , figsize=(14, 6)
                    , color = ["darkmagenta"]
                   )
            plt.show()


    def cases_additions(self):
        df = pd.DataFrame({"Daily Cases Addition" : self.confirmed_new_}, index=self.deaths_new_.index)
        print("New Cases Per Day\n" + str(df.tail(8)))
        df.plot(title = f"{self.region_} Daily Cases Addition"
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkblue"]
               )
        plt.show()

        df[-60:].plot(title = f"{self.region_} Daily Cases Addition - last 60 days"
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

        # Last N days
        days = 90
        df[-days:].plot(title = f'{self.region_} COVID-19 Dynamics - last {days} days (%)'
                , grid = True
                , legend = True
                , style = '-o'
                , figsize=(14, 6)
                , color = ["darkred", "darkblue"]
               )
    
        

    def show(self):
#         self.added_new_cases()
        self.deaths_additions()
        self.cases_additions()
        self.dynamics()

def Country_COVID19_Stats(country: str):
    return COVID_19_Stats(country, country_data(country))

def USA_State_COVID19_Stats(state : str):
    return COVID_19_Stats(state, usa_state_data(state))

def USA_State_County_COVID19_Stats(state : str, county: str):
    return COVID_19_Stats(f"{state}:{county}", usa_state_county_data(state, county))


def get_all_states_stats(verbose : bool = True):
    if (verbose):
        print("Getting population...")
    pop = USA_population()

    if (verbose): print("Getting list of states...")
    states = list_of_JHUD_US_states()

    if (verbose): print("Getting USA data...")
    us_data = USA_Data()

    if (verbose): print("%-30s%-20s%-10s%-20s%-10s%-16s" 
          % ("State", "Population", "New Conf.", "Conf./Popul.(%)"
             , "New Death", "Death/Popul.(%)")
         )
    df = pd.DataFrame()
    for state in states:
        if state in pop:

            stats = COVID_19_Stats(state, usa_state_data(state, us_data))
            state_pop = int(pop[state])
            stats.pops_ratio_conf_ = stats.cv_data_.Confirmed * 100 / state_pop
            stats.pops_ratio_deaths_ = stats.cv_data_.Dead * 100 / state_pop
            if (verbose): print("%-30s%-20s%-10d%-20f%-10d%-16f" 
                  % (state
                     , state_pop
                        , int(stats.confirmed_new_[-1])
                        , stats.pops_ratio_conf_[-1]
                        , int(stats.deaths_new_[-1])
                        , stats.pops_ratio_deaths_[-1]
                       )
                 )
            df = df.append(pd.DataFrame({"State" : [state], "Statistics": [stats], "Population" : [state_pop]}))
    #         stats.dynamics()

    return df.set_index("State")