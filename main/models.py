from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Bank(models.Model):
    total_supply = models.FloatField()
    in_bank = models.FloatField()
    inflation = models.FloatField()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.TextField()
    Holdings = models.FloatField(default=0)
    wallet = models.FloatField(default=0)
    interest = models.FloatField(default=0)

    def __str__(self):
        return str(self.user)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    to = models.CharField(max_length=50)
    time = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return str(self.user)
    