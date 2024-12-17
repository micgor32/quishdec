from django import forms

class ImageUploadForm(forms.Form):
    image = forms.ImageField(required=True, label="Select a QR code image:")
