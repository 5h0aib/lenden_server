from rest_framework import serializers
from base.models import EmailUsage,DeepSocial,AppUsage,SocialFp,MobileFp,Survey,Survey2


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailUsage
        fields = "__all__"



class DeepSocialSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeepSocial
        fields = "__all__"


class AppUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppUsage
        fields = "__all__"


class SocialFpSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialFp
        fields = "__all__"
        

class MobileFpSerializer(serializers.ModelSerializer):
    class Meta:
        model = MobileFp
        fields = "__all__"


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = "__all__"


class Survey2Serializer(serializers.ModelSerializer):
    class Meta:
        model = Survey2
        fields = "__all__"