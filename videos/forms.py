"""
Create for video upload, user registration and profile editing.
Render HTML input fields and validate submitted data.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Video

class VideoUploadForm(forms.ModelForm):
    """Upload form of file, title, description and visibility."""
    class Meta:
        model = Video
        fields = ['file', 'title', 'description', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Give your video a title',
                'class': 'form-input',
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Describe your video...',
                'rows': 4,
                'class': 'form-input',
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-input',
            }),
            'file': forms.ClearableFileInput(attrs={
                'accept': 'video/*',
                'id': 'file',
            }),
        }

class RegisterForm(UserCreationForm):
    """Extends Django's built-in form with an email field."""
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Choose a username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['placeholder'] = 'Create a password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

class ProfileForm(forms.ModelForm):
    """Form for editing user profile (bio + avatar)."""
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'placeholder': 'Tell people about yourself...',
                'rows': 4,
                'class': 'form-input',
            }),
            'avatar': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
            }),
        }
