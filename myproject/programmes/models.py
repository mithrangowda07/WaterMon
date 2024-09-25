from django.db import models

# UG Programme Model
class UGProgramme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    hod_name = models.CharField(max_length=100, blank=True, null=True)  # HOD name
    year_started = models.PositiveIntegerField(blank=True, null=True)   # Year started

    def __str__(self):
        return self.name

# PG Programme Model
class PGProgramme(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    hod_name = models.CharField(max_length=100, blank=True, null=True)  # HOD name
    year_started = models.PositiveIntegerField(blank=True, null=True)   # Year started

    def __str__(self):
        return self.name
