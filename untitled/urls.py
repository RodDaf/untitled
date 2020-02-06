from django.conf.urls import url,include
from django.contrib import admin
from goods import views
urlpatterns = [
    url(r'^$', views.indexs),
    url(r'^admin/', admin.site.urls),
    url(r'^user/',include('user.urls')),
    url(r'^goods/',include('goods.urls')),
    url(r'^cart/',include('cart.urls')),
    url(r'^orders/',include('orders.urls')),
]
