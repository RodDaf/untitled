from django.conf.urls import url
from cart import views


urlpatterns = [
    url(r'^car/',views.car),
    url(r'^goods_car_del/(\d+)',views.goods_car_del),
    url(r'^goods_car_add/',views.goods_car_add),  #加入购物车连接
    url(r'^cart_delete_ajax/',views.cart_delete_ajax),
    url(r'^cart_update/',views.cart_update)
]