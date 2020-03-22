from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model
User = get_user_model()


class UserCreationForm(forms.ModelForm):
    password = forms.CharField(
        label='password', widget=forms.PasswordInput, required=True)
    username = forms.CharField(label='username', widget=forms.TextInput)
    is_active = forms.BooleanField()
    is_admin = forms.BooleanField()

    class Meta:
        model = User
        fields = ('email', 'password', 'username',
                  'is_active', 'is_admin')

    def save(self, commit=True):
        user = super().save(commit=True)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', 'is_admin')
