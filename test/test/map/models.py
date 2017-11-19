from django.db import models

#priya added these imports on 11/19
import pandas as pd
import geopandas
import numpy as np
from geopandas.tools import sjoin
import folium
import googlemaps
from folium.plugins import MarkerCluster
from branca.colormap import linear
import datetime
# Create your models here.

class Predictions(models.Model):
    zcta = models.CharField(max_length=5)
    year = models.IntegerField()
    month = models.IntegerField()
    day_of_month = models.IntegerField()
    hour_of_day = models.IntegerField()
    day_of_year = models.IntegerField()
    week_of_year = models.IntegerField()
    day_of_week = models.IntegerField()
    is_weekend = models.BooleanField()
    call_counts = models.FloatField()

class Ambulance(models.Model):
    amb_id = models.IntegerField()
    LAT = models.FloatField()
    LONG = models.FloatField()
    AVAILABLE = models.IntegerField()
    time = models.DateTimeField(auto_now_add=True)

class EMS_Calls(models.Model):
    ems_id = models.IntegerField(primary_key=True)
    addr = models.CharField(max_length=200)
    LAT = models.FloatField()
    LONG = models.FloatField()
    time = models.DateTimeField()

class Current_predictions(models.Model):
    zcta = models.CharField(max_length=5)
    year = models.IntegerField()
    month = models.IntegerField()
    day_of_month = models.IntegerField()
    hour_of_day = models.IntegerField()
    day_of_year = models.IntegerField()
    week_of_year = models.IntegerField()
    day_of_week = models.IntegerField()
    is_weekend = models.BooleanField()
    call_counts = models.FloatField()

    def __str__(self):
        return self.zcta + "_" + str(self.call_counts)

class Current_ambulance(models.Model):
    amb_id = models.IntegerField(primary_key=True)
    LAT = models.FloatField()
    LONG = models.FloatField()
    AVAILABLE = models.IntegerField()

    def store_amb_record(self,):
        curr_amb = Current_ambulance.objects.all().values_list()
        for amb in curr_amb:
            t = Ambulance(amb_id=amb[0],LAT=amb[1],LONG=amb[2],AVAILABLE=amb[3])
            t.save()

    def update_amb_records(self,id_,lat_,long_,avail_):
        t = Current_ambulance.objects.get(amb_id=id_)
        t.LAT = lat_
        t.LONG = long_
        t.AVAILABLE = avail_
        t.save()


    def api_call(self,amb_coord,call_coord,dep_time,key,available_amb):
        gmaps = googlemaps.Client(key=key)
        result = gmaps.distance_matrix(amb_coord, call_coord, mode="driving", units="imperial", departure_time=dep_time)
        output_mat = pd.DataFrame()
        for idx, row in enumerate(result['rows']):
            row_mat = pd.DataFrame()
            mat = row['elements'][0]
            for key, val in mat.items():
                if key != 'status':
                    df = pd.DataFrame.from_dict(val, orient='index')
                    df = df.transpose()
                    df.columns = [key + "_" + c for c in df.columns]
                    if row_mat.empty:
                        row_mat = df
                    else:
                        row_mat = pd.concat([row_mat, df], axis=1)
            if output_mat.empty:
                output_mat = row_mat
            else:
                output_mat = output_mat.append(row_mat)
        output_mat.index = [amb for amb in available_amb.AMB_ID]
        
        chosen = output_mat.loc[output_mat.duration_in_traffic_value == min(output_mat.duration_in_traffic_value)].index[0]
        return chosen

    def dispatch_ambulance(self,api_key):
        ambulance = pd.DataFrame(list(Current_ambulance.objects.all().values()))
        available_amb = ambulance.loc[ambulance.AVAILABLE == 1]
        amb_coord = [(row[2], row[3]) for row in available_amb.itertuples()]

        #get current call
        current_call = Current_emscall.objects.all().values_list()[0]
        call_coord = [(current_call[2], current_call[3])]
        dep_time = current_call[4]
        result = self.api_call(amb_coord,call_coord,dep_time,api_key,available_amb)
        
        #update ambulance to table
        result = int(result)
        LAT = ambulance.LAT[ambulance.amb_id==result].tolist()[0]
        LONG = ambulance.LONG[ambulance.amb_id==result].tolist()[0]

        self.update_amb_records(result,LAT,LONG,0)

class Current_emscall(models.Model):
    addr = models.CharField(max_length=200)
    LAT = models.FloatField()
    LONG = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)	

    def __str__(self):
        return self.addr


    def get_coordinates(self,key, addr):
        """Runs google maps geocoding api to return lat/long coords
        for a list of addresses.
        key: string (API key)
        addr: list of strings (addresses)"""
        gmaps = googlemaps.Client(key=key)
        coords = []
        for ad in addr:
            geocode_result = gmaps.geocode(ad)
            lat_long = geocode_result[0]['geometry']['location']
            # Add tuple with lat & long to coords output
            coords.append((lat_long['lat'], lat_long['lng']))
        return coords

    def update_current_ems(self,address):
        curr_ems= Current_emscall.objects.all().values_list()
        for i in curr_ems:
            t = EMS_Calls(ems_id= i[0],addr=i[1],LAT=i[2],LONG=i[3],time=i[4])
            t.save()

        Current_emscall.objects.all().delete()

        coor = self.get_coordinates(key_code,address)

        p = Current_emscall(addr=address,LAT=coor[0][0],LONG=coor[0][1])
        p.save()


    #functions to add markers to map
    def add_ambmarker(self,smap,lat,long,amb_name):
        folium.Marker([lat, long], icon=folium.Icon(icon='plus',color='blue'),
                      popup="Amb #:" + str(amb_name)
                     ).add_to(smap)
        
    def used_ambmarker(self,smap,lat,long,amb_name):
        folium.Marker([lat, long], icon=folium.Icon(icon='plus',color='gray'),
                      popup="Amb #:" + str(amb_name)
                     ).add_to(smap)
        
    def add_emsmarker(self,smap,lat,long,event_id):
        folium.RegularPolygonMarker([lat, long], popup="EMS #: " + str(event_id),
                                    fill_color='red',number_of_sides=5,radius=10).add_to(smap)

    def create_map(self):  
        #geopandas
        geodata = geopandas.read_file('./map/templates/sf_zcta/sf_zcta.shp')
          
        #call in Current_predictions table values  
        t = pd.DataFrame(list(Current_predictions.objects.all().values()))


        geodata['ZCTA5CE10'] = geodata['ZCTA5CE10'].astype('int64')
        t['zcta'] = t['zcta'].astype('int64')
        gdf = geodata.merge(t,left_on='ZCTA5CE10' ,right_on='zcta')
        gdf1 = gdf
        gdf = gdf.set_index('ZCTA5CE10')['call_counts']
        gdf1 = gdf1.set_index('ZCTA5CE10')
        gdf1.crs={'init': 'epsg:4326'}
        
        #color scale
        colormap = linear.OrRd.scale(gdf1.call_counts.min(),gdf1.call_counts.max())
        
        #foliium
        sfmap = folium.Map([37.7556, -122.4399], zoom_start = 12)
        
        #plot zip codes and prob color grid
        folium.GeoJson(gdf1.to_json(),overlay=True,
            style_function=lambda feature: 
                   {'color': "black",
                   'weight':1.5,
                   'fillColor': colormap(gdf[int(feature['id'])])}
                  ).add_to(sfmap)
        folium.LayerControl().add_to(sfmap)
        
        #read in ambulance data, add markers
        
        ambulance = pd.DataFrame(list(Current_ambulance.objects.all().values()))
        
        for i in ambulance.values:
            if i[1] != 0:
                if i[0] == 1:
                    self.add_ambmarker(sfmap,i[1], i[2],i[3])

                else:
                    self.used_ambmarker(sfmap,i[1], i[2],i[3])

        #input ems event markers

        current_call = Current_emscall.objects.all().values_list() 
        for call in current_call:
            self.add_emsmarker(sfmap,call[2],call[3],call[0])

        sfmap.save('./map/templates/map.html')



