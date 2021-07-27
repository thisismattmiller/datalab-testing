from django.urls import include, path
from django.views.generic import TemplateView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
     path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('img/favicon.ico'))),
    path('datalab/search/', views.search, name='search-blog'),
    path('datalab/about/', views.about, name='about'),
    path('datalab/contact/', views.contact, name='contact'),
    path('datalab/experiments/chdl-0007/', views.chdl0007, name='chdl-0007'),
    path('datalab/experiments/chdl-0001-d/', views.chdl0001d, name='chdl-0001-d'),
    path('datalab/experiments/chdl-0001-c/', views.chdl0001c, name='chdl-0001-c'),
    path('datalab/experiments/chdl-0002/', views.beethovenCount, name='beethovenCount'),
    path('datalab/experiments/chdl-0003/', views.firstVienneseSchool, name='firstVienneseSchool'),
    path('datalab/experiments/chdl-0004/', views.threeBs, name='threeBs'),
    path('datalab/experiments/chdl-0005/', views.grammyWinners, name='grammyWinners'),
    path('datalab/experiments/chdl-0006/', views.genreChart, name='genreChart'),
    path('datalab/experiments/chdl-0008/', views.may5, name='may5'),
    path('datalab/experiments/chdl-0009/', views.top25, name='top25'),
    path('datalab/experiments/chdl-0010/', views.leschetizky, name='leschetizky'),
    path('datalab/experiments/chdl-0011/', views.chdl0011, name='chdl-0011'),
    path('datalab/experiments/', views.experiments, name='experiments'),
    path('datalab/labReport_create/', views.LabReportCreateView.as_view(),
         name='labReport_create'),
    path('datalab/labReport_list/', views.LabReportListView.as_view(),
         name='labReport_list'),
    path('datalab/labReport/<int:pk>', views.LabReportDetailView.as_view(),
         name='labReport_detail'),
    path('datalab/yearForm/', views.yearForm, name='yearForm'),
]
