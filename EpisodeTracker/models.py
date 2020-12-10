from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birth_date = models.DateField(null=True, blank=True)

@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    try:
        instance.profile.save()
    except ObjectDoesNotExist:
        Profile.objects.create(user=instance)

LabelChoices = (
    ("1", "Series"),
    ("2", "Movie"),
    ("3", "Animation"),
    ("4", "Anime"),
    ("5", "OVA")
)
class Series(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    SeriesName = models.CharField(max_length=30, default="")
    NoEpisodes = models.PositiveIntegerField(default=0)
    EpisodesWatched = models.PositiveIntegerField(null=True, blank=True, default=0)
    Label = models.CharField(max_length=20, choices=LabelChoices, default="Series")
    CoverImage = models.ImageField(upload_to="uploads", null=True, blank=True, default="/noimg.png")
    DateCreated = models.DateField(default=timezone.now)

    def __str__(self):
        return self.SeriesName

    class Meta:
        verbose_name_plural = "Series"

    