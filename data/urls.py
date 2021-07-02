"""chlod URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf import settings


from . import views

urlpatterns = [
    url(r'^$', views.route_homepage),
    url(r'^admin/', admin.site.urls),
    url(r'^works/(?P<id>[0-9]+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_works),
    url(r'^works/(?P<id>[0-9]+)', views.route_works),
    url(r'^events/(?P<id>[0-9]+)/work_(?P<product_id>[0-9]+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_products),
    url(r'^events/(?P<id>[0-9]+)/work_(?P<product_id>[0-9]+)', views.route_products),
    url(r'^events/(?P<id>[0-9]+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_events),
    url(r'^events/(?P<id>[0-9]+)', views.route_events),
    url(r'^venues/(?P<id>[0-9]+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_venues),
    url(r'^venues/(?P<id>[0-9]+)', views.route_venues),
    url(r'^names/(?P<id>[0-9]+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_names),
    url(r'^names/(?P<id>[0-9]+)', views.route_names),
    url(r'^instruments/(?P<id>[0-9]+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_instruments),
    url(r'^instruments/(?P<id>[0-9]+)', views.route_instruments),
    url(r'^roles/(?P<id>[0-9]+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_roles),
    url(r'^roles/(?P<id>[0-9]+)', views.route_roles),
    url(r'^ensembles/(?P<id>[0-9]+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_ensembles),
    url(r'^ensembles/(?P<id>[0-9]+)', views.route_ensembles),
    url(r'^genres/(?P<id>[0-9]+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_genres),
    url(r'^genres/(?P<id>[0-9]+)', views.route_genres),
    # url(r'^sparql/select', views.route_sparql_query),
    url(r'^sparql/', views.route_sparql),
    url(r'^void/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_void),
    url(r'^void/', views.route_void),
    url(r'^vocabulary/roles/$', views.route_vocab_role),
    url(r'^vocabulary/roles/(?P<type>about|xml|turtle|jsonld|nt|n3)$', views.about_vocab_role),
    url(r'^vocabulary/roles/(?P<id>(?!(about|xml|turtle|jsonld|nt|n3))\w+)/(?P<type>about|xml|turtle|jsonld|nt|n3)', views.about_vocab_roles),
    url(r'^vocabulary/roles/(?P<id>(?!(about|xml|turtle|jsonld|nt|n3))\w+)', views.route_vocab_roles)

]
