from django.db import models
from PIL import Image


def thumbnailField(image_field: models.ImageField, icon_size: int):
    try:
        img = Image.open(image_field.path)

        if img.height > icon_size or img.width > icon_size:
            output_size = (icon_size, icon_size)
            img.thumbnail(output_size)
        img.save(image_field.path)
    except Exception as error:
        print(error)


class Category(models.Model):
    class Meta:
        abstract = True

    # Categories for products
    name = models.CharField(max_length=120, unique=True)
    ICON_SIZE = 64
    icon = models.ImageField(upload_to='images/icons',
                             blank=True)

    def save(self, *args, **kwargs):
        super(Category, self).save(*args, **kwargs)
        thumbnailField(self.icon, self.ICON_SIZE)

    def __str__(self):
        return self.name
