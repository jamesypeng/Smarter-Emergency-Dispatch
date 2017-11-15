#must start rabit server and celery worker for scheduled jobs
#rabbitmq-server
#python3 manage.py celery worker --loglevel=info

from __future__ import absolute_import, unicode_literals
from celery import task
from celery.task.schedules import crontab
from celery.decorators import periodic_task
import datetime
from map.models import Current_ambulance,Current_predictions, Predictions

@periodic_task(run_every=crontab(minute=0, hour='*/1'))

#use task for testing
#@task()
def get_current_preds():
   month = datetime.datetime.now().month
   day = datetime.datetime.now().day
   hour = datetime.datetime.now().hour
   year = datetime.datetime.now().year
   
   #clear our current_predictions tables
   Current_predictions.objects.all().delete()

   #filter the predictions tables
   t = Predictions.objects.filter(year=year,month=month,day_of_month=day,hour_of_day=hour).values_list()

   #fill up current predictions table
   for line in t:
    t2 = Current_predictions(zcta=line[1], year=line[2], month=line[3],day_of_month=line[4],
     	hour_of_day=line[5], day_of_year=line[6],week_of_year=line[7],day_of_week=line[8],
     	is_weekend=line[9],call_counts=line[10])
    t2.save()

