from . import views
from django.urls import path,include

urlpatterns = [
    path('cleanEmailLog', views.cleanEmailData, name = "email"),
    path('cleanCallLog',views.cleanCallLog, name = "deepsocial"),
    path('cleanAppList',views.cleanAppList, name = "app"),
    path('cleanMobileFp',views.cleanMobileFp, name = "mobile"),
    path('cleanSurvey',views.cleanSurvey, name = "survey"),
]