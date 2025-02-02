from django.db import models

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)
    glb_url = models.URLField(blank=True, null=True)  # URL du modèle 3D généré
