from django.shortcuts import render,HttpResponse,redirect
import re
from user import models as user_models
from itsdangerous import TimedJSONWebSignatureSerializer as TS
from django.conf import settings            #邮箱导包
from django.core.mail import send_mail      #发送邮件--邮箱导包
from django.http import HttpResponse        #邮箱导包
from django.contrib.auth import authenticate,login,logout
from untitled.settings import BASE_DIR
from django_redis import get_redis_connection
from goods import models as gos_models
from django_redis import get_redis_connection
from orders.models import *

#继承base界面
def base0(request):
    return render(request,'base0.html')

#用户信息
def user_center_info(request):


    rr = get_redis_connection('default')

    history_key = 'history_%s' %request.user.id

    #redis中获取数据 ---得到的是一个商品id集合
    goods_list = rr.lrange(history_key,0,5)

    #用户最近浏览记录 把id对应的商品加入到一个空列表中，然后在前端进行遍历，
    history = []

    for aaa in goods_list:
        goods_goods = gos_models.GoodsSKU.objects.get(id=aaa)
        history.append(goods_goods)
    print("最近浏览查询成功")
    return render(request,'user_center_info.html',locals())



#用户订单
def user_center_order(request):

    #获取当前人用户的订单信息
    order = OrderInfo.objects.filter(user_id=request.user.id).order_by("-create_time")


    return  render(request,'user_center_order.html',locals())


#修改默认地址
def commit_1(request):
    if request.method == 'POST':
        tt_id = request.POST.get('sse')
        aa =  user_models.Address.objects.filter(user_id=request.user.id,is_default=True)
        aa.update(is_default=False)   #把当前默认地址修改成0
        tt = user_models.Address.objects.get(id=tt_id)
        tt.is_default = True
        tt.save()
        return redirect('/user/user_center_site/')


#用户地址
def user_center_site(request):
    if request.method == 'GET':
        try:
            add_ob = user_models.Address.objects.get(user_id=request.user.id,is_default=True)
            a1 = add_ob.receiver
            a2 = add_ob.addr
            a3 = add_ob.phone
            return render(request, 'user_center_site.html', {'q1': a1, 'q2': a2, 'q3': a3})
        except:
            return render(request, 'user_center_site.html')

    else:
        receiver_name = request.POST.get('rename')
        receiver_addr = request.POST.get('readdr')
        receiver_zip_code = request.POST.get('zip_code')
        receiver_phone = request.POST.get('phone')


        if not all([receiver_name,receiver_addr,receiver_phone]):
            return render(request,'user_center_site.html',{'error1':'请填写完整信息'})
        if not re.match(r'^1[3|4|5|6|7|8][0-9]{9}$',receiver_phone):
            return render(request,'user_center_site.html',{'error2':'手机号码格式错误'})



        add_1 = user_models.Address.objects.filter(user_id=request.user.id)
        if len(add_1) == 1:
            user_models.Address.objects.create(receiver=receiver_name,addr=receiver_addr,phone=receiver_phone,
                                   zip_code=receiver_zip_code,user_id=request.user.id)
        else:
            user_models.Address.objects.create(receiver=receiver_name, addr=receiver_addr, phone=receiver_phone,
                                   zip_code=receiver_zip_code, user_id=request.user.id,is_default=True)
        return render(request,'user_center_site.html')




#注册
def register(request):
    if request.method == 'GET':

        return render(request, 'register.html')

    else:
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        password2 = request.POST.get("cpwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")
        # print(email)
        if not all([username,password,password2,email]):
            return render(request, 'register.html', {'errmsg1': "数据不完整"})

        if password2 != password:
            return render(request, 'register.html', {'errmsg': "两次密码不一致"})


        if not re.match(r"^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$",email):
            return render(request, 'register.html', {'errmsg': "邮箱格式不正确"})


        if not allow == "on":
            return render(request, 'register.html', {'errmsg': "请同意协议"})

        """
        邮箱激活--发送邮件（当前填写的邮箱）--携带用户id
        发送的是一个a链接：http://localhost:8000/user/register/id   点击就能激活
        直接携带数字id是不安全的（防止用户猜到，扰乱数据库），所以要加密
        使用itsdangerous  没有需要安装
        导包--TimedJSONWebSignatureSerializer--可以起个别名
        from itsdangerous import TimedJSONWebSignatureSerializer as TS
        ser = TS('随便一个参数什么都行这里参数越复杂加密越高'，30（有效期30秒）)
        d = 用户id
        ret = ser.dumps(d)  对d用户的id进行加密---有个返回值，就是加密后的密文

        解密
        ser.loads(ret)   解密解的返回的是密文
        """
        user = user_models.User.objects.filter(username=username)
        # user = user_models.User.objects.get(username=username)
        print(')' * 20)
        print(user)
        print(')' * 20)

        if len(user)==1:
            return render(request, 'register.html', {'errmsg5': "用户名已经存在"})
        else:
            user = user_models.User.objects.create_user(username,email,password)

            user.is_active = 0
            user.save()

            ser = TS('aabbccdd',300)

            d = {'user_id':user.id}
            ret = ser.dumps(d)   #返回值是一个字节---加密后的用户id
            # print(ret)

            #给邮箱发送邮件--加密
            #发送链接格式：http://localhost:8000/user/register/+ret.decode()
            recive_mail= [email]
            herf = 'http://localhost:8888/user/active/'+ret.decode()
            attention = '<h1>请点击下边蓝色字进行激活</h1> <a href='+herf+'>请点击我激活用户</a>'
            send_mail('注册激活', '',settings.EMAIL_FROM,recive_mail,html_message=attention)   #收件邮箱,是个列表，所以先定义一个列表
            return render(request,'login.html')

#邮箱激活
def active(request,token):#点击链接传给一个用户--id--是加密操作所以需要解密
    ser = TS('aabbccdd', 300)
    # print(')'*20)
    # print(ser)
    # print(')' * 20)
    try:
        rrrr = ser.loads(token)   #解密后是上边设置的一个字典，使用字典取值   有有效期，有可能报错
        user_id = rrrr['user_id']
        user = user_models.User.objects.get(id=user_id)   #找到用户
        user.is_active = 1    #修改用户is_active状态
        user.save()           #保存
        return render(request,'login.html')
    except:
        return HttpResponse('链接失效')

#登录
def loginin(request):
    if request.method == 'GET':
        get_cookie = request.COOKIES.get('username','')  #如果第一个值取到为None的话会取第二值传入前端
        return render(request, 'login.html',locals())
    elif request.method == 'POST':
        user_name = request.POST.get('username')
        user_pawd = request.POST.get('pwd')
        is_check = request.POST.get('check')

        user = authenticate(username=user_name,password=user_pawd)  #is_active是1的话就会返回一个账户名，不是1的话会返回一个None
        if user is not None:
            if user.is_active:

                tt = get_redis_connection('default')
                key = 'car_%s' % user.id
                request.session['car_lenght'] = tt.hlen(key)

                login(request, user)
                print('*'*20)
                print('登陆成功')
                if is_check:
                    response_obj = redirect('/goods/indexs/')
                    response_obj.set_cookie('username',user_name)
                    print('*'*20)
                    print('已选择记住用户名')
                    return response_obj
                else:
                    return redirect('/goods/indexs/')
            else:

                return HttpResponse('用户未激活')
        else:
            return HttpResponse('用户名或密码错误')



#注销
def logoutt(request):
    logout(request)
    return redirect('/goods/indexs/')


#用户中心
def user_info(requst):
    return render(requst,'user_center_info.html')


#修改用户信息
def submit_info(request):
    aa = user_models.User.objects.get(username=request.user)
    print(aa)
    user_name = request.POST.get('user_name')
    user_sex = request.POST.get('sex')
    user_head1 = request.FILES.get('user_head')

    if user_sex == '女':
        user_sex = 1
    elif user_sex == '男':
        user_sex = 2
    print(1111)
    path = BASE_DIR + '\\media\\head\\' + user_head1.name
    with open(path,'wb') as tt:
        for ff in user_head1.chunks():
            tt.write(ff)
    print(2222)
    aa.head = 'head/' + user_head1.name
    aa.sex = user_sex
    aa.name = user_name
    print(3333)
    aa.save()
    return redirect('/user/user_center_info/')



