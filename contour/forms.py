from django import forms


class FinishDrawingForm(forms.Form):
    finish_drawing  = forms.BooleanField(required=True, initial=True)

class DiscardSessionForm(forms.Form):
    discard_session  = forms.BooleanField(required=True, initial=True)

class SaveSessionForm(forms.Form):
    name = forms.CharField(max_length=255)
    save_session  = forms.BooleanField(required=True, initial=True)

class UploadFileForm(forms.Form):
    file  = forms.FileField(required=True)
