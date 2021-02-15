from django.db import models
from django.core import validators
from django.core.exceptions import ValidationError

from . import literals
import datetime

import numpy as np

## Different Validators

def validate_date(value):
    """ Custom validator """
    format = "%Y-%m-%d"
    if not datetime.datetime.strptime(str(value), format):
        raise ValidationError(f'{value} Should be a parsable date in YYYY-MM-DD (ISO format).')

def validate_stat_one(value):
    if not int(value) in (int(literals.STAT_ONE_CHOICE_ONE),int(literals.STAT_ONE_CHOICE_TWO),int(literals.STAT_ONE_CHOICE_THREE),int(literals.STAT_ONE_CHOICE_FOUR),int(literals.STAT_ONE_CHOICE_FIVE),int(literals.STAT_ONE_CHOICE_NOT_SPECIFIED)):
        raise ValidationError(f'{value} Should be one of the STAT_ONE_CHOICE_* literals')
    else:
        return value

def validate_stat_two(value):
    if not int(value) in (int(literals.STAT_TWO_CHOICE_ONE),int(literals.STAT_TWO_CHOICE_TWO),int(literals.STAT_TWO_CHOICE_THREE), int(literals.STAT_TWO_CHOICE_NOT_SPECIFIED)):
        raise ValidationError(f'{value} Should be one of the STAT_TWO_CHOICE_* literals')
    else:
        return value

def validate_name(value):
    length = len(value)
    if not len(value)<10:
        raise ValidationError(f"{value}-{length} Please check name should be having at most 10 charecters.")

def validate_rating(value):
    x = np.linspace(0,5,51)
    if not float(value) in [round(y, 1) for y in x]:
        raise ValidationError(f"{value} Should be a string representation of a 5 star rating with two significant digits. I.e. '1.0' through '5.0' ")
    else:
        return value

def validate_score(value):
    if not value in np.arange(0,51,1):
        raise ValidationError(f"{value} Should be an integer between 0 and 50, inclusive")
    else:
        return value

class Thing (models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    description = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateField(null=True, blank=True, validators=[validate_date])
    stat_one = models.CharField(max_length=2, default=literals.STAT_ONE_CHOICE_NOT_SPECIFIED,validators=[validate_stat_one])
    stat_two = models.CharField(max_length=1, default=literals.STAT_TWO_CHOICE_NOT_SPECIFIED, validators=[validate_stat_two])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now = True)

    def save(self, *args, **kwargs):
        self.full_clean(exclude=None)
        super(Thing, self).save(*args, **kwargs)


class Item (models.Model):
    thing = models.ForeignKey(Thing, on_delete=models.CASCADE)
    name = models.CharField(max_length=10, validators=[validate_name])
    rating = models.CharField(max_length=3, validators=[validate_rating])
    score = models.IntegerField(default=0, blank=True, validators=[validate_score])
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now = True)


    def save(self, *args, **kwargs):
        self.full_clean(exclude=None)
        super(Item, self).save(*args, **kwargs)

## Model to uploas the data.
class Document (models.Model):
    document = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    activated = models.BooleanField(default=False)

    class Meta:
        db_table = 'Document'
    
    def __str__(self):
        return f"File id: {self.id}"

## Creating this model to save the previously saved last object date.
class Previous_date (models.Model):
    prev_modified = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "Previous_date"
    
    def __str__(self):
        return f"Last Updated or Created : {self.prev_modified}"