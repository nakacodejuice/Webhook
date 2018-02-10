from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

import viberapp.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    url(r'^$', viberapp.views.index, name='index'),
    url(r'^viber/', viberapp.views.viber, name='viber'),
    url(r'^telegram/', viberapp.views.telegram, name='telegram'),
    url(r'^log/', viberapp.views.log, name='log'),
    url(r'^RNG/', viberapp.views.RNG, name='RNG'),
    url(r'^viberfiles/', viberapp.views.viberfiles, name='viberfiles'),
    url(r'^admin/', include(admin.site.urls)),
]
