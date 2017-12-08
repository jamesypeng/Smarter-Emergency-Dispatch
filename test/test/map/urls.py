# from . import views
# from django.contrib import admin
# from django.views.generic import TemplateView
# from django.conf.urls import include, url

# urlpatterns = [
# url(r'^admin/', include(admin.site.urls)),
# url(r'^$', TemplateView.as_view(template_name="map.html")),
# url(r'', include('map.urls')),
# ]


from django.conf.urls import include, url
from . import views

urlpatterns = [
    # url(r'^$', views.current_state, name='current_state'),
    url(r'^$', views.current_map, name='current_map'),
    # url(r'^about$', views.about, name='about'),
]