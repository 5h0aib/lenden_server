from . import views
from django.urls import path,include

urlpatterns = [
    path('getEmailData/',views.getEmailData),
    path('addEmailData/',views.addEmailData),

    path('getDeepSocialData/',views.getDeepSocialData),
    path('addDeepSocialData/',views.addDeepSocialData),

    path('getAppUsageData/',views.getAppUsageData),
    path('addAppUsageData/',views.addAppUsageData),

    path('getSocialFpData/',views.getSocialFpData),
    path('addSocialFpData/',views.addSocialFpData),

    path('getMobileFpData/',views.getMobileFpData),
    path('addMobileFpData/',views.addMobileFpData),

    path('getSurvey/',views.getSurvey),
    path('addSurvey/',views.addSurvey),

    path('getSurvey2/',views.getSurvey2),
    path('addSurvey2/',views.addSurvey2),



    
]