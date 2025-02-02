import os
import base64
import time
import requests
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import default_storage
from .models import UploadedImage

# Remplace par ta clé API Meshy
MESHY_API_KEY = "msy_MosdkRcAiF4kRnrovuiouQUQhnbVwoWCMx1E"

class MeshyAPI:
    def __init__(self):
        self.base_url = "https://api.meshy.ai/openapi/v1"
        self.headers = {"Authorization": f"Bearer {MESHY_API_KEY}"}

    def create_3d_task(self, image_path):
        """Envoie l'image à l'API Meshy pour la conversion"""
        with open(image_path, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        payload = {
            "image_url": f"data:image/jpeg;base64,{image_base64}",
            "ai_model": "meshy-4",
            "topology": "triangle",
            "target_polycount": 30000,
            "should_remesh": True,
            "enable_pbr": True,
            "should_texture": True,
            "symmetry_mode": "auto"
        }

        response = requests.post(f"{self.base_url}/image-to-3d", headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json().get("result")

    def get_task_status(self, task_id):
        """Vérifie l'état du traitement"""
        response = requests.get(f"{self.base_url}/image-to-3d/{task_id}", headers=self.headers)
        response.raise_for_status()
        return response.json()

def index(request):
    """Affiche la page d'accueil"""
    return render(request, "index.html")

def upload_image(request):
    """Vue pour uploader une image et obtenir un modèle 3D"""
    if request.method == "POST" and request.FILES.get("image"):
        uploaded_file = request.FILES["image"]
        file_path = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)
        full_path = os.path.join(settings.MEDIA_ROOT, file_path)

        meshy = MeshyAPI()
        task_id = meshy.create_3d_task(full_path)

        while True:
            task_info = meshy.get_task_status(task_id)
            status = task_info.get("status")

            if status == "SUCCEEDED":
                glb_url = task_info.get("model_urls", {}).get("glb", "")
                UploadedImage.objects.create(image=file_path, glb_url=glb_url)
                return render(request, "result.html", {"glb_url": glb_url})

            elif status == "FAILED":
                return render(request, "kasserine/error.html", {"error": "La conversion a échoué."})

            time.sleep(5)  # Vérifie toutes les 5 secondes

    return render(request, "upload.html")
