from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True
    )

    
    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]

class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Username",
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Password",
            }
        )
    )



# class LoginForm(AuthenticationForm):

#     email = forms.EmailField(
#             required=True
#         )

#     class Meta:
#             model = User
#             fields = [
#                 'username',
#                 'password',
#             ]    




class UserForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
        ]


class ProfileForm(forms.ModelForm):

    class Meta:

        model = UserProfile

        fields = [
            "address",
            "phone_number",
            "gender",
            "profile_picture",
        ]