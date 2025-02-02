from django.urls import path
from .views import index, upload_image

urlpatterns = [
    path("index/", index, name="index"),  # Page d'accueil
    path("upload/", upload_image, name="upload_image"),  # Upload et conversion 3D
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
