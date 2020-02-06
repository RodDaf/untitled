from django.shortcuts import render,HttpResponse,redirect
from goods.models import *
import time
from django.core.paginator import Paginator
from django.contrib.auth import authenticate
from django_redis import get_redis_connection
from tt import tt


# from redis import *
# sr = StrictRedis(host='',port=6379,db=0,password=123)
# sr.lpush(111,222)




#首页
def indexs(request):
    #主页购物车后数字
    lenght = tt.get_car_lenght(request.user.id)

    #先进行排序，取四张轮播的图片
    banner_a = IndexGoodsBanner.objects.all().order_by("index")[0:4]

    #广告促销
    banner_b = IndexPromotionBanner.objects.all().order_by("index")[0:2]

    #商品种类
    banner_c = GoodsType.objects.all()

    #商品sku---是标题还是图片
    # banner_d = IndexTypeGoodsBanner.objects.all()
    print('*'*20)
    print("首页页面信息获取成功")
    return render(request,'index.html',locals())

#商品列表
def list(request,type_id,index):
    #主页购物车后数字
    lenght = tt.get_car_lenght(request.user.id)

    #商品分类
    type_id2 = GoodsType.objects.get(id=type_id)
    #当前种类下的所有商品
    goods_sku = GoodsSKU.objects.filter(type=type_id2)
    # goods_sku2 = GoodsSKU.objects.get(type=type_id2)
    #新品推荐
    new_goods = GoodsSKU.objects.filter(type=type_id2).order_by('-create_time')[:2]
    banner_c = GoodsType.objects.all()


    sort = request.GET.get('sort')
    if sort == 'id':
    #默认（id） 排序
        goods_sku = GoodsSKU.objects.filter(type=type_id2).order_by('id')
    elif sort == 'price':
    # 价格 排序
        goods_sku = GoodsSKU.objects.filter(type=type_id2).order_by('price')
    else:
    #人气（销量）排序
        goods_sku = GoodsSKU.objects.filter(type=type_id2).order_by('-sales')


    # # 将种类商品按一页1条进行分页
    # p = Paginator(goods_sku,1)
    # #返回总页数
    # p_nums = Paginator.num_pages
    # #返回页码列表
    # p_range = Paginator.page_range
    # #如果大于总页数，返回最后一页，小于的话返回第一个
    # aaa = p_nums if int(pag) > p_nums else pag
    #
    # page = Paginator.page(pag)
    #分页
    paginator = Paginator(goods_sku,2)
    page_nums = paginator.num_pages
    page_range = paginator.page_range
    index = page_nums if int(index) > page_nums else index
    page = paginator.page(index)

    print('*' * 20)
    print("商品列表获取数据成功，分页成功")
    return render(request,'list.html',locals())

#商品详情
def detail(request,id):
    #主页购物车后数字
    lenght = tt.get_car_lenght(request.user.id)

    aaa = id
    goods_sku = GoodsSKU.objects.get(id=aaa)
    name = goods_sku.name     #名字----
    desc = goods_sku.desc     #简介----
    price = goods_sku.price   #价钱----
    unite = goods_sku.unite   #单位----
    stock = goods_sku.stock   #库存
    sales = goods_sku.sales   #销售量
    status = goods_sku.status #商品状态

    detail = goods_sku.goods.detail #查看商品详情
    try:
        goods_image = GoodsImage.objects.get(sku__id=aaa)
        image = goods_image.image    #找商品图片
    except:
        None


    new_goods = GoodsSKU.objects.filter(type=goods_sku.type).order_by('-create_time')[:2]


    if request.user.is_authenticated():
        # 视图中手动连接redis 需要导包get_redis_connection
        rr = get_redis_connection("default")
        # 获取用户id
        history_key = 'history_%s' % request.user.id

        # 先删除在添加，防止重复数据
        rr.lrem(history_key, 0, goods_sku.id)

        # 添加用户浏览记录
        rr.lpush(history_key, goods_sku.id)
    print('*' * 20)
    print("商品详情获取成功")
    return render(request,'detail.html',locals())


