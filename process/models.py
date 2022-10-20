from django.db import models

class MapImage(models.Model):
    label = models.CharField(max_length=20)
    image = models.ImageField(upload_to='maps')

    def __str__(self):
        return self.label
 