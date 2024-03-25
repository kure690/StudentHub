from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('home', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('passreset', auth_views.PasswordResetView.as_view,name='passreset'),
    path('passresetdone', auth_views.PasswordResetDoneView.as_view,name='passresetdone'),
    path('passresetconfirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view,name='passresetconfirm'),
    path('passresetcomplete', auth_views.PasswordResetCompleteView.as_view,name='passresetcomplete'),

]
 
