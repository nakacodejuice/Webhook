from django.conf.urls import include, url
from django.urls import path
from django.contrib import admin
admin.autodiscover()

import viberapp.views

# Examples:
# url(r'^$', 'gettingstarted.views.home', name='home'),
# url(r'^blog/', include('blog.urls')),

urlpatterns = [
    #path(r'$', viberapp.views.index, name='index'),
    path(r'viber/', viberapp.views.viber, name='viber'),
    path(r'telegram/', viberapp.views.telegram, name='telegram'),
    path(r'log/', viberapp.views.log, name='log'),
    path(r'RNG/', viberapp.views.RNG, name='RNG'),
    path(r'viberfiles/', viberapp.views.viberfiles, name='viberfiles'),
    path(r'admin/', admin.site.urls),
]
