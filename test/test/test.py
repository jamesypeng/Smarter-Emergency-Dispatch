from map.models import Current_ambulance, Predictions,Current_predictions
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


from map.models import Current_ambulance, Predictions,Current_predictions,Current_emscall,Ambulance, EMS_Calls


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
t2 = Current_emscall(addr='110 sutter street',LAT=00.0,LONG=00.0,time=str(datetime.now()))


