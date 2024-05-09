from django import forms
from .models import UploadedFile


class UploadFileForm(forms.Form):
    file = forms.FileField()

    class Meta:
        model = UploadedFile
        fields = ['file']

    def clean_file(self):
        file = self.cleaned_data.get('file', False)
        max_size = 25 * 1024 * 1024  # 20MB in bytes

        if file:
            if file.size > max_size:
                raise forms.ValidationError("The file size exceeds the limit of 20MB.")
            return file
        else:
            raise forms.ValidationError("Please select a file to uploads.")
