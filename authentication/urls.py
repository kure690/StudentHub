from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import InfoUpdate, ClassView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('home', views.home, name="home"),
    path('signup', views.signup, name="signup"),
    path('signin', views.signin, name="signin"),
    path('signout', views.signout, name="signout"),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard2/', ClassView.as_view(), name='dashboard2'),
    path('editprofile/<int:pk>/', InfoUpdate.as_view(), name='editprofile'),
    path('changepass', views.Change_Password, name= "ChangePassword"),
    


    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='authentication/reset_pass.html'), name = "reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='authentication/reset_pass_done.html'), name = "password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/reset_pass_change.html'), name = "password_reset_confirm"),
    #path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name = "password_reset_confirm"),
    #path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='authentication/changepass.html'), name = "password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='authentication/reset_pass_confirm.html'), name = "password_reset_complete"),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)








    # path('passreset', views.passreset_view, name='passreset'),
    # path('changepass', views.changepass, name="changepass"),
    # path('resetpass/', views.resetpass, name='resetpass'),
    # path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    #path('passresetdone/', views.passreset_view, name='passreset'),
    # path('passreset/', auth_views.PasswordResetView.as_view(template_name='authentication/forgetpass.html'),name='passreset'),
    # path('passreset/', auth_views.PasswordResetView.as_view(),name='passreset'),
    #path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(),name='password_reset_done'),
    # path('passresetconfirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #path('passresetconfirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),name='passresetconfirm'),
    #path('passresetcomplete', auth_views.PasswordResetCompleteView.as_view(),name='passresetcomplete'),
    


 
