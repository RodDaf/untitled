from django.conf.urls import url
from goods import views



urlpatterns = [
    url(r'^indexs/',views.indexs),
    url(r'^list/(?P<type_id>.*)/(?P<index>\d+)/',views.list),
    url(r'^detail/(?P<id>.*)/',views.detail),

]
