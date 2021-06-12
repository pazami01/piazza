from django.urls import path
from . import views

# THE ENTIRE CODE IN THIS FILE IS FROM CCC LAB4 #

urlpatterns = [
    path('register/', views.register),
    path('token/', views.token),
    path('token/refresh/', views.refresh_token),
    path('token/revoke/', views.revoke_token),
]
