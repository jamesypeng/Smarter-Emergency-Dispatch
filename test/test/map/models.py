from django.db import models

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

class Current_emscall(models.Model):
    addr = models.CharField(max_length=200)
    LAT = models.FloatField()
    LONG = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)	

    def __str__(self):
        return self.addr


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
