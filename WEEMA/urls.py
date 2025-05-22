"""
URL configuration for WEEMA project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

# Create a schema view using drf-yasg
schema_view = get_schema_view(
    openapi.Info(
        title="WEEMA platform",
        default_version='v1',
        description="WEEMA platform implemented using django",
        terms_of_service="",
        contact=openapi.Contact(email=settings.EMAIL),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url='https://community.weema.org/api/v1/user/'
)

from django.contrib import admin
from django.urls import path, include, re_path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/user/", include("user_management.urls")),
    path("api/v1/user/", include("authentication.urls")),
    path("api/v1/user/", include("cluster_management.urls")),
    path("api/v1/user/analytics/", include("analytics.urls")),
    path("api/v1/user/", include("data_collection.urls")),
    path("api/v1/user/", include("meeting_tracker.urls")),
    
    
    re_path(r'^api/v1/user/swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^api/v1/user/redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
