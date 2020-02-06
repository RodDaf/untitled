from django.shortcuts import render,HttpResponse,redirect
from django.http import JsonResponse   #ajax请求时返回JsonResponse
from django_redis import get_redis_connection
from goods.models import GoodsSKU

#取redis购物车数据
def car(request):
    tt = get_redis_connection('default')

    #当前用户的购物车   键
    key = "car_%s"%request.user.id
    lenght = tt.hlen(key)

    #得到当前用户key的所有  属性和值
    user_car_key = tt.hgetall(key)
    car_list = []
    for sku_id,count in user_car_key.items():
        #从redis中的商品id查询goods中商品，，得到商品对象
        goods_obj = GoodsSKU.objects.get(id=int(sku_id.decode('utf-8')))
        goods_obj.count = count.decode('utf-8')
        car_list.append(goods_obj)
    print("*"*20)
    print("获取购物车redis商品数据成功")
    return render(request,'cart.html',locals())

#redis添加购物车数据
def goods_car_add(request):
    goods_id = request.POST.get("id")
    goods_count = request.POST.get("count")
    if request.user.is_authenticated:               #判断当前是否又用户登录
        tt = get_redis_connection('default')
        #进行redis存储 hash   key：   field  value
                            #用户id  商品id  商品数量
        #拼接key
        car_id = 'car_%s'%request.user.id
        sku_count = tt.hget(car_id,goods_id)
        if sku_count is None:
            tt.hset(car_id,goods_id,goods_count)

            lenghts = tt.hlen(car_id)

            # key = 'car_%s' % request.user.id
            # request.session['car_lenght'] = tt.hlen(key)

            print('*'*20)
            print('购物车添加成功')
        else:
            count = int(sku_count.decode('utf-8')) + int(goods_count)

            tt.hset(car_id, goods_id, count)
            lenghts = tt.hlen(car_id)

            # key = 'car_%s' % request.user.id
            # request.session['car_lenght'] = tt.hlen(key)


            print('*' * 20)
            print('购物车添加成功')

        return JsonResponse({'manage':'添加成功','code':1,'car_lenght':lenghts})
    else:
        return JsonResponse({'manage':'用户未登录','code':0 })

#删除购物车商品
def goods_car_del(request,sku_id):
    #根据当前商品id删除redis中的商品
    goods_car_del = get_redis_connection('default')

    #redid删除，，，hdel  键  属性  值
    key = "car_%s"%request.user.id
    goods_car_del.hdel(key,sku_id)
    print("购物车商品删除成功")
    return redirect('/cart/car/')

#普通删除，刷新页面
def cart_delete_ajax(request):
    # 根据当前商品id删除redis中对应的数据。
    tt = get_redis_connection("default")
    car_id = request.POST.get('car_id')
    key = "car_%d" % request.user.id
    tt.hdel(key,car_id)
    print('*'*20)
    print('ajax删除成功')
    return JsonResponse({"msg":"删除成功"})

#加减号进行redis中数据更新
def cart_update(request):
    sku_id = request.POST.get('sku_id')
    count = request.POST.get('count')
    tt = get_redis_connection('default')
    key = 'car_%s'%request.user.id
    tt.hset(key,sku_id,count)
    print('加减号数据更新成功')
    return JsonResponse({'code':'1','mag':'数据更新成功'})




