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
    Call_counts = models.FloatField()

class Ambulance(models.Model):
    id = models.IntegerField(primary_key=True)
    amb_id = models.IntegerField()
    LAT = models.FloatField()
    LONG = models.FloatField()
    AVAILABLE = models.IntegerField()

class EMS_Calls(models.Model):
    ems_id = models.IntegerField(primary_key=True)
    LAT = models.FloatField()
    LONG = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)

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
    Call_counts = models.FloatField()

class Current_ambulance(models.Model):
    amb_id = models.IntegerField(primary_key=True)
    LAT = models.FloatField()
    LONG = models.FloatField()
    AVAILABLE = models.IntegerField()

class Current_emscall(models.Model):
    LAT = models.FloatField()
    LONG = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)	
