# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from cms.sitemaps import CMSSitemap
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.urls import path, include
from Registro import views
from django.conf.urls.static import static

admin.autodiscover()


urlpatterns = [
    url(r'^sitemap\.xml$', sitemap,
        {'sitemaps': {'cmspages': CMSSitemap}}),
]

app_name = 'detalhe'

urlpatterns += i18n_patterns(
    url('loginSite/', views.login, name='login'),
    url('logout/', views.logout, name='logout'),
    path('', views.RegistroIndex.as_view(), name='index'),
    path('Detalhe/', include('Detalhes.urls')),
    path('Renovacao/', include('Renovacao.urls')),
    path('Usuario/', include('Usuario.urls')),
    url(r'^admin/', admin.site.urls),  # NOQA
    url(r'^', include('cms.urls')),
)

# This is only needed when using runserver.
if settings.DEBUG:
    urlpatterns = [
        url(r'^media/(?P<path>.*)$', serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        ] + staticfiles_urlpatterns() + urlpatterns
