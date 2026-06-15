from django.contrib import admin
from django.urls import path
from workflows.views import save_workflow

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/workflows/save/', save_workflow), # Our new save route
]