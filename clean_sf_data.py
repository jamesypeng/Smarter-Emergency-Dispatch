import numpy as np
import pandas as pd
import sys
from pandas.tseries.holiday import USFederalHolidayCalendar

# default paths for raw and clean data files
data_path = './Fire_Department_Calls_for_Service.csv'
clean_save_path = './clean_sf_fire.csv'

# setting paths if arguments were provided.
# first arg is raw data location, second is save location for cleaned data
if len(sys.argv) > 1:
    data_path = sys.argv[1]
if len(sys.argv) > 2:
    clean_save_path = sys.argv[2]

# loading and sorting raw data
df = pd.read_csv(data_path)
df.sort_values('Incident Number', inplace=True)

# Removing unwanted fields
unwanted_fields = ['Watch Date', 'Battalion', 'Station Area', 'Box',
                    'Call Type Group', 'Number of Alarms',
                    'Fire Prevention District', 'Supervisor District']
keep_fields = [field for field in df.columns if field not in unwanted_fields]
df = df[keep_fields]

# Removing records without an on-scene time
df = df[~pd.isnull(df['On Scene DtTm'])]

# Filtering down to the top three incident call types
df = df[df['Call Type'].isin(['Medical Incident', 'Traffic Collision',
                                'Structure Fire'])]

# Filtering down to only Medic and Private unit types
df = df[df['Unit Type'].isin(['MEDIC','PRIVATE'])]

#### Adding useful fields ####
# Splitting lat/lon field in to two numeric fields
df['lat'], df['lon'] = zip(*df.Location.map(lambda x: [float(val) for val in x.strip('()').split(',')]))

# Converting call date to pandas datetime objects for easy manipulation
df['Call Date'] = pd.to_datetime(df['Call Date'])

# Getting list of US Federal Holidays (includes observed)
holidays = USFederalHolidayCalendar().holidays(start='2000-01-01', end='2018-01-01')

# Adding holiday flag
df['is_holiday'] = df['Call Date'].isin(holidays)

# Splitting call date into separate parts, including flag for weekends
df['year'], df['month'], df['day_of_month'], df['day_of_year'], df['week_of_year'], df['day_of_week'], df['is_weekend'] = \
    zip(*df['Call Date'].map(lambda val: [val.year, val.month, val.day, val.dayofyear, val.week, val.weekday(), val.weekday() in [5,6]]))

# Saving to csv
