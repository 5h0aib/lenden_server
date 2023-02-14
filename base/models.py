from django.db import models

# Create your models here.
class EmailUsage(models.Model):
    userId = models.CharField(max_length=200)
    email_log = models.JSONField()
    time_log = models.DateTimeField(auto_now_add=True)


class DeepSocial(models.Model):
    userId = models.CharField(max_length=200)
    call_log = models.JSONField()


class AppUsage(models.Model):
    userId = models.CharField(max_length=200)
    app_log = models.JSONField()

class SocialFp(models.Model):
    userId = models.CharField(max_length=200)
    app_list = models.JSONField()

class MobileFp(models.Model):
    userId = models.CharField(max_length=200)
    no_contacts = models.IntegerField()
    no_sms = models.IntegerField()


class Survey(models.Model):
    userId = models.CharField(max_length=200)
    answers = models.JSONField()


class Survey2(models.Model):
    userId = models.CharField(max_length=200)
    qp7 = models.JSONField()
    qp3 = models.CharField(max_length=200)

