"""
Copyright (C) 2023  Benjamin Secker, Jolon Behrent, Louis Li, James Quilty

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


Server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from configservice.views import DeviceViewSet, ReadingViewSet, SensorViewSet
from rest_framework_nested import routers

# router = routers.DefaultRouter()
# router.register(r"devices", DeviceViewSet)
# router.register(r"sensors", SensorViewSet)
# router.register(r"readings", ReadingViewSet)

router = routers.SimpleRouter()
router.register(r"devices", DeviceViewSet)

sdi12_sensors_router = routers.NestedSimpleRouter(
    router, r"devices", lookup="sdi12_sensors"
)
sdi12_sensors_router.register(r"sdi12_sensors", SensorViewSet)

readings_router = routers.NestedSimpleRouter(
    sdi12_sensors_router, r"sdi12_sensors", lookup="readings"
)
readings_router.register(r"readings", ReadingViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(sdi12_sensors_router.urls)),
    path("", include(readings_router.urls)),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
