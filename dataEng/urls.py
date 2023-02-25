from . import views
from django.urls import path,include

urlpatterns = [
    path('', views.cleanEmailData, name = "email")

]