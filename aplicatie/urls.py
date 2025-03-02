from django.urls import path
from . import views
urlpatterns = [
	path("bluray", views.afisare_bluray, name='afisare_bluray'),
	path("blurays", views.bluray_form, name="bluray_form"),
	path("mesaj_trimis", views.mesaj_trimis, name="mesaj_trimis"),
    path("contact", views.contact, name="contact"),
    path("creare_bluray", views.creare_blurays, name="creare_bluray"),
    path('inregistrare', views.inregistrare, name='inregistrare'),
    path('login', views.custom_login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('profile', views.profile_view, name='profile'),
    path('change_password', views.change_password_view, name='change_password'),
    path('confirma_mail/<str:cod>/', views.confirma_mail, name='confirma_mail'),
    path('bluray/<int:pk>', views.bluray_detalii, name='bluray_detalii'),
    path('promotii', views.promotii_view, name='promotii'),
]
