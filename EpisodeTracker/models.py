from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db.models.signals import pre_save
from django.utils.text import slugify

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
    slug = models.SlugField(unique=True, default='')
    is_multiple_seasons = models.BooleanField(default=False)
    NoEpisodes = models.PositiveIntegerField(default=0)
    EpisodesWatched = models.PositiveIntegerField(null=True, blank=True, default=0)
    Label = models.CharField(max_length=20, choices=LabelChoices, default="Series")
    CoverImage = models.ImageField(upload_to="uploads", null=True, blank=True, default="/noimg.png")
    DateCreated = models.DateField(default=timezone.now)

    def __str__(self):
        return self.SeriesName

    def get_absolute_url(self):
        return reverse('seriespage', kwargs={'slug': self.slug})

    class Meta:
        verbose_name_plural = "Series"


def create_slug(instance, new_slug = None):
    slug = slugify(instance.SeriesName)
    if new_slug is not None:
        slug = new_slug
    qs = Series.objects.filter(slug=slug).order_by("-id")
    exists = qs.exists()
    if exists:
        new_slug = "%s-%s" %(slug, qs.first().id)
        return create_slug(instance, new_slug = new_slug)
    return slug

def pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)

pre_save.connect(pre_save_receiver, sender=Series)

class Seasons(models.Model):
    pass