from django.conf.urls import url

from . import views
from django.contrib import admin
from django.views.generic import TemplateView
from django.conf.urls import include, url
urlpatterns = [
url(r'^admin/', include(admin.site.urls)),
url(r'^$', TemplateView.as_view(template_name="map.html")),
]

