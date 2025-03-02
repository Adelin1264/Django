from django.shortcuts import render, redirect, get_object_or_404
from .models import BluRay
from .forms import FilterForm, ContactForm, preprocesare_salvare, BluRayForm
from django.core.paginator import Paginator
from django.http import HttpResponse
from django import forms
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
import uuid
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import CustomUser, Gen
from django.core.mail import send_mass_mail, mail_admins
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

def afisare_bluray(request):
    blurays = BluRay.objects.all()

    titlu = request.GET.get('titlu')
    if titlu:
        blurays = blurays.filter(titlu__icontains=titlu)

    calitate_video = request.GET.get('calitate_video')
    if calitate_video:
        blurays = blurays.filter(calitate_video__icontains=calitate_video)

    pret_min = request.GET.get('pret_min')
    pret_max = request.GET.get('pret_max')
    if pret_min and pret_min.isdigit():
        blurays = blurays.filter(pret__gte=int(pret_min))
    if pret_max and pret_max.isdigit():
        blurays = blurays.filter(pret__lte=int(pret_max))

    stoc_min = request.GET.get('stoc_min')
    if stoc_min and stoc_min.isdigit():
        blurays = blurays.filter(stoc__gte=int(stoc_min))

    subtitrari = request.GET.get('subtitrari')
    if subtitrari == '1':
        blurays = blurays.filter(subtitrari=True)
    elif subtitrari == '0':
        blurays = blurays.filter(subtitrari=False)

    paginator = Paginator(blurays, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'bluray.html', {'page_obj': page_obj})


def bluray_form(request):
    blurays = BluRay.objects.all().order_by('id')
    if request.method == 'POST':
        form = FilterForm(request.POST)
        if form.is_valid():
            nume = form.cleaned_data['nume']
            calitate_video = form.cleaned_data['calitate_video']
            pret_minim = form.cleaned_data['pret_minim']
            pret_maxim = form.cleaned_data['pret_maxim']
            stoc_min = form.cleaned_data['stoc']
            subtitrari = form.cleaned_data['subtitrari']
            
            if nume:
                blurays = blurays.filter(titlu__icontains=nume)
            if calitate_video:
                blurays = blurays.filter(calitate_video__icontains=calitate_video)
            if pret_minim is not None:
                blurays = blurays.filter(pret__gte=pret_minim)
            if pret_maxim is not None:
                blurays = blurays.filter(pret__lte=pret_maxim)
            if stoc_min is not None:
                blurays = blurays.filter(stoc__gte=stoc_min)
            if subtitrari == 'DA':
                blurays = blurays.filter(subtitrari=True)
            elif subtitrari == 'NU':
                blurays = blurays.filter(subtitrari=False)
    
    else:
        form = FilterForm()
    
    blurays = blurays.order_by('id')
    
    paginator = Paginator(blurays, 10)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'blurays.html', {'form': form, 'page_obj': page_obj})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            cleaned_data.pop("confirmare_email")
            preprocesare_salvare(cleaned_data)
            return redirect('mesaj_trimis')
    else:
        form = ContactForm()
        
    return render(request, 'contact.html', {'form': form})
        
def mesaj_trimis(request):
    return HttpResponse("Mesajul s-a trimis")

def creare_blurays(request):
    if request.method == 'POST':
        form = BluRayForm(request.POST)
        if form.is_valid():
            bluray = form.save(commit=False)
            pret_minim = form.cleaned_data['pret_minim']
            pret_maxim = form.cleaned_data['pret_maxim']
            bluray.pret = (pret_minim+pret_maxim)/2
            bluray.save()
            return redirect('bluray_form')
        else:
            return render(request, 'creare_bluray.html', {'form': form})
    else:
        form = BluRayForm()
    for field in form:
        print(field.label)
    return render(request, 'creare_bluray.html', {'form': form})


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import uuid

def inregistrare(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.cod = str(uuid.uuid4())
            user.save()

            subject = "Confirmare email - Bun venit!"
            html_content = render_to_string('email_confirmare.html', {
                'nume': user.first_name,
                'prenume': user.last_name,
                'username': user.username,
                'link_confirmare': f"{settings.SITE_URL}/confirma_mail/{user.cod}/"
            })

            email = EmailMultiAlternatives(
                subject=subject,
                body="Confirmare email",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()

            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'inregistrare.html', {'form': form})


def custom_login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST, request=request)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data.get('ramane_logat'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(24*60*60)
            return redirect('profile')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Parola a fost actualizata')
            return redirect('login')
        else:
            messages.error(request, 'Exista erori.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def profile_view(request):
    user = request.user
    user_data = {
        'username': user.username,
        'email': user.email,
        'telefon': user.telefon,
        'adresa': user.adresa,
        'data_nasterii': user.data_nasterii,
        'ocupatie': user.ocupatie,
        'descriere_personala': user.descriere_personala,
    }

    return render(request, 'profile.html', {'user_data': user_data})

def confirma_mail(request, cod):
    user = get_object_or_404(CustomUser, cod=cod)
    if not user.email_confirmat:
        user.email_confirmat = True
        user.cod = None 
        user.save()
        messages.success(request, "Emailul a fost confirmat cu succes!")
    else:
        messages.warning(request, "Emailul a fost deja confirmat.")

    return redirect('login')


from django.db.models import Count
from .models import Vizualizare, Film
from django.db.models import Prefetch
N = 5


def bluray_detalii(request, pk):
    try:
        bluray = get_object_or_404(
            BluRay.objects.prefetch_related(
                Prefetch('filme', queryset=Film.objects.prefetch_related('gen', 'director'))
            ),
            id=pk
        )

        if request.user.is_authenticated:
            Vizualizare.objects.create(utilizator=request.user, bluray=bluray)
            vizualizari = Vizualizare.objects.filter(utilizator=request.user).order_by('data_vizualizarii')

            if vizualizari.count() > N:
                vizualizari_vechi = vizualizari[:vizualizari.count() - N]
                for vizualizare in vizualizari_vechi:
                    vizualizare.delete()

        return render(request, 'bluray_detalii.html', {'bluray': bluray})

    except Exception as e:
        eroare_html = f"""
        <html>
            <body style="background-color: #ffcccc; padding: 20px; font-family: Arial, sans-serif;">
                <h2 style="color: #a00;">Eroare detectată în funcția <i>bluray_detalii</i></h2>
                <p><strong>Mesaj eroare:</strong> {str(e)}</p>
                <p><strong>Utilizator:</strong> {request.user.username if request.user.is_authenticated else "Anonim"}</p>
                <p><strong>URL:</strong> {request.build_absolute_uri()}</p>
            </body>
        </html>
        """
        mail_admins(
            subject="Eroare în aplicație: bluray_detalii",
            message="O eroare a avut loc. Vezi conținutul HTML pentru detalii.",
            html_message=eroare_html
        )


from .forms import PromotieForm
from .models import Promotie

def promotii_view(request, k_minim=3):
    if request.method == 'POST':
        form = PromotieForm(request.POST)
        if form.is_valid():
            promo = form.save(commit=False)
            promo.save()

            categorii_selectate = form.cleaned_data['categorii']
            emailuri = []

            for categorie in categorii_selectate:
                if categorie == 'calitate_video':
                    produse = BluRay.objects.filter(calitate_video=promo.calitate_video)
                elif categorie == 'subtitrari':
                    produse = BluRay.objects.filter(subtitrari=promo.subtitrari)
                else:
                    continue

                utilizatori = User.objects.filter(
                    id__in=Vizualizare.objects.filter(
                        produs__in=produse
                    ).values('utilizator').annotate(vizualizari=Count('id')).filter(vizualizari__gte=k_minim)
                ).distinct()

                for user in utilizatori:
                    if categorie == 'calitate_video':
                        template = 'email_calitate_video.html'
                    elif categorie == 'subtitrari':
                        template = 'email_subtitrari.html'
                    else:
                        continue

                    context = {
                        'user': user,
                        'nume_promotie': promo.nume,
                        'data_expirare': promo.data_expirare,
                        'reducere': promo.reducere,
                        'calitate_video': promo.calitate_video,
                        'link': f"http://localhost:8000/aplicatie/promotii/{promo.id}",
                    }

                    mesaj = render_to_string(template, context)
                    emailuri.append((
                        form.cleaned_data['subiect'],
                        mesaj,
                        'adelincircimaru.proiect@gmail.com',
                        [user.email]
                    ))
            send_mass_mail(emailuri, fail_silently=False)

            messages.success(request, "Promoția a fost creată și e-mailurile au fost trimise!")
            return redirect('promotii')
    else:
        form = PromotieForm()

    return render(request, 'promotii.html', {'form': form})