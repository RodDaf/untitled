from django_redis import  get_redis_connection


#写base0中购物车后边的数字
def get_car_lenght(user_id):
    key = "car_%s"%user_id
    tt = get_redis_connection('default')
    lenght = tt.hlen(key)
    return lenght