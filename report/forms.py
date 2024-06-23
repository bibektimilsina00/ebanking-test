
from django import forms

class ReportForm(forms.Form):
    account_number = forms.CharField(label='Account Number', max_length=255)
    start_date = forms.DateField(label='Start Date', widget=forms.SelectDateWidget)
    end_date = forms.DateField(label='End Date', widget=forms.SelectDateWidget)
