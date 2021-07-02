from django import forms
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
import datetime

today = datetime.datetime.now()
thisYear = today.year

INTEGER_CHOICES= [tuple([x,x]) for x in range(1958,thisYear+1)]
class YearForm(forms.Form):
  year = forms.CharField(label='Select a year', widget=forms.Select(choices=INTEGER_CHOICES))

  def clean_year(self):
      data = self.cleaned_data['year']
      return data
