from rest_framework.response import Response
from rest_framework.decorators import api_view
from base.models import EmailUsage,DeepSocial,AppUsage,SocialFp,MobileFp,Survey,Survey2
from .serializers import EmailSerializer,DeepSocialSerializer,AppUsageSerializer,SocialFpSerializer,MobileFpSerializer,SurveySerializer,Survey2Serializer
import logging


# ------------------------------------------------------------------------------------
@api_view(['GET'])
def getEmailData(request):
    emails = EmailUsage.objects.all()
    serializer = EmailSerializer(emails , many=True)
    return Response(serializer.data)


@api_view(['POST'])
def addEmailData(request):
    serializer = EmailSerializer( data = request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

# ------------------------------------------------------------------------------------
@api_view(['GET'])
def getDeepSocialData(request):
    deepsocialdata = DeepSocial.objects.all()
    serializer = DeepSocialSerializer(deepsocialdata , many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addDeepSocialData(request):
    serializer = DeepSocialSerializer( data = request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

# ------------------------------------------------------------------------------------

@api_view(['GET'])
def getAppUsageData(request):
    appusagedata = AppUsage.objects.all()
    serializer = AppUsageSerializer(appusagedata , many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addAppUsageData(request):
    logging.critical(request.data)
    serializer = AppUsageSerializer(data = request.data)
    if serializer.is_valid():
        serializer.save()
        logging.critical("pls")
    logging.critical(serializer.data)
    return Response(serializer.data)


# ------------------------------------------------------------------------------------

@api_view(['GET'])
def getSocialFpData(request):
    socialfpdata = SocialFp.objects.all()
    serializer = SocialFpSerializer(socialfpdata , many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addSocialFpData(request):
    serializer = SocialFpSerializer( data = request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

# ------------------------------------------------------------------------------------

@api_view(['GET'])
def getMobileFpData(request):
    mobilefpdata = MobileFp.objects.all()
    serializer = MobileFpSerializer(mobilefpdata , many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addMobileFpData(request):
    serializer = MobileFpSerializer( data = request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)



# ------------------------------------------------------------------------------------

@api_view(['GET'])
def getSurvey(request):
    surveydata = Survey.objects.all()
    serializer = SurveySerializer(surveydata , many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addSurvey(request):
    serializer = SurveySerializer( data = request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)



# ------------------------------------------------------------------------------------

@api_view(['GET'])
def getSurvey2(request):
    survey2data = Survey2.objects.all()
    serializer = Survey2Serializer(survey2data , many=True)
    return Response(serializer.data)

@api_view(['POST'])
def addSurvey2(request):
    serializer = Survey2Serializer( data = request.data)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)