from django.conf.urls import url
from user import views


urlpatterns = [
    url(r'^register/',views.register),
    url(r'^loginin/',views.loginin),
    url(r'^logoutt/',views.logoutt),
    url(r'^submit_info/',views.submit_info),
    url(r'^base0/',views.base0),
    url(r'^user_center_info/$',views.user_center_info),
    url(r'^user_center_order/$',views.user_center_order),
    url(r'^commit_1/',views.commit_1),
    url(r'^user_center_site/$',views.user_center_site),
    url(r'^user_info/',views.user_info),
    url(r'^active/(?P<token>.*)/',views.active),#激活链接，携带用户id，便于更改数据库中该用户is_active状态

]
