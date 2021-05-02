from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model


class Image(models.Model):
    S3_DIR = "iidb"

    img = models.FileField(upload_to=S3_DIR)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="images")

    date_added = models.DateTimeField(editable=False)
    date_modified = models.DateTimeField(editable=True)

    def __str__(self):
        return str(self.__dict__)

    def save(self, *args, **kwargs):
        if self.id:
            self.date_modified = timezone.now()
        else:
            self.date_added = timezone.now()
            self.date_modified = timezone.now()

        super(Image, self).save(*args, **kwargs)
