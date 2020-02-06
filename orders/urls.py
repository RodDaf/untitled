from django.conf.urls import url
from orders import views


urlpatterns = [
    url(r'^place_order/$',views.place_order),
    url(r'^place_order2/(\d+)/$',views.place_order2),
    url(r'^submit_order/$',views.submit_order),
    url(r'^submit_order2/$',views.submit_order2),
    url(r'^pay/$',views.pay),
    url(r'^return_msg/$',views.return_msg),

]
