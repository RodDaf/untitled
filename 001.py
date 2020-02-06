from redis import *
from django_redis import get_redis_connection
# sr = StrictRedis(host='192.168.1.3',port=6379,db=0,password='123')
# sr.lpush(1111,2222)

def aa(request):
    rr = get_redis_connection("default")
    rr.set
