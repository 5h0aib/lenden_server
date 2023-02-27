from . import views
from django.urls import path,include

urlpatterns = [
    path('cleanEmailLog', views.cleanEmailData, name = "email"),
    path('cleanCallLog',views.cleanCallLog, name = "mobile")
]