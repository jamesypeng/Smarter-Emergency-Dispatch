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