from django.urls import path
from emaildjango.views import *
from django.conf.urls import include


urlpatterns = [
    path('database/', updateDatabase, name='update_database'),
    path('list/<int:id>/', listEmployees.as_view(), name='detail-employee'),
    path('list/', listEmployees.as_view(), name='list-employees'),
    path('add/',addEmployee.as_view(), name='add-employee'),
    path('sendemail/',send_email_to_employees.as_view(),name='send_email_to_employees'),
    path('delete/<int:id>/',deleteEmployee.as_view(),name='delete-employee'),
    path('update/<int:id>/',updateEmployee.as_view(),name='update-employee'),
    path('activate/<str:token>/',activate_account.as_view(), name='activate'),
    path('login/',login.as_view(),name='login'),
    path('view_profile/',profile_view.as_view(),name='profile'),
    path('edit_profile/',profile_edit.as_view(),name='profile'),
    
]