#run this in the django project folder where manage.py is
#./manage.py shell < load_data.py

import csv
from map.models import Current_ambulance, Predictions


amb_file_path = "/Users/priyagupta/desktop/mids/w210/project/Smarter-Emergency-Dispatch/together/ambulance_loc2.csv"
ems_preds_path = "/Users/priyagupta/desktop/mids/w210/project/Smarter-Emergency-Dispatch/together/ems_calls_predict_mod2.csv"

reader_amb = csv.reader(open(amb_file_path))

reader_ems = csv.reader(open(ems_preds_path))

next(reader_amb)
next(reader_ems)
for line in reader_amb:
     t = Current_ambulance(amb_id=line[0], LAT=line[1], LONG=line[2],AVAILABLE=line[3])
     t.save()

for line2 in reader_ems:
     t2 = Predictions(zcta=line2[0], year=line2[1], month=line2[2],day_of_month=line2[3],
     	hour_of_day=line2[4], day_of_year=line2[5],week_of_year=line2[6],day_of_week=line2[7],
     	is_weekend=line2[8],Call_counts=line2[9])
     t2.save()
