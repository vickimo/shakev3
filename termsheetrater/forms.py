"""
Forms and validation code for user registration.

"""


from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.forms import USStateField, USZipCodeField


attrs_dict = {'class': 'required'}

class TermForm(forms.Form):
    price = forms.IntegerField(widget=forms.TextInput(attrs={}),
                                label=_("Price"))
    paytoplay = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Yes',), ('2', 'No',), ('0', 'Unknown',)),
                                label=_("Pay to Play"))
    employeepool = forms.IntegerField(widget=forms.TextInput(attrs={}),
                                label=_("Employee Pool"))
    liqpref1 = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Junior',), ('2', 'Pari Passu',), ('0', 'Senior',)),
                                label=_("Liquidation Preference - Seniority"))
    liqpref2 = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', 'Yes',), ('2', 'No',), ('0', 'Unknown',)),
                                label=_("Liquidation Preference - Participating"))
    liqpref3 = forms.ChoiceField(widget=forms.RadioSelect, choices=(('1', '1',), ('2', '2',), ('3', '3',),('4', '4',), ('5', '5',)),
                                label=_("Liquidation Preference - Multiple"))

class SimpleFileForm(forms.Form):
    file = forms.Field(widget=forms.FileInput, required=False)