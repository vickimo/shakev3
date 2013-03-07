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

class ProfileForm(forms.Form):
    """
    Form for editing user profile
    
    """
    first_name = forms.CharField(widget=forms.TextInput(attrs={}),
                                label=_("First Name"))
    last_name = forms.CharField(widget=forms.TextInput(attrs={}),
                                label=_("Last Name"))
    email = forms.EmailField(widget=forms.TextInput(attrs={'maxlength':75}),
                                label=_("Email address"))
    shipping_street1 = forms.CharField(widget=forms.TextInput(attrs={}),
                                label=_("Address Line 1"))
    shipping_street2 = forms.CharField(widget=forms.TextInput(attrs={}),
                                label=_("Address Line 2"))
    shipping_city = forms.CharField(widget=forms.TextInput(attrs={}),
                                label=_("City"))
    shipping_state = USStateField(widget=forms.Select(choices={}),
                                label=_("State"))
    shipping_zipcode = USZipCodeField(widget=forms.TextInput(attrs={}),
                                label=_("Zipcode"))
    

    def __init__(self, *args, **kwargs):
        YOUR_STATE_CHOICES = list(STATE_CHOICES)
        YOUR_STATE_CHOICES.insert(0, ('', '---------'))
        self.request = kwargs.pop("request")
        super(ProfileForm, self).__init__(*args, **kwargs)
        user_profile = self.request.user.get_profile()
        for key, field in self.fields.iteritems():
            if hasattr(self.request.user, key):
                print key
                self.fields[key].widget.attrs['placeholder'] = getattr(self.request.user, key) #change placeholder to value if want more defined
            elif hasattr(user_profile, key):
                if key == 'shipping_state':
                    YOUR_STATE_CHOICES.insert(0, ('', getattr(user_profile, key)))
                    self.fields[key].widget.choices = YOUR_STATE_CHOICES
                else:
                    self.fields[key].widget.attrs['placeholder'] = getattr(user_profile, key)
            self.fields[key].required = False

    def clean(self):
        user_profile = self.request.user.get_profile()
        for field in self.cleaned_data:
            if self.cleaned_data[field] != '' and field != 'email':
                value = self.cleaned_data[field]
                setattr(user_profile, field, value)
                setattr(self.request.user, field, value)
        if 'email' in self.cleaned_data and self.cleaned_data['email'] != '':
            try:
                user = User.objects.get(email__iexact=self.cleaned_data['email'])
                if self.request.user.email != self.cleaned_data['email']:
                    raise forms.ValidationError(_("Email already in use!"))
            except User.DoesNotExist:
                self.request.user.email = self.cleaned_data['email']
        self.request.user.save()
        user_profile.save()
        return self.cleaned_data

class PasswordForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Current Password"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("New Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("New Password (again)"))
    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if len(self.cleaned_data['password1']) < 4:
                raise forms.ValidationError(_("New password is too short! (4 char min)"))
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
        return self.cleaned_data

class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("New Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("New Password (again)"))
    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
            elif len(self.cleaned_data['password1']) < 4:
                raise forms.ValidationError(_("Password is too short!"))
        return self.cleaned_data

class RegistrationForm(forms.Form):
    """
    Form for registering a new user account.
    
    Validates that the requested username is not already in use, and
    requires the password to be entered twice to catch typos.
    
    Subclasses should feel free to add any additional validation they
    need, but should avoid defining a ``save()`` method -- the actual
    saving of collected user data is delegated to the active
    registration backend.
    
    """
    username = forms.RegexField(regex=r'^\w+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _("This value must contain only letters, numbers and underscores.")})
    email = forms.EmailField(widget=forms.TextInput(attrs=dict(attrs_dict,
                                                               maxlength=75)),
                             label=_("Email address"))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
                                label=_("Password (again)"))
    
    def clean_username(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.
        
        """
        try:
            user = User.objects.get(username__iexact=self.cleaned_data['username'])
        except User.DoesNotExist:
            return self.cleaned_data['username']
        raise forms.ValidationError(_("A user with that username already exists."))
    def clean_email(self):
        """
        Validate that the email is not already
        in use.
        
        """
        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except User.DoesNotExist:
            return self.cleaned_data['email']
        raise forms.ValidationError(_("A user with that email already exists."))

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
        
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
            elif len(self.cleaned_data['password1']) < 4:
                raise forms.ValidationError(_("Password is too short!"))
        return self.cleaned_data


class RegistrationFormTermsOfService(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which adds a required checkbox
    for agreeing to a site's Terms of Service.
    
    """
    tos = forms.BooleanField(widget=forms.CheckboxInput(attrs=attrs_dict),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})


class RegistrationFormUniqueEmail(RegistrationForm):
    """
    Subclass of ``RegistrationForm`` which enforces uniqueness of
    email addresses.
    
    """
    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']