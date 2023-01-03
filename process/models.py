from django.db import models

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    try:
        ext = filename[filename.index("."):]
    except:
        ext = ".png"
    return f'maps/{instance.id}/{instance.label}{ext}'

class MapImage(models.Model):    
    id = models.CharField(max_length=11, primary_key=True)
    label = models.CharField(max_length=20)
    image = models.ImageField(upload_to=user_directory_path, blank = True)
        
    def __str__(self):
        return self.label
    
class File(models.Model):
    existingPath = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=50)
    eof = models.BooleanField()
 