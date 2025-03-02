from django import forms
from datetime import date, datetime
import re, os, json
from django.conf import settings
from .models import BluRay
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Gen, Promotie
from django.core.mail import mail_admins


class FilterForm(forms.Form):
    variante = [('TOATE', 'Toate'), ('DA', 'Cu subtitrari'), ('NU', 'Fara subtitrari')]
    nume = forms.CharField(max_length=30, label='Nume', required=False)
    calitate_video = forms.CharField(max_length=30, label='Calitate video', required=False)
    pret_minim = forms.IntegerField(label='Pret minim', required=False)
    pret_maxim = forms.IntegerField(label='Pret maxim', required=False)
    stoc = forms.IntegerField(label='Stoc minim', required=False)
    subtitrari = forms.ChoiceField(choices=variante, required=False)
    

def validare_spatii(sir):
    if not sir.istitle():
        raise forms.ValidationError("Numele, prenumele si subiectul mesajului trebuie sa inceapa cu litera mare.")
    if not all(c.isalpha() or c.isspace() for c in sir):
        raise forms.ValidationError("Numele, prenumele si subiectul mesajului trebuie sa contina doar litere si spatii.")
    
class ContactForm(forms.Form):
    nume = forms.CharField(max_length=10, label='Nume', required=True)
    prenume = forms.CharField(label='Prenume')
    data_nastere = forms.DateField(label='Data nasterii')
    email = forms.EmailField(label='E-mail', required=True)
    confirmare_email = forms.EmailField(label='Confirmare e-mail', required=True)
    tip_mesaj = forms.ChoiceField(choices=[('RECLAMATIE', 'reclamatie'),
                                        ('INTREBARE', 'intrebare'), ('REVIEW', 'review'),
                                        ('CERERE', 'cerere'), ('PROGRAMARE', 'programare')],
                                label='Tip mesaj', required=True)
    subiect = forms.CharField(label='Subiect', required=True)
    min_zile_ast = forms.IntegerField(min_value=1, label='Minin zile asteptare')
    mesaj = forms.CharField(widget=forms.Textarea, label='Mesaj (semnatura la final)', required=True)
    
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        confirm_email = cleaned_data.get("confirmare_email")
        if email and confirm_email and email != confirm_email:
            raise forms.ValidationError("Adresele de email nu coincid.")
        
        data_nastere = cleaned_data.get("data_nastere")
        data_curenta = date.today()
        diferenta_ani = data_curenta.year - data_nastere.year
        if (data_curenta.month, data_curenta.day) < (data_nastere.month, data_nastere.day):
            diferenta_ani -= 1
        if data_nastere and diferenta_ani<18:
            raise forms.ValidationError("Varsta minima este 18.")
        
        mesaj = cleaned_data.get("mesaj")
        cuvinte = re.findall(r'\w+', mesaj)
        if mesaj and (len(cuvinte)<5 or len(cuvinte)>100):
            raise forms.ValidationError("Mesajul trebuie sa contina intre 5 si 100 de cuvinte.")
        
        cuvinte = mesaj.split()
        for cuvant in cuvinte:
            if cuvant.startswith("http://") or cuvant.startswith("https://"):
                raise forms.ValidationError("Mesajul nu poate contine link-uri.")

        nume = cleaned_data.get("nume")
        if cuvinte and cuvinte[-1] != nume:
            raise forms.ValidationError("La finalul mesajului trebuie sa existe semnatura.")
        
        prenume = cleaned_data.get("prenume")
        subiect = cleaned_data.get("subiect")
        validare_spatii(nume)
        if prenume:
            validare_spatii(prenume)
        validare_spatii(subiect)
        
        return cleaned_data
        
def preprocesare_salvare(form_data):
    data_nastere = form_data.pop("data_nastere")
    data_curenta = date.today()
    ani = data_curenta.year - data_nastere.year
    luni = data_curenta.month - data_nastere.month
    if luni < 0:
        ani -= 1
        luni += 12
    form_data['varsta'] = f"{ani} ani și {luni} luni"

    mesaj = form_data['mesaj']
    mesaj = re.sub(r'\s+', ' ', mesaj.replace('\n', ' ')).strip()
    form_data['mesaj'] = mesaj

    timestamp = int(datetime.now().timestamp())
    nume_fisier = f"mesaj_{timestamp}.json"
    cale_folder = os.path.join(settings.BASE_DIR, 'aplicatie', 'mesaje')


    cale_fisier = os.path.join(cale_folder, nume_fisier)
    with open(cale_fisier, 'w', encoding='utf-8') as fisier_json:
        json.dump(form_data, fisier_json, ensure_ascii=False, indent=4)
        
class BluRayForm(forms.ModelForm):
    pret_minim = forms.DecimalField(
        label="Preț minim", 
        help_text="Introduceți prețul minim pentru intervalul de preț.",
        error_messages={
            'required': "Prețul minim este obligatoriu.",
            'invalid': "Introduceți un număr valid pentru prețul minim."
        }
    )
    pret_maxim = forms.DecimalField(
        label="Preț maxim",
        error_messages={
            'required': "Prețul maxim este obligatoriu.",
            'invalid': "Introduceți un număr valid pentru prețul maxim."
        }
    )
    class Meta:
        model = BluRay
        fields = ['titlu', 'calitate_video', 'stoc', 'subtitrari']
        labels = {
            'titlu': 'Titlul filmului',
            'calitate_video': 'Calitate video',
            'stoc': 'Stoc disponibil',
            'subtitrari': 'Are subtitrări?',
        }
        help_texts = {
            'titlu': "Introduceți titlul complet al BluRay. Maximum 50 de caractere.",
        }
        error_messages = {
            'titlu': {
                'required': "Titlul filmului este obligatoriu.",
                'max_length': "Titlul nu poate depăși 50 de caractere.",
            },
            'calitate_video': {
                'required': "Calitatea video este obligatorie.",
            },
            'stoc': {
                'required': "Stocul este obligatoriu.",
                'invalid': "Introduceți un număr valid pentru stoc.",
            },
        }
        
    def clean_calitate_video(self):
        calitate_video = self.cleaned_data.get('calitate_video')
        valid_options = ['HD', 'FullHD', '4K', '8K']
        if not any(option in calitate_video for option in valid_options):
            raise forms.ValidationError(f"Calitatea video trebuie sa contina unul dintre: {', '.join(valid_options)}.")
        return calitate_video

    def clean_titlu(self):
        titlu = self.cleaned_data.get('titlu')
        if len(titlu) < 3:
            raise forms.ValidationError("Titlul trebuie sa contina cel putin 3 caractere.")
        return titlu
    
    def clean_stoc(self):
        stoc = self.cleaned_data.get('stoc')
        if stoc <= 0:
            raise forms.ValidationError("Stocul trebuie sa fie mai mare decat 0.")
        return stoc
    
    def clean(self):
        cleaned_data = super().clean()
        pret_minim = cleaned_data.get('pret_minim')
        pret_maxim = cleaned_data.get('pret_maxim')

        if pret_minim and pret_maxim and pret_minim > pret_maxim:
            raise forms.ValidationError("Pretul minim trebuie sa fie mai mic decat pretul maxim.")
        
        return cleaned_data
    
    
class CustomUserCreationForm(UserCreationForm):
    telefon = forms.CharField(max_length=15, required=True)
    adresa = forms.CharField(widget=forms.Textarea)
    data_nasterii = forms.DateField(required=True)
    ocupatie = forms.CharField(max_length=100)
    descriere_personala = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'password1', 'password2', 
            'telefon', 'adresa', 'data_nasterii', 'ocupatie', 'descriere_personala'
        ]

    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon')
        if not telefon.isdigit():
            raise forms.ValidationError("Numărul de telefon trebuie să conțină doar cifre.")
        if len(telefon) < 10 or len(telefon) > 15:
            raise forms.ValidationError("Numărul de telefon trebuie să aibă între 10 și 15 cifre.")
        return telefon

    def clean_data_nasterii(self):
        data_nasterii = self.cleaned_data.get('data_nasterii')
        from datetime import date
        if data_nasterii >= date.today():
            raise forms.ValidationError("Data nașterii trebuie să fie în trecut.")
        return data_nasterii

    def clean_adresa(self):
        adresa = self.cleaned_data.get('adresa')
        if len(adresa.split()) < 3:
            raise forms.ValidationError("Adresa trebuie să conțină cel puțin 3 cuvinte.")
        return adresa
    
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')

        if username and username.lower() == 'admin':
            subiect = "Cineva încearcă să ne preia site-ul"
            mesaj = f"Adresa de e-mail: {email if email else 'Necunoscută'}"
            mesaj_html = f"""
                <h1 style="color: red;">Cineva încearcă să ne preia site-ul</h1>
                <p>Adresa de e-mail: {email if email else 'Necunoscută'}</p>
            """
            mail_admins(subiect, mesaj, html_message=mesaj_html)
            raise forms.ValidationError("Acest username nu este permis.")
        return cleaned_data


class CustomAuthenticationForm(AuthenticationForm):
    ramane_logat = forms.BooleanField(
        required=False,
        initial=False,
        label='Ramaneti logat'
        
    )
    def confirm_login_allowed(self, user):
        if not user.email_confirmat:
            raise forms.ValidationError(
                "Contul nu a fost confirmat. Verifică emailul pentru confirmare.",
                code='email_not_confirmed',
            )

    def clean(self):        
        cleaned_data = super().clean()
        ramane_logat = self.cleaned_data.get('ramane_logat')
        return cleaned_data

class PromotieForm(forms.ModelForm):
    CATEGORII_CHOICES = [
        ('calitate_video', 'Calitate Video (4K)'),
        ('subtitrari', 'Subtitrări'),
    ]

    subiect = forms.CharField(max_length=100, required=True)
    mesaj = forms.CharField(widget=forms.Textarea, required=True)
    categorii = forms.MultipleChoiceField(choices=CATEGORII_CHOICES, widget=forms.CheckboxSelectMultiple, required=True)

    class Meta:
        model = Promotie
        fields = ['nume', 'data_expirare', 'reducere', 'calitate_video', 'subtitrari']