from django.forms import Form, CharField, TextInput

class DownloadOneProductInformationForm(Form):
    article_number = CharField(max_length=9, label='Номер артикула')