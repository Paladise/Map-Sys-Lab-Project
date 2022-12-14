from django.db import models

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    ext = filename[filename.index("."):]
    return f'maps/{instance.id}/{instance.label}{ext}'

class MapImage(models.Model):    
    id = models.CharField(max_length=11, primary_key=True)
    label = models.CharField(max_length=20)
    image = models.ImageField(upload_to=user_directory_path)
        
    def __str__(self):
        return self.label
    
 