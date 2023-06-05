from django.urls import path
from emaildjango.views import *

urlpatterns = [
    path('send/', EmailAPI.as_view(), name='send_email'),
]