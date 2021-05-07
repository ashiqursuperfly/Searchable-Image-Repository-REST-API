from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from django.template.defaultfilters import slugify
import hashlib


class ImageCategory(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        verbose_name_plural = "ImageCategories"

    def __str__(self):
        return self.name.__str__()


class Image(models.Model):
    S3_DIR = "iidb"

    img = models.FileField(upload_to=S3_DIR)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='images')
    description = models.CharField(max_length=512, help_text='tell us something in short that best describe your image(mandatory)')
    country = CountryField(null=True, blank=True)
    categories = models.ManyToManyField(ImageCategory, related_name='images', blank=True)

    orb_descriptor = models.BinaryField()

    date_added = models.DateTimeField(editable=False)
    date_modified = models.DateTimeField(editable=True)

    def __str__(self):
        return str(self.img) + '-' + str(self.owner)

    def save(self, *args, **kwargs):
        if self.id:
            self.date_modified = timezone.now()
        else:
            self.date_added = timezone.now()
            self.date_modified = timezone.now()

        super(Image, self).save(*args, **kwargs)

    @staticmethod
    def generate_s3_key(filename: str):
        slug = slugify(filename)
        hashed = int(hashlib.sha256(filename.encode('utf-8')).hexdigest(), 16) % 10 ** 8
        return Image.S3_DIR + '/' + (str(hashed) + '_' + slug)
