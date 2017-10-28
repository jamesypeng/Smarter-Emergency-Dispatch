from django.db import models

# Create your models here.

class Prob(models.Model):
	prob_id = models.IntegerField()
	zipcode = models.CharField(max_length=5)
	predicted_ems = models.FloatField()

