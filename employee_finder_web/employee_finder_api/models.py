import datetime

from django.db import models

# Create your models here.

class Employees(models.Model):
    """
        `id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, 
        `first_name` VARCHAR(255),
        `last_name` VARCHAR(255),
        `middle_name` VARCHAR(255),
        `position` VARCHAR(255),
        `email` VARCHAR(255),
        `phone` VARCHAR(15),
        `date` DATETIME DEFAULT CURRENT_TIMESTAMP,
        `origin` VARCHAR(255),
        `url` VARCHAR(255) UNIQUE
    """

    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    middle_name = models.CharField(max_length=255, blank=True)
    position = models.CharField(max_length=255)
    email = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    date  = models.DateTimeField(default=datetime.datetime.now())
    origin = models.CharField(max_length=255)
    url = models.CharField(max_length=255, unique=True)

    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"