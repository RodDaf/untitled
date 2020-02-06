from django.shortcuts import render,HttpResponse,redirect
from goods.models import GoodsSKU,GoodsType,GoodsImage,Goods
from django_redis import get_redis_connection
from user.models import User,Address
import datetime
from orders.models import OrderInfo,OrderGoods
from django.http import JsonResponse
from django.db import transaction
import os
import sys
from django.contrib.auth import authenticate

from alipay import AliPay


from untitled import settings

#购物车结算
def place_order(request):
    #获取默认地址
    default_add_obj = Address.objects.filter(user_id=request.user.id,is_default=True).first()
    if default_add_obj == None:
        default_add_obj_id = '-1'
    else:
        default_add_obj_id = default_add_obj.id


    tt = get_redis_connection("default")
    sku_checkbox = request.POST.getlist("sku_checkbox")  #获取前端cart中复选框选中的商品id

    order_sku_lists =",".join(sku_checkbox)


    order_sku_list = []
    key = 'car_%s'%request.user.id
    sku_count = 0
    sku_price = 0
    for sku_checkboxs in sku_checkbox:
        order_sku_obj = GoodsSKU.objects.get(id=sku_checkboxs)
        count = tt.hget(key,sku_checkboxs)   #redis中获得商品商品数量
        sku_count +=1     #遍历几次得到几件商品

        price = "%.2f" %order_sku_obj.price     #把价格转成小数后来两位
        sku_price += float(price) * int(count)   #商品的总金额

        # # 减少当前商品库存
        # sku_stock = int(order_sku_obj.stock) - int(count)
        # order_sku_obj.stock = sku_stock
        # order_sku_obj.save()

        order_sku_obj.count = count    #给当前对象加上一个属性，实现商品id对应的数量一一对应的关系
        order_sku_list.append(order_sku_obj)
    if sku_price >=100:
        freight = 0
    else:
        freight = 10


    type = 1    #用于前端判断是购物车提交订单

    return render(request,'place_order.html',locals())

#商品详情购买
def place_order2(request,id):
    default_add_obj = Address.objects.filter(user_id=request.user.id, is_default=True).first()
    if default_add_obj is None:
        default_add_obj_id = '-1'
    else:
        default_add_obj_id = default_add_obj.id


    sku_id = id
    order_sku_lists = str(sku_id)
    count = int(request.POST.get('count'))
    price = request.POST.get('price')

    order_sku_list_s = GoodsSKU.objects.get(id=sku_id)
    # order_sku_list = order_sku_list_s.first()

    order_sku_list_s.count = count
    order_sku_list = []
    order_sku_list.append(order_sku_list_s)

    sku_count = 1

    price = "%.2f" %order_sku_list_s.price     #把价格转成小数后来两位
    sku_prices = (float(price) * int(count))
    if sku_prices >=100:     #判断商品大于100免邮费
        freight = 0
        sku_price = (float(price) * int(count))
    else:
        freight = 10
        sku_price = (float(price) * int(count))+freight

    # #减少当前商品库存
    # sku_stock = int(order_sku_list_s.stock) - int(count)
    # order_sku_list_s.stock = sku_stock
    # order_sku_list_s.save()

    type = 0   #用于前端判断是商品详情提交订单


    return render(request,'place_order.html',locals())


#购物车提交订单到数据库
@transaction.atomic
def submit_order(request):
    tt = get_redis_connection('default')
    sku_id =request.POST.get('sku_id')
    addr = request.POST.get('addr')
    freight = request.POST.get('freight')

    sku_id_list = sku_id.split(",")     #商品id列表
    order_id = datetime.datetime.now().strftime('%Y%m%d')+str(request.user.id)+datetime.datetime.now().strftime('%H%M%S')

    zzz = transaction.savepoint()
    #添加商品订单信息表
    order_obj = OrderInfo.objects.create(user_id=request.user.id,
                                         order_id=order_id,
                                         total_count=0,
                                         total_price=0,
                                         transit_price=freight,
                                         addr_id=addr,
                                         )

    key = "car_%s"%request.user.id
    total_price1 = 0
    total_count = 0
    #添加商品单个商品订单表
    for sku_id_tt in sku_id_list:
        count = tt.hget(key,sku_id_tt)
        price_cc = GoodsSKU.objects.get(id=sku_id_tt)
        # count = int(count1.decode('utf-8'))
        price = float("%.2f"%price_cc.price)*int(count)

        total_count += int(count.decode('utf-8'))
        total_price1 += price   #所有商品的总价格

        # 判断当前购物车内商品数量是否大于库存
        stock =int(price_cc.stock)
        if int(total_count) > stock :
            print('*'*10)
            transaction.savepoint_rollback(zzz)
            return JsonResponse({'code': 1, 'msg1': '库存不足'})

        order_sku_obj = OrderGoods.objects.create(order_id=order_id,
                                             sku_id=sku_id_tt,
                                             count=int(count),
                                             price=price
                                             )

        # 减少当前商品库存,增加销量
        sku_stock = stock - int(count)
        price_cc.stock = sku_stock
        price_cc.sales += sku_stock
        price_cc.save()


    total_price = float("%.2f" % total_price1)    #所有商品的总价格
    order_obj.total_count = total_count
    order_obj.total_price = total_price
    order_obj.save()

    #订单提交之后，需要把购物车中的商品信息删除，删除redis中数据
    tt.hdel(key,*sku_id_list)

    return JsonResponse({'msg':1})


#商品详情提交订单到数据库
@transaction.atomic
def submit_order2(request):
    sku_id = request.POST.get('sku_id')
    addr = request.POST.get('addr')
    freight = request.POST.get('freight')
    count = request.POST.get('count')

    # sku_id_list = sku_id.split(",")  # 商品id列表
    order_id = datetime.datetime.now().strftime('%Y%m%d') + str(request.user.id) + datetime.datetime.now().strftime(
        '%H%M%S')

    #事务回滚标记
    zzz = transaction.savepoint()

    # 添加商品订单信息表
    order_obj = OrderInfo.objects.create(user_id=request.user.id,
                                         order_id=order_id,
                                         total_count=0,
                                         total_price=0,
                                         transit_price=freight,
                                         addr_id=addr,
                                         )

    # 添加商品单个商品订单表
    price_cc = GoodsSKU.objects.get(id=sku_id)
    price = float("%.2f" % price_cc.price) * int(count)
    total_count = count
    total_price1 = price  # 所有商品的总价格

    stock = int(price_cc.stock)
    # 判断商品详情表数量是否超出库存
    if int(total_count) > stock:
        print(int(total_count),stock)
        transaction.savepoint_rollback(zzz)
        print('11111')
        return JsonResponse({'code': 1, 'msg1': '库存不足'})

    # 减少当前商品库存,增加销量
    sku_stock = stock - int(count)
    price_cc.stock = sku_stock
    price_cc.sales +=sku_stock
    price_cc.save()



    order_sku_obj = OrderGoods.objects.create(order_id=order_id,
                                              sku_id=sku_id,
                                              count=count,
                                              price=price
                                              )



    total_price = float("%.2f" % total_price1)  # 所有商品的总价格
    order_obj.total_count = total_count
    order_obj.total_price = total_price
    order_obj.save()

    return JsonResponse({'msg': 1})


def pay(request):
    order_id = request.POST.get('order_id')
    price = request.POST.get('price')

    # print(order_id,price)

    alipay = AliPay(
        appid="2016101500690430",
        app_notify_url=None,  # 默认回调url

        #相对路径，不同电脑文件位置不一样
        app_private_key_path=os.path.join(settings.BASE_DIR,'alipay\\private_2048.txt'),
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path=os.path.join(settings.BASE_DIR,'alipay\\public_2048.txt'),

        sign_type="RSA2",  # RSA 或者 RSA2
        debug = True,  # 默认False
    )

    #把商品信息发送到支付宝，需要一个地址
    tt = alipay.api_alipay_trade_page_pay(
        #订单标题
        subject='测试支付',
        #订单编号
        out_trade_no =order_id,
        #商品数量
        total_amount=price,
    )

    #发送到沙箱支付宝的url,使用？的形式进行拼接
    url = "	https://openapi.alipaydev.com/gateway.do?" + tt
    return JsonResponse({"msg":"支付成功","url":url})


import time
def return_msg(request):

    order_id = request.POST.get('order_id')

    if sys.platform == "win32":
        app_private_key_path = os.path.join(settings.BASE_DIR, "alipay\\private_2048.txt")
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path = os.path.join(settings.BASE_DIR, "alipay\\public_2048.txt")
    elif sys.platform == "linux2":
        app_private_key_path = os.path.join(settings.BASE_DIR, "alipay/private_2048.txt")
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path = os.path.join(settings.BASE_DIR, "alipay/public_2048.txt")
    else:
        app_private_key_path =""
        alipay_public_key_path = ""

    alipay = AliPay(
        appid="2016101500690430",
        app_notify_url=None,  # 默认回调url

        #相对路径，不同电脑文件位置不一样
        app_private_key_path=app_private_key_path,
        # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
        alipay_public_key_path=alipay_public_key_path,

        sign_type="RSA2",  # RSA 或者 RSA2
        debug = True,  # 默认False
    )


    order_order = OrderInfo.objects.get(order_id=order_id)
    while True:
        time.sleep(3)
        # #返回值，是一个josn格式的响应字符串----josn格式转化的python字典
        response = alipay.api_alipay_trade_query(out_trade_no = order_id)   # json格式转化的python字典

        print(response)
        print(response.get('trade_status'))
        if response.get("code") == "10000" and response.get('trade_status') == "TRADE_SUCCESS":
            order_order.order_status = '2'
            order_order.save()
            print('*'*20)
            print('支付成功')
            return JsonResponse({"msg":"付款成功",'tt':'1','urll':'http://127.0.0.1:8888/user/user_center_order/'})

        elif response.get("code") == '40004' or (response.get("code" == "10000" ) and response.get('trade_status') == "WAIT_BUYER_PAY"):
            print('*' * 20)
            print('支付失败')
            continue
