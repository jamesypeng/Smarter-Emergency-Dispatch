import numpy as np
import pandas as pd
import sys
import geopandas
from pandas.tseries.holiday import USFederalHolidayCalendar

'''
Processes a csv of SF Fire EMS data and returns csv ready for model training.
Currently aggregates by the hour for each Zip Code Tabulation Area in SF
County.

INPUTS: Arguments are
1) Path to raw SF Fire data csv
2) Path to save resulting training data
3) Path to shape file for SF County ZCTAs
'''

####### SETUP #######
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

# default paths for raw and clean data files
data_path = './Fire_Department_Calls_for_Service.csv'
clean_save_path = './clean_sf_fire.csv'
zcta_shp_path = './sf_zcta/sf_zcta.shp'

# setting paths if arguments were provided.
# first arg is raw data location, second is save location for cleaned data
if len(sys.argv) > 1:
    data_path = sys.argv[1]
if len(sys.argv) > 2:
    clean_save_path = sys.argv[2]
if len(sys.argv) > 3:
    zcta_shp_path = sys.argv[3]

####### IMPORTING AND CLEANING #######
# loading and sorting raw data
data_types={'Incident Number':np.int64, 'Call Type':str, 'On Scene DtTm':str,
            'Received DtTm': str, 'Zipcode of Incident':np.float64, 'Unit Type':str,
            'Unit sequence in call dispatch':np.float64,'Location':str, 'RowID':str}
date_cols = ['Received DtTm']
df = pd.read_csv(data_path, dtype=data_types, usecols=data_types.keys(), parse_dates=date_cols, na_values='None')

# Removing records without an on-scene time
df = df[~pd.isnull(df['On Scene DtTm'])]

# Filtering down to the top three incident call types and medic/private units
call_type_keep = ['Medical Incident', 'Traffic Collision', 'Structure Fire']
unit_type_keep = ['MEDIC','PRIVATE']
df = df[(df['Call Type'].isin(call_type_keep)) & (df['Unit Type'].isin(unit_type_keep))]

####### ADDING DATETIME FEATURES #######
# Splitting lat/lon field in to two numeric fields
df['lat'], df['lon'] = zip(*df.Location.map(lambda x: [float(val) for val in x.strip('()').split(',')]))

# Getting list of US Federal Holidays (includes observed)
holidays = USFederalHolidayCalendar().holidays(start='2000-01-01', end='2018-01-01')

# Splitting received datetime into separate parts, including flag for weekends
df['year'], df['month'], df['day_of_month'], df['hour_of_day'], df['day_of_year'], df['week_of_year'], df['day_of_week'], df['is_weekend'],  = \
    zip(*df['Received DtTm'].map(lambda val: [val.year, val.month, val.day, val.hour, val.dayofyear, val.week, val.weekday(), val.weekday() in [5,6]]))

# Adding flag for holidays. Includes days that holidays are observed.
df['is_holiday'] = df['Received DtTm'].isin(holidays)

####### BUILDING REGION FIELD #######
# Loading ZCTA shape file with geopandas
gdf = geopandas.read_file(zcta_shp_path)

# Finding ZCTA for each point
df['zcta'] = df.apply(lambda row: get_zcta(geopandas.geoseries.Point(row.lon, row.lat)), axis=1)

# We need to remove records that are not in a ZCTA. These are likely border cases where a unit was dispatched
# outside of SF for some reason. Most of these cases also have no Zip in the data.
df = df[~pd.isnull(df['zcta'])]

# Setting region to be the ZCTA. This is to keep the region field generic in case we choose to use some other kind
# of region mapping in the future.
df['region'] = df.zcta

####### AGGREGATING BY REGION AND TIME #######
# filtering for fields that will be retained in training set
keep_fields = ['year', 'month', 'day_of_month', 'hour_of_day', 'day_of_year',
               'week_of_year', 'day_of_week', 'is_weekend', 'is_holiday',
               'region']

df = df[keep_fields]

# creating a unique region and time field for grouping on an hourly basis in each region
df['region_time'] = df.apply(lambda row: '-'.join([str(row.region), str(row.year), str(row.month), str(row.day_of_month), str(row.hour_of_day)]), axis=1)

# Creating dictionary of the number of dispatches in each region/hour tuple
# The 'year' field is arbitrary, I just needed it to return a series of counts instead of a dataframe
dispatch_counts = dict(df.groupby(['region_time'])['year'].count())

# Dropping duplicate region_hour rows
df.drop_duplicates(subset='region_time', inplace=True)

# assigning dispatch counts
df['dispatch_count'] = df.apply(lambda row: dispatch_counts[row.region_time], axis=1)

# Saving to csv
df.to_csv(clean_save_path)
