from map.models import Current_ambulance, Predictions,Current_predictions,Current_emscall,Ambulance, EMS_Calls


import datetime

month = datetime.datetime.now().month
day = datetime.datetime.now().day
hour = datetime.datetime.now().hour
year = datetime.datetime.now().year

t = Predictions.objects.filter(year=year,month=month,day_of_month=day,hour_of_day=hour).values_list()


Current_predictions.objects.all().delete()

for line in t:
    t2 = Current_predictions(zcta=line[1], year=line[2], month=line[3],day_of_month=line[4],
     	hour_of_day=line[5], day_of_year=line[6],week_of_year=line[7],day_of_week=line[8],
     	is_weekend=line[9],call_counts=line[10])
    t2.save()



def store_amb_record():
	curr_amb = Current_ambulance.objects.all().values_list()
	for amb in curr_amb:
		t = Ambulance(amb_id=amb[0],LAT=amb[1],LONG=amb[2],AVAILABLE=amb[3])
		t.save()

def update_amb_records(id_,lat_,long_,avail_):
	t = Current_ambulance.objects.get(amb_id=id_)
	t.LAT = lat_
	t.LONG = long_
	t.AVAILABLE = avail_
	t.save()


def get_coordinates(key, addr):
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

def update_current_ems(address):
	curr_ems= Current_emscall.objects.all().values_list()
	for i in curr_ems:
		t = EMS_Calls(ems_id= i[0],addr=i[1],LAT=i[2],LONG=i[3],time=i[4])
		t.save()

	Current_emscall.objects.all().delete()

	coor = self.get_coordinates(key_code,address)

	p = Current_emscall(addr=address,LAT=coor[0][0],LONG=coor[0][1])
	p.save()



#for testing
t2 = Current_emscall(addr='110 sutter street',LAT=37.784172,LONG=-122.401558)


def add_ambmarker(smap,lat,long,amb_name):
    folium.Marker([lat, long], icon=folium.Icon(icon='plus',color='blue'),
                  popup="Amb #:" + str(amb_name)
                 ).add_to(smap)
    
def used_ambmarker(smap,lat,long,amb_name):
    folium.Marker([lat, long], icon=folium.Icon(icon='plus',color='gray'),
                  popup="Amb #:" + str(amb_name)
                 ).add_to(smap)
    
def add_emsmarker(smap,lat,long,event_id):
    folium.RegularPolygonMarker([lat, long], popup="EMS #: " + str(event_id),
                                fill_color='red',number_of_sides=5,radius=10).add_to(smap)


def create_map():  
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



    sfmap.save('./map/templates/map_test.html')
    return sfmap





def dispatch_ambulance(api_key):
    ambulance = pd.DataFrame(list(Current_ambulance.objects.all().values()))
    available_amb = ambulance.loc[ambulance.AVAILABLE == 1]
    amb_coord = [(row[2], row[3]) for row in available_amb.itertuples()]

    #get current call
    current_call = Current_emscall.objects.all().values_list()[0]
    call_coord = [(current_call[2], current_call[3])]
    dep_time = current_call[4]
    result = api_call(amb_coord,call_coord,dep_time,api_key,available_amb)
    
    #update ambulance to table
    result = int(result)
    LAT = ambulance.LAT[ambulance.amb_id==result].tolist()[0]
    LONG = ambulance.LONG[ambulance.amb_id==result].tolist()[0]

    self.update_amb_records(result,LAT,LONG,0)



def api_call(amb_coord,call_coord,dep_time,key,available_amb):
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



def update_amb_locs(self):
    ambfile = pd.DataFrame(list(Current_ambulance.objects.all().values()))
    predsfile = pd.DataFrame(list(Current_predictions.objects.all().values()))

    new_amb_locations = model_2_funcs.update_ambulance_assignments(amb_status_file_path=ambfile,
                                                               shape_file_path='./map/templates/sf_zcta/sf_zcta.shp',
                                                               predictions_file_path=predsfile,
                                                               results_file_path=None,
                                                               shape_region_id_col = 'ZCTA5CE10')


    for ind, row in new_amb_locations:
        self.update_amb_records(ind,row[1],row[2],row[0])








