from django import forms 
from .models import Document, Thing, Item
import csv
import io
from django.core.exceptions import ValidationError

class DocumentForm(forms.ModelForm):
    error_messages = { 
                 'required':"Please Upload correct File or check whether the data is well formatted."
                 }
    class Meta:
        model = Document
        fields = ('document',)
