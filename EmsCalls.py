import sys,os, re, itertools, datetime
import collections

import numpy as np
import pandas as pd
import datetime
import importlib
import scipy
import sqlite3
from sqlalchemy import create_engine
from sodapy import Socrata
from pandas.tseries.holiday import USFederalHolidayCalendar
import geopandas

from IPython.display import display, HTML

DATA_DIR = './data'

class EmsCalls:
    def __init__(self):
        self._datafile = None
        self._df = None
        
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass
    
    def to_sqlite3(self, sqlite3_file = "ems_calls.sl3", chunksize = 100000):
        sl3_engine = create_engine('sqlite:///{file}'.format(file=sqlite3_file))
        self._df.to_sql('ems_call', sl3_engine, 
                      chunksize = chunksize,
                      if_exists='append')      
    
    def read_data(self, file, nrows = None, content_type = 'csv', ):

        
        self._datafile  = os.path.join(DATA_DIR, file)
    
        self._df = pd.read_csv(self._datafile, 
                               dtype = {'Zipcode of Incident': str},
                                sep = '\t',
                                nrows = nrows # pass None to read the whole file 
                                )        
    
    
    def stream_data(self, nrows):
        
        
        # Unauthenticated client only works with public data sets. Note 'None'
        # in place of application token, and no username or password:
        self._webclient = Socrata("data.sfgov.org", "v5742hH1aWm5HDSi7MgeGPbC0")
        
        # Example authenticated client (needed for non-public datasets):
        # client = Socrata(data.sfgov.org,
        #                  MyAppToken,
        #                  userame="user@example.com",
        #                  password="AFakePassword")
        
        # First 2000 results, returned as JSON from API / converted to Python list of
        # dictionaries by sodapy.
        results = self._webclient.get("enhu-st7v", limit=nrows, content_type='json')
        
        # Convert to pandas DataFrame
        self._df = pd.DataFrame.from_records(results)
        
        
        self._webclient.close()       
        
        self.describe()       
        
        
    def describe(self, n_samples = 5, describe_all=False, print_value=False):
        
        # data type of columns
        display(self._df.info())
        
        # index
        display(self._df.index)
        
        
        # return pandas.Index
        display(self._df.columns)
        
        # each row, return array[array]
        if print_value:
            display(self._df.values)
        
        # a tuple representing the dimensionality of df
        display(self._df.shape)        
        
        # head, tail, and samples
        display(self._df.head(n_samples))
        display(self._df.tail(n_samples))
        display(self._df.sample(n=n_samples))
        
        # then decribe
        
        if describe_all == True:
            display(self._df.describe(include='all'))
        
        
        # print category
        for c in list(self._df.select_dtypes(include=['category']).columns):       
            print('{} ({}): {}\n'.format(c, 
                                       len(self._df[c].cat.categories), 
                                       self._df[c].cat.categories))        
        
        # print unique values and check if the  column contains NA values 
        for c in self._df.columns:
            print("{} ({}): {}".format(c, 
                                       self._df[c].nunique(), 
                                       np.any(self._df[c].isnull() )))        
        
    def clean(self, sort=True, zip_na='000000'):
        '''
        Paramters:
            zip_na: value if ZIP Code is NA
            sort: sort self._df, by ['Call_Number','Unit_sequence_in_call_dispatch']
        
        '''
        # Replace spaces in column names with _
        print("Replace spaces in column names with _ ")
        self._df.columns = [x.strip().replace(' ', '_') for x in self._df.columns]
        

        # Removing records without an on-scene time
        print('remove records without on-scene_time')
        self._df = self._df[~pd.isnull(self._df['On_Scene_DtTm'])]

        # Filtering down to the top three incident call types and medic/private units
        call_type_keep = ['Medical Incident', 'Traffic Collision', 'Structure Fire']
        unit_type_keep = ['MEDIC','PRIVATE']
        print('Keep Call Type = {}'.format(call_type_keep))
        print('Keep Unit Type = {}'.format(unit_type_keep))

        self._df = self._df[(self._df['Call_Type'].isin(call_type_keep)) & 
                            (self._df['Unit_Type'].isin(unit_type_keep))]

        # Convert to datetime format
        print("Convert dattime strings to datetime object")
        datetime_cols = {'Call_Date' : '%m/%d/%Y', 
                         'Watch_Date': '%m/%d/%Y', 
                         'Received_DtTm': '%m/%d/%Y %I:%M:%S %p', 
                         'Entry_DtTm':    '%m/%d/%Y %I:%M:%S %p', 
                         'Dispatch_DtTm': '%m/%d/%Y %I:%M:%S %p', 
                         'Response_DtTm': '%m/%d/%Y %I:%M:%S %p', 
                         'On_Scene_DtTm': '%m/%d/%Y %I:%M:%S %p', 
                         'Transport_DtTm':'%m/%d/%Y %I:%M:%S %p', 
                         'Hospital_DtTm': '%m/%d/%Y %I:%M:%S %p', 
                         'Available_DtTm':'%m/%d/%Y %I:%M:%S %p'}
        
        def to_datetime(df, columns):
            for col,fmt in columns.items():
                print( "Convert {} to datetime object by the fmt {}".format(col, fmt))
                df[col] = pd.to_datetime(df[col], format = fmt)
        
        to_datetime(self._df, datetime_cols)        
        
        print("Extract time features - year, month, day_of_month, hour_of_day, day_of_year, week_of_year")
        
        # self._df['Received_Hour'] = self._df['Received_DtTm'].map( lambda x: x.hour)
        # self._df['Received_Min'] = self._df['Received_DtTm'].map( lambda x: x.minute)
        # self._df['Received_Year'] = self._df['Received_DtTm'].map( lambda x: x.year)
        # self._df['Received_Month'] = self._df['Received_DtTm'].map( lambda x: x.month)
        # self._df['Received_Day'] = self._df['Received_DtTm'].map( lambda x: x.day)
        # self._df['Received_Weekday'] = self._df['Received_DtTm'].map( lambda x: x.weekday()) 
        
        self._df['year'], self._df['month'], self._df['day_of_month'], \
            self._df['hour_of_day'], self._df['day_of_year'], \
            self._df['week_of_year'],self._df['day_of_week'], self._df['is_weekend'] = \
            zip(*self._df['Received_DtTm'].map(lambda val: [val.year, val.month, val.day, val.hour, \
                                                        val.dayofyear, val.week, val.weekday(), \
                                                        val.weekday() in [5,6]]))

        # Adding flag for holidays. Includes days that holidays are observed.
        # Getting list of US Federal Holidays (includes observed)
        holidays = USFederalHolidayCalendar().holidays(start='2000-01-01', end='2018-01-01')
        self._df['is_holiday'] = self._df['Received_DtTm'].isin(holidays)

        self._df['Call_Number'] = self._df['Call_Number'].astype(int)
        self._df['Incident_Number'] = self._df['Incident_Number'].astype(int)        
        


        # Convery ZIP code to string format
        self._df['Zipcode_of_Incident'] = self._df['Zipcode_of_Incident'].map(
            lambda x: str(int(x)) if pd.notnull(x) else zip_na)        
        
        print('extract GPS coordinates')
        def extract_coord(df, col_from, col_to = ['lat', 'lon']):
            '''
                col_coord: column which stores GPS coordinates information, in the format of  "(lat, lng)"
            
            '''
            df[col_to] = df[col_from].str.extract('(?P<lat>[-+]?[0-9]*\.[0-9]+|[0-9]+),\s+(?P<lng>[-+]?[0-9]*\.[0-9]+|[0-9]+)',
                                         expand=True)
            return df
        
        self._df = extract_coord(self._df, 'Location')

        # Get ZCTA basedo n lat and lng
        def get_zcta(point):
            '''
            Takes a geopandas/shapely longitude/latitude point object and returns
            the US Census Zip Code Tabulation Area containing it.
            INPUT: Point must have longitude first, since it expects an x,y coordinate
            OUTPUT: The ZCTA code, or None if not found in San Francisco County
            '''
            zcta = gdf.ZCTA5CE10[gdf.geometry.contains(point)]
            if len(zcta) > 0:
                return zcta.values[0]
            else:
                return None

        ZCTA_SHP_PATH = './sf_zcta/sf_zcta.shp'

        gdf = geopandas.read_file(ZCTA_SHP_PATH)

        # Finding ZCTA for each point
        self._df['zcta'] = self._df.apply(lambda row: get_zcta(geopandas.geoseries.Point(float(row.lon),
                                                                                         float(row.lat))), axis=1)

        
        print('Convert to category')
        def to_category(df, columns = None):
            for c in columns:
                df[c] = df[c].astype('category')
                
        cols =  ['Call_Number', 'Call_Type', 'Call_Final_Disposition', 'Battalion', 'Station_Area', 'Box', 
                 'Original_Priority', 'Priority', 'Final_Priority',
                 'Zipcode_of_Incident', 'Unit_ID', 'Unit_Type', 
                 'Fire_Prevention_District', 'Supervisor_District', 'Incident_Number',
                 'Neighborhooods_-_Analysis_Boundaries', 'Call_Type_Group',
                 'year', 'month', 'day_of_month',
                 'hour_of_day', 'day_of_year', 'week_of_year', 
                 'day_of_week', 'is_weekend'
                ]  
        
        to_category(self._df, cols)     
        
        if sort:
            self._df.sort_values(['Call_Number','Unit_sequence_in_call_dispatch'], ascending=[True,True], inplace = True)
    
    def EDA(self):
        
        # pivot table
        result = self._df.pivot_table( index = 'Zipcode_of_Incident', 
                                       columns = ["Supervisor_District", "Final_Priority"],
                                       values= "Call_Number",
                                       aggfunc = "nunique")
        display(result)
        
        
        # pivot 2
        result = self._df.pivot_table( index = ['Zipcode_of_Incident'], aggfunc=('nunique','count'))        
        display(result)
        
        
        # print the earliest and latest timestamp
        for c in list(self._df.select_dtypes(include=['datetime']).columns):
            print("{} \t: oldest: {} | latest: {}".format(c,
                                                                        min(self._df[c]), 
                                                                        max(self._df[c])))
        
        top_k = 10
        for c in list(self._df.select_dtypes(include=['category']).columns): 
            if c != 'Call_Number':
                print('-----Top {}: {}----------'.format(top_k,c))
                display(self._df[c].value_counts()[:top_k])
                display(self._df.pivot_table(index = c, 
                                             columns = 'Call_Number', 
                                             aggfunc= 'nunique'))
        
             
    def resample(self, rule = '1H'):
        '''
        Resample the timestamp data into 1 hour interval
        
        
        '''
        grp = self._df.groupby('Call_Number', as_index=False)
        self._grp = grp
        
        # possible aggfunc:
        #   'count': dont not include NA
        #   'size' : include NA
        #   'nunique' : count distinct, does not include NA
        #   'mean', 'sum', 'sd', 'first', 'last'
        # ems_calls._df2['cnt_incident'] = grp['Incident_Number'].agg('count')
        agg_dict = {'Unit_ID': 'nunique',
                    'Incident_Number': ['count','nunique'],
                    'Call_Type': 'nunique',
                    'Call_Date': ['min', 'max', 'nunique'],
                    'Watch_Date': ['min', 'max', 'nunique'],
                    'Entry_DtTm': ['min', 'max', 'nunique'],
                    'Hospital_DtTm': ['min', 'max', 'nunique'],
                    'Available_DtTm': ['min', 'max', 'nunique'],
                    'Transport_DtTm': ['min', 'max', 'nunique'],
                    'On_Scene_DtTm': ['min', 'max', 'nunique'],
                    'Received_DtTm': ['min', 'max', 'nunique'],
                    'Dispatch_DtTm': ['min', 'max', 'nunique'],
                    'Response_DtTm': ['min', 'max', 'nunique'],
                    'Call_Final_Disposition': ['first', 'nunique'],
                    'Address': ['first', 'nunique'],
                    'Zipcode_of_Incident': ['first', 'nunique'],
                    'Battalion': ['first', 'nunique'],
                    'Station_Area' : ['first', 'nunique'],
                    'Box': ['first', 'nunique'],
                    'Original_Priority' : ['first', 'nunique'],
                    'Priority': ['first', 'nunique'],
                    'Final_Priority': ['first', 'nunique'],
                    'ALS_Unit': ['first', 'nunique'], 
                    'Call_Type_Group': ['first', 'nunique'],
                    'Final_Priority': ['first', 'nunique'],            
                    'Number_of_Alarms' : ['first', 'nunique','mean'],
                    'Unit_Type': ['first', 'nunique'],
                    'Unit_sequence_in_call_dispatch': ['max','nunique'],          
                    'Fire_Prevention_District': ['first', 'nunique'],
                    'Supervisor_District': ['first', 'nunique'],          
                    'Neighborhooods_-_Analysis_Boundaries' : ['first', 'nunique'],                        
                    'Location' : ['first', 'nunique'],
                    'latitude' : ['first'],
                    'longitude' : ['first']
                    }
        self._df2 = self._grp.agg(agg_dict)
        

        # after the aggregation, the column is two level hierarchy index
        # For convenience, I rename the column into single level
        #ems_calls._df2.columns        
        
        new_col_index = []
        for c in self._df2.columns.values:    
            # if the 2nd level name is not ''
            if len(c[1]) > 0 : 
                new_col_index.append("_".join(c))
            else: 
                new_col_index.append(c[0])
        
        self._df2.columns = new_col_index     
        
        display(self._df2.head())
        display(self._df2.tail())
        display(self._df2.sample(n=5))        
        
        
        #ts = ('Received_DtTm', 'min')
        #zip_code = ('Zipcode_of_Incident', 'first')
        #ressample_dict = {
        #    ('Call_Number','') : ['nunique']
        #    }
        ts = 'Received_DtTm_min'
        zip_code = 'Zipcode_of_Incident_first'
        ressample_dict = {'Call_Number': lambda x: x.nunique(), 
                          'Box_nunique': lambda x: (x.nunique(),x.count()),
                          'Unit_sequence_in_call_dispatch_max': np.sum,
                          'Number_of_Alarms_mean' : np.sum}      
        
        #ems_resampled = self._df2.set_index(ts_col)
        #ems_resampled.head()
        #ems_resampled.columns
        
        self._resampled = self._df2.set_index(ts).groupby([zip_code]).resample('1H').agg(ressample_dict)        
        
        display(self._resampled.head())
        display(self._resampled.tail())
        display(self._resampled.sample(n=5))          
        
    def clean_addr(self):

        Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'pos'])
        
        def tokenize(code):
            keywords = {'BLOCK', 'ST', 'AV', 'AVE', 'TER', 'TR', 'CT','BLVD', 'RD' }
            token_specification = [
                ('NUMBER',  r'\d+(\.\d*)?'),  # Integer or decimal number
                ('ID',      r'[A-Za-z/]+'),   # Identifiers
                ('NEWLINE', r'\n'),           # Line endings
                ('STOP',    r'of'),           # stopwords, of 
                ('BLOCK',   r'block'),        # 'word' block
                ('SEMICOL', r'[:]'),
                ('PUNC',    r'[@\.+\-*,]'),   # punctuations
                ('SKIP',    r'[ \t]+'),       # Skip over spaces and tabs
                ('MISMATCH',r'.'),            # Any other character
            ]
                        
            tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
            line_num = 1
            line_start = 0
            for mo in re.finditer(tok_regex, code, re.IGNORECASE):
                kind = mo.lastgroup
                value = mo.group(kind)
                if kind == 'NEWLINE':
                    line_start = mo.end()
                    line_num += 1
                elif kind == 'SKIP':
                    pass
                elif kind == 'MISMATCH':
                    raise RuntimeError('%r unexpected on line %d' % (value, line_num))
                else:
                    if kind == 'ID' and value in keywords:
                        kind = value
                    pos = mo.start() - line_start
                    yield Token(kind, value, line_num, pos)
        
            
        address = "1000 Block of LARKIN ST"
        for token in tokenize(address):
            print(token)        
    
                 
        
        
        
        pass
        
        
#==============================================================================
# Class Test
#==============================================================================
if __name__ == '__main__':

    # Test Parent
    with EmsCalls() as ems_calls:
        
        ems_calls.clean_addr()
        
        ems_calls.read_data(file='Fire_Department_Calls_for_Service.tsv', nrows=10000)
    
        #ems_calls.describe()
        ems_calls.clean()
    
        #ems_calls.EDA()
        
        ems_calls.resample()
    
    
    