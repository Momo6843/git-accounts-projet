from django import forms
from django.contrib.auth.models import User
from .models import AccountType, Manager, Employee, Profile,Department
from django import forms
from django.contrib.auth.models import User


class AccountTypeForm(forms.ModelForm):
    class Meta:
        model = AccountType
        fields = ['name', 'description']

class ProfileForm(forms.ModelForm):
    account_types = forms.ModelMultipleChoiceField(
        queryset=AccountType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Types de comptes"
    )

    class Meta:
        model = Profile
        fields = ['name', 'account_types']
        labels = {
            'name': 'Nom du profil'
        }

class ManagerForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class EmployeeForm(forms.ModelForm):
    profile = forms.ModelChoiceField(queryset=Profile.objects.all(), required=False, label='Profile')
    account_types = forms.ModelMultipleChoiceField(
        queryset=AccountType.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Account Types'
    )
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

    class Meta:
        model = Employee
        fields = ['first_name', 'last_name', 'email', 'department', 'profile','account_types']

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        if 'account_types' in self.data:
            try:
                self.fields['account_types'].queryset = AccountType.objects.all()
            except (ValueError, TypeError):
                self.fields['account_types'].queryset = AccountType.objects.none()
        elif self.instance.pk:
            self.fields['account_types'].queryset = self.instance.account_types.all()

    def save(self, commit=True):
        instance = super(EmployeeForm, self).save(commit=False)
        if commit:
            instance.save()
            self.save_m2m()
        return instance
    
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['name']