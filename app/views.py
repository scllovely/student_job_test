import base64
import json
import re
import time
from django.db import IntegrityError
import requests
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views import View
import pandas as pd
from pyecharts.charts import Bar, Pie
from pyecharts import options as opts
from django.http import JsonResponse
from django.shortcuts import render
from .models import TripartiteInfo
from app import models

import pandas as pd
from django.shortcuts import render
from .models import TripartiteInfo


# 定向到登录页面
def login(request):
    return HttpResponseRedirect('/jobs/login/')


'''
基础处理类，其他处理继承这个类
'''


class BaseView(View):
    '''
    检查指定的参数是否存在
    存在返回 True
    不存在返回 False
    '''

    def isExit(param):

        if (param == None) or (param == ''):
            return False
        else:
            return True

    '''
    转换分页查询信息
    '''

    def parasePage(pageIndex, pageSize, pageTotal, count, data):

        return {'pageIndex': pageIndex, 'pageSize': pageSize, 'pageTotal': pageTotal, 'count': count, 'data': data}

    '''
    转换分页查询信息
    '''

    def parasePage(pageIndex, pageSize, pageTotal, count, data):
        return {'pageIndex': pageIndex, 'pageSize': pageSize, 'pageTotal': pageTotal, 'count': count, 'data': data}

    '''
    成功响应信息
    '''

    def success(msg='处理成功'):
        resl = {'code': 0, 'msg': msg}
        return HttpResponse(json.dumps(resl), content_type='application/json; charset=utf-8')

    '''
    成功响应信息, 携带数据
    '''

    def successData(data, msg='处理成功'):
        resl = {'code': 0, 'msg': msg, 'data': data}
        return HttpResponse(json.dumps(resl), content_type='application/json; charset=utf-8')

    '''
    系统警告信息
    '''

    def warn(msg='操作异常，请重试'):
        resl = {'code': 1, 'msg': msg}
        return HttpResponse(json.dumps(resl), content_type='application/json; charset=utf-8')

    '''
    系统异常信息
    '''

    def error(msg='系统异常'):
        resl = {'code': 2, 'msg': msg}
        return HttpResponse(json.dumps(resl), content_type='application/json; charset=utf-8')


'''
系统请求处理
'''


class SysView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'login':
            return render(request, 'login.html')

        elif module == 'exit':

            del request.session["user"]
            del request.session["type"]

            return HttpResponseRedirect('/jobs/login')

        if module == 'info':

            return SysView.getSessionInfo(request)

        elif module == 'show':
            companies = models.Companies.objects.all()
            return render(request, 'index.html',{'companies': companies})

        elif module == 'sysNum':

            return SysView.getSysNums(request)

    def post(self, request, module, *args, **kwargs):

        if module == 'login':
            return SysView.jwxt_login(request)

        if module == 'info':
            return SysView.updSessionInfo(request)

        if module == 'pwd':
            return SysView.updSessionPwd(request)

    def jwxt_login(request):
        if request.method == "POST":
            userName = request.POST.get("userName")
            passWord = request.POST.get("passWord")

            # 检查用户名是否存在
            user = models.Users.objects.filter(userName=userName).first()
            if not user:
                return JsonResponse({
                    "code": 1,
                    "msg": "账号不存在"
                })

            # 检查密码是否正确
            if user.passWord != passWord:
                return JsonResponse({
                    "code": 1,
                    "msg": "密码不正确"
                })

            # 登录成功，设置session信息
            request.session["user"] = user.id
            request.session["type"] = user.type
            request.session["userName"] = userName

            return JsonResponse({
                "code": 0,
                "msg": "登录成功",
                "type": user.type  # 添加用户类型到响应中
            })

        return render(request, "login.html")

    def getSessionInfo(request):

        user = request.session.get('user')

        data = models.Users.objects.filter(id=user)

        resl = {}
        for item in data:
            resl = {
                'id': item.id,
                'userName': item.userName,
                'passWord': item.passWord,
                'gender': item.gender,
                'name': item.name,
                'age': item.age,
                'phone': item.phone,
                'type': item.type,
            }

        return SysView.successData(resl)

    def getSysNums(request):

        resl = {
            'companiesTotal': models.Companies.objects.all().count(),
            'jobTotal': models.Jobs.objects.all().count(),
            'inStuTotal': models.Students.objects.filter(status=0).count(),
            'outStuTotal': models.Students.objects.filter(status=1).count()
        }

        return BaseView.successData(resl)

    def updSessionInfo(request):

        user = request.session.get('user')

        models.Users.objects.filter(id=user).update(
            userName=request.POST.get('userName'),
            name=request.POST.get('name'),
            age=request.POST.get('age'),
            gender=request.POST.get('gender'),
            phone=request.POST.get('phone'),
        )

        return SysView.success()

    def updSessionPwd(request):

        user = request.session.get('user')

        models.Users.objects.filter(id=user).update(
            passWord=request.POST.get('password'),
        )

        return SysView.success()


'''
学院信息管理
'''


class CollegesView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'colleges.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):

        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.Colleges.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'name': data.name,
            'createTime': data.createTime
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        qruery = Q();

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        data = models.Colleges.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        models.Colleges.objects.create(name=request.POST.get('name'),
                                       createTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                       )

        return BaseView.success()

    def updInfo(self, request):

        models.Colleges.objects.filter(id=request.POST.get('id')) \
            .update(
            name=request.POST.get('name')
        )
        return BaseView.success()

    def delInfo(self, request):

        if models.Students.objects.filter(college__id=request.POST.get('id')).exists():

            return BaseView.warn('存在关联内容无法删除')
        else:
            models.Colleges.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
专业信息管理
'''


class MajorsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'majors.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.Majors.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'name': data.name,
            'createTime': data.createTime,
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        qruery = Q();

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        data = models.Majors.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'name': item.name,
                'createTime': item.createTime
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        models.Majors.objects.create(name=request.POST.get('name'),
                                     createTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                                     )

        return BaseView.success()

    def updInfo(self, request):

        models.Majors.objects.filter(id=request.POST.get('id')) \
            .update(
            name=request.POST.get('name')
        )
        return BaseView.success()

    def delInfo(self, request):

        if models.Students.objects.filter(major__id=request.POST.get('id')).exists():

            return BaseView.warn('存在关联内容无法删除')
        else:
            models.Majors.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
企业信息管理
'''


class CompaniesView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'companies.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.Companies.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'name': data.name,
            'phone': data.phone,
            'address': data.address,
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')

        qruery = Q();

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        data = models.Companies.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'name': item.name,
                'phone': item.phone,
                'address': item.address,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        models.Companies.objects.create(id=int(time.time()),
                                        name=request.POST.get('name'),
                                        phone=request.POST.get('phone'),
                                        address=request.POST.get('address')
                                        )
        return BaseView.success()

    def updInfo(self, request):

        models.Companies.objects.filter(id=request.POST.get('id')) \
            .update(
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            address=request.POST.get('address')
        )
        return BaseView.success()

    def delInfo(self, request):

        if models.Jobs.objects.filter(company__id=request.POST.get('id')).exists():

            return BaseView.warn('存在关联内容无法删除')
        else:
            models.Companies.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
岗位信息管理
'''


class JobsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':

            companies = models.Companies.objects.all().values()

            return render(request, 'jobs.html', {'companies': list(companies)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.Jobs.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'name': data.name,
            'duty': data.duty,
            'ask': data.ask,
            'companyId': data.company.id,
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        companyId = request.GET.get('companyId')

        qruery = Q();

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        if BaseView.isExit(companyId):
            qruery = qruery & Q(company__id=companyId)

        data = models.Jobs.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'name': item.name,
                'duty': item.duty,
                'ask': item.ask,
                'companyId': item.company.id,
                'companyName': item.company.name
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        models.Jobs.objects.create(name=request.POST.get('name'),
                                   duty=request.POST.get('duty'),
                                   ask=request.POST.get('ask'),
                                   company=models.Companies.objects.get(id=request.POST.get('companyId'))
                                   )
        return BaseView.success()

    def updInfo(self, request):

        models.Jobs.objects.filter(id=request.POST.get('id')) \
            .update(
            name=request.POST.get('name'),
            duty=request.POST.get('duty'),
            ask=request.POST.get('ask'),
            company=models.Companies.objects.get(id=request.POST.get('companyId'))
        )
        return BaseView.success()

    def delInfo(self, request):

        if models.SendLogs.objects.filter(job__id=request.POST.get('id')).exists():

            return BaseView.warn('存在关联内容无法删除')
        else:
            models.Jobs.objects.filter(id=request.POST.get('id')).delete()
            return BaseView.success()


'''
用户信息管理
'''


class UsersView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'users.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.Users.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'userName': data.userName,
            'passWord': data.passWord,
            'name': data.name,
            'gender': data.gender,
            'age': data.age,
            'phone': data.phone,
            'type': data.type
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        userName = request.GET.get('userName')
        name = request.GET.get('name')
        phone = request.GET.get('phone')

        qruery = Q(type=1);

        if BaseView.isExit(userName):
            qruery = qruery & Q(userName__contains=userName)

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        if BaseView.isExit(phone):
            qruery = qruery & Q(phone__contains=phone)

        data = models.Users.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'userName': item.userName,
                'passWord': item.passWord,
                'name': item.name,
                'gender': item.gender,
                'age': item.age,
                'phone': item.phone,
                'type': item.type
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        models.Users.objects.create(
            userName=request.POST.get('userName'),
            passWord=request.POST.get('passWord'),
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            age=request.POST.get('age'),
            phone=request.POST.get('phone'),
            type=request.POST.get('type'),
        )
        return BaseView.success()

    def updInfo(self, request):

        models.Users.objects.filter(id=request.POST.get('id')) \
            .update(
            userName=request.POST.get('userName'),
            passWord=request.POST.get('passWord'),
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            age=request.POST.get('age'),
            phone=request.POST.get('phone'),
        )
        return BaseView.success()

    def delInfo(self, request):

        models.Users.objects.filter(id=request.POST.get('id')).delete()
        return BaseView.success()


'''
学生信息管理
'''


class StudentsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':

            colleges = models.Colleges.objects.all().values()
            majors = models.Majors.objects.all().values()
            classes = models.Class.objects.all().values()

            return render(request, 'students.html', {'colleges': list(colleges), 'majors': list(majors), 'classes': list(classes)})
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.Students.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'address': data.address,
            'birthday': data.birthday,
            'status': data.status,
            'collegeId': data.college.id,
            'majorId': data.major.id,
            'classId': data.class_id.class_id
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        userName = request.GET.get('userName')
        name = request.GET.get('name')
        phone = request.GET.get('phone')
        collegeId = request.GET.get('collegeId')
        majorId = request.GET.get('majorId')
        classId = request.GET.get('classId')

        qruery = Q();

        if BaseView.isExit(userName):
            qruery = qruery & Q(user__userName__contains=userName)

        if BaseView.isExit(name):
            qruery = qruery & Q(user__name__contains=name)

        if BaseView.isExit(phone):
            qruery = qruery & Q(user__phone__contains=phone)

        if BaseView.isExit(collegeId):
            qruery = qruery & Q(college__id=collegeId)

        if BaseView.isExit(majorId):
            qruery = qruery & Q(major__id=majorId)
        if BaseView.isExit(classId):
            qruery = qruery & Q(class_id__class_id=classId)

        data = models.Students.objects.filter(qruery)
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'address': item.address,
                'birthday': item.birthday,
                'status': item.status,
                'collegeId': item.college.id,
                'collegeName': item.college.name,
                'classId': item.class_id.class_id,
                'className': item.class_id.class_name,
                'majorId': item.major.id,
                'majorName': item.major.name,
                'userName': item.name,
                'name': item.name,
                'gender': item.gender,
                'age': item.user.age,
                'phone': item.phone_number,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        user = models.Users.objects.create(
            userName=request.POST.get('userName'),
            passWord=request.POST.get('passWord'),
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            age=request.POST.get('age'),
            phone=request.POST.get('phone'),
            type=request.POST.get('type')
        )

        models.Students.objects.create(
            id=request.POST.get('id'),  #
            address=request.POST.get('address'),
            birthday=request.POST.get('birthday'),
            status=request.POST.get('status'),
            college=models.Colleges.objects.get(id=request.POST.get('collegeId')),
            major=models.Majors.objects.get(id=request.POST.get('majorId')),
            user=user,
            phone_number=request.POST.get('phone'),
            name=request.POST.get('name'),
            gender=request.POST.get('gender'),
            class_id=models.Class.objects.get(class_id=request.POST.get('classId'))

        )

        return BaseView.success()

    def updInfo(self, request):

        models.Students.objects.filter(id=request.POST.get('id')) \
            .update(
            address=request.POST.get('address'),
            birthday=request.POST.get('birthday'),
            college=models.Colleges.objects.get(id=request.POST.get('collegeId')),
            major=models.Majors.objects.get(id=request.POST.get('majorId'))
        )

        return BaseView.success()

    def delInfo(self, request):

        student = models.Students.objects.filter(id=request.POST.get('id')).first()

        print(request.GET.get('id'), student);
        models.Users.objects.filter(id=student.user.id).delete()
        models.EducationLogs.objects.filter(student__id=student.id).delete()
        models.ProjectLogs.objects.filter(student__id=student.id).delete()
        models.SendLogs.objects.filter(student__id=student.id).delete()

        student.delete()

        return BaseView.success()


'''
教育经历管理
'''


class EducationLogsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'educationLogs.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.EducationLogs.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'name': data.name,
            'startTime': data.startTime,
            'endTime': data.endTime,
            'studentId': data.student.id,
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        type = request.session.get('type')
        user = request.session.get('user')

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        studentName = request.GET.get('studentName')

        qruery = Q();

        if type == 2:
            student = models.Students.objects.filter(user__id=user).first()
            qruery = qruery & Q(student__id=student.id)

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        if BaseView.isExit(studentName):
            qruery = qruery & Q(student__user__name__contains=studentName)

        if type == 2:
            data = models.EducationLogs.objects.filter(qruery).order_by("-startTime")
            paginator = Paginator(data, pageSize)
        else:
            data = models.EducationLogs.objects.filter(qruery).order_by("student_id")
            paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'name': item.name,
                'startTime': item.startTime,
                'endTime': item.endTime,
                'studentId': item.student.id,
                'studentName': item.student.user.name,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        user = request.session.get('user')

        models.EducationLogs.objects.create(name=request.POST.get('name'),
                                            startTime=request.POST.get('startTime'),
                                            endTime=request.POST.get('endTime'),
                                            student=models.Students.objects.filter(user__id=user).first()
                                            )
        return BaseView.success()

    def updInfo(self, request):

        models.EducationLogs.objects.filter(id=request.POST.get('id')) \
            .update(
            name=request.POST.get('name'),
            startTime=request.POST.get('startTime'),
            endTime=request.POST.get('endTime'),
        )
        return BaseView.success()

    def delInfo(self, request):

        models.EducationLogs.objects.filter(id=request.POST.get('id')).delete()
        return BaseView.success()


'''
项目经历管理
'''


class ProjectLogsView(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'projectLogs.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.ProjectLogs.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'name': data.name,
            'duty': data.duty,
            'detail': data.detail,
            'studentId': data.student.id,
        }

        return BaseView.successData(resl)

    def getPageInfo(self, request):

        type = request.session.get('type')
        user = request.session.get('user')

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        name = request.GET.get('name')
        studentName = request.GET.get('studentName')

        qruery = Q();

        if type == 2:
            student = models.Students.objects.filter(user__id=user).first()
            qruery = qruery & Q(student__id=student.id)

        if BaseView.isExit(name):
            qruery = qruery & Q(name__contains=name)

        if BaseView.isExit(studentName):
            qruery = qruery & Q(student__user__name__contains=studentName)

        data = models.ProjectLogs.objects.filter(qruery)

        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'name': item.name,
                'duty': item.duty,
                'detail': item.detail,
                'studentId': item.student.id,
                'studentName': item.student.user.name,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        user = request.session.get('user')

        models.ProjectLogs.objects.create(name=request.POST.get('name'),
                                          duty=request.POST.get('duty'),
                                          detail=request.POST.get('detail'),
                                          student=models.Students.objects.filter(user__id=user).first()
                                          )
        return BaseView.success()

    def updInfo(self, request):

        models.ProjectLogs.objects.filter(id=request.POST.get('id')) \
            .update(
            name=request.POST.get('name'),
            duty=request.POST.get('duty'),
            detail=request.POST.get('detail'),
        )
        return BaseView.success()

    def delInfo(self, request):

        models.ProjectLogs.objects.filter(id=request.POST.get('id')).delete()
        return BaseView.success()


'''
投递记录管理
'''


class SendLogs(BaseView):

    def get(self, request, module, *args, **kwargs):

        if module == 'show':
            return render(request, 'sendLogs.html')
        elif module == 'info':
            return self.getInfo(request)
        elif module == 'page':
            return self.getPageInfo(request)
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            return self.addInfo(request)
        elif module == 'upd':
            return self.updInfo(request)
        elif module == 'del':
            return self.delInfo(request)
        else:
            return self.error()

    def getInfo(self, request):

        data = models.SendLogs.objects.filter(id=request.GET.get('id')).first()

        resl = {
            'id': data.id,
            'snedTime': data.snedTime,
            'status': data.status,
            'jobId': data.job.id,
            'studentId': data.student.id,
        }

        return self.successData(resl)

    def getPageInfo(self, request):

        type = request.session.get('type')
        user = request.session.get('user')

        pageIndex = request.GET.get('pageIndex', 1)
        pageSize = request.GET.get('pageSize', 10)
        jobName = request.GET.get('jobName')
        studentName = request.GET.get('studentName')

        qruery = Q();

        if type == 2:
            student = models.Students.objects.filter(user__id=user).first()
            qruery = qruery & Q(student__id=student.id)

        if BaseView.isExit(jobName):
            qruery = qruery & Q(job__name__contains=jobName)

        if BaseView.isExit(studentName):
            qruery = qruery & Q(student__user__name__contains=studentName)

        data = models.SendLogs.objects.filter(qruery).order_by("-snedTime")
        paginator = Paginator(data, pageSize)

        resl = []

        for item in list(paginator.page(pageIndex)):
            temp = {
                'id': item.id,
                'snedTime': item.snedTime,
                'status': item.status,
                'jobId': item.job.id,
                'jobName': item.job.name,
                'jobDuty': item.job.duty,
                'companyName': item.job.company.name,
                'studentId': item.student.id,
                'studentName': item.student.user.name,
            }
            resl.append(temp)

        pageData = BaseView.parasePage(pageIndex, pageSize,
                                       paginator.page(pageIndex).paginator.num_pages,
                                       paginator.count, resl)

        return BaseView.successData(pageData)

    def addInfo(self, request):

        user = request.session.get('user')
        jobId = request.POST.get('jobId')
        student = models.Students.objects.filter(user__id=user).first()

        qruery = Q();

        qruery = qruery & Q(job__id=jobId)
        qruery = qruery & Q(student__id=student.id)

        if ((models.EducationLogs.objects.filter(student__id=student.id).exists()) &
                (models.ProjectLogs.objects.filter(student__id=student.id).exists())):

            if models.SendLogs.objects.filter(qruery).exists():

                return BaseView.warn('已投递，请勿重复')
            else:

                models.SendLogs.objects.create(status=request.POST.get('status'),
                                               snedTime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                                               student=student,
                                               job=models.Jobs.objects.filter(id=jobId).first()
                                               )
                return BaseView.success()
        else:

            return BaseView.warn('完善个人项目和教育经历后才可投递简历')

    def updInfo(self, request):

        status = request.POST.get('status')

        if int(status) == 1:

            sendLog = models.SendLogs.objects.filter(id=request.POST.get('id')).first()

            student = models.Students.objects.filter(id=sendLog.student.id).first()

            if student.status == 0:

                models.SendLogs.objects.filter(id=request.POST.get('id')).update(
                    status=request.POST.get('status'),
                )

                models.Students.objects.filter(id=sendLog.student.id) \
                    .update(
                    status=1,
                )

                return BaseView.success()
            else:

                return BaseView.warn('学生已被录取')

        else:
            models.SendLogs.objects.filter(id=request.POST.get('id')) \
                .update(
                status=request.POST.get('status'),
            )
            return BaseView.success()

    def delInfo(self, request):

        models.SendLogs.objects.filter(id=request.POST.get('id')).delete()

        return BaseView.success()


'''
三方信息管理
'''


class TripartiteInfoView(BaseView):
    def get(self, request, module, *args, **kwargs):
        if module == 'show':
            user = request.session.get('user')
            student = models.Students.objects.filter(user__id=user).first()
            tripartite_info = models.TripartiteInfo.objects.filter(student=student)
            # 检查是否有未审核或审核通过的三方信息
            can_add = not models.TripartiteInfo.objects.filter(student=student, status__in=['待审核', '已通过', '未通过']).exists()
            # 检查是否有未通过的三方信息
            has_unapproved = models.TripartiteInfo.objects.filter(student=student, status='未通过').exists()
            unapproved_info = None
            if has_unapproved:
                unapproved_info = models.TripartiteInfo.objects.filter(student=student, status='未通过').first()
            return render(request, 'tripartite_info.html', {
                'tripartite_info': tripartite_info,
                'can_add': can_add,
                'has_unapproved': has_unapproved,
                'unapproved_info': unapproved_info
            })
        elif module == 'add':
            user = request.session.get('user')
            student = models.Students.objects.filter(user__id=user).first()
            # 检查学生是否已有未审核或者审核通过的三方信息
            existing_info = models.TripartiteInfo.objects.filter(student=student, status__in=['待审核', '已通过', '未通过']).exists()
            if existing_info:
                return JsonResponse({'status': 'error', 'message': '您已有未审核或审核通过的三方信息，不可再次填写'})
            tripartite_info = models.TripartiteInfo.objects.filter(student=student)
            return render(request, 'add_tripartite_info.html', {'student': student})
        elif module == 'teacher/show':
            colleges = models.Colleges.objects.all()
            majors = models.Majors.objects.all()
            return render(request, 'teacher_tripartite_info.html', {'colleges': colleges, 'majors': majors})
        elif module == 'page':
            pageIndex = int(request.GET.get('pageIndex', 1))
            pageSize = int(request.GET.get('pageSize', 10))
            collegeId = request.GET.get('collegeId')
            majorId = request.GET.get('majorId')
            keyword = request.GET.get('keyword')

            queryset = models.TripartiteInfo.objects.select_related('student__college', 'student__major').all()
            if collegeId:
                queryset = queryset.filter(student__college_id=collegeId)
            if majorId:
                queryset = queryset.filter(student__major_id=majorId)
            if keyword:
                queryset = queryset.filter(
                    models.Q(student_name__icontains=keyword) |
                    models.Q(company_location__icontains=keyword) |
                    models.Q(position_name__icontains=keyword)
                )

            total_count = queryset.count()
            totalPage = (total_count + pageSize - 1) // pageSize
            start = (pageIndex - 1) * pageSize
            end = start + pageSize
            data_list = queryset[start:end]

            result = []
            for item in data_list:
                result.append({
                    'id': item.id,
                    'student_name': item.student_name,
                    'company_location': item.company_location,
                    'company_name': item.company_name,
                    'company_scale': item.company_scale,
                    'salary': item.salary,
                    'position_name': item.position_name,
                    'position_category': item.position_category,
                    'company_category': item.company_category,
                    'school': item.school,
                    'college_name': item.student.college.name if item.student and item.student.college else '',
                    'major_name': item.student.major.name if item.student and item.student.major else '',
                    'status': item.status,
                })

            data = {
                'list': result,
                'totalPage': totalPage
            }
            return JsonResponse({'code': 0, 'data': data})
        elif module == 'audit':
            id = request.POST.get('id')
            status = request.POST.get('status')
            user = request.session.get('user')
            student = models.Students.objects.filter(user__id=user).first()
            try:
                tripartite_info = models.TripartiteInfo.objects.get(id=id)
                tripartite_info.status = status
                tripartite_info.save()
                return JsonResponse({'code': 0, 'msg': '审核成功'})
            except models.TripartiteInfo.DoesNotExist:
                return JsonResponse({'code': 1, 'msg': '三方信息不存在'})
        elif module == 'edit':
            user = request.session.get('user')
            student = models.Students.objects.filter(user__id=user).first()
            unapproved_info = models.TripartiteInfo.objects.filter(student=student, status='未通过').first()
            return render(request, 'edit_tripartite_info.html', {'info': unapproved_info, 'student': student})
        else:
            return self.error()

    def post(self, request, module, *args, **kwargs):
        if module == 'add':
            user = request.session.get('user')
            student = models.Students.objects.filter(user__id=user).first()
            # 检查学生是否已有未审核或者审核通过的三方信息
            existing_info = models.TripartiteInfo.objects.filter(student=student, status__in=['待审核', '已通过']).exists()
            if existing_info:
                return JsonResponse({'status': 'error', 'message': '您已有未审核或审核通过的三方信息，不可再次填写'})
            models.TripartiteInfo.objects.create(
                company_location=request.POST.get('company_location'),
                company_scale=request.POST.get('company_scale'),
                salary=request.POST.get('salary'),
                position_name=request.POST.get('position_name'),
                position_category=request.POST.get('position_category'),
                company_category=request.POST.get('company_category'),
                school=request.POST.get('school'),
                college=request.POST.get('college'),
                major=request.POST.get('major'),
                class_name=request.POST.get('class_name'),
                gender=request.POST.get('gender'),
                phone_number=request.POST.get('phone_number'),
                student_name=request.POST.get('student_name'),
                student_id_card=request.POST.get('student_id_card'),
                student=student
            )
            return JsonResponse({'status': 'success', 'message': '三方信息提交成功，等待审核'})
        elif module == 'audit':
            return self.get(request, module, *args, **kwargs)
        elif module == 'edit':
            user = request.session.get('user')
            student = models.Students.objects.filter(user__id=user).first()
            unapproved_info = models.TripartiteInfo.objects.filter(student=student, status='未通过').first()
            unapproved_info.company_location = request.POST.get('company_location')
            unapproved_info.company_scale = request.POST.get('company_scale')
            unapproved_info.salary = request.POST.get('salary')
            unapproved_info.position_name = request.POST.get('position_name')
            unapproved_info.position_category = request.POST.get('position_category')
            unapproved_info.company_category = request.POST.get('company_category')
            unapproved_info.school = request.POST.get('school')
            unapproved_info.college = request.POST.get('college')
            unapproved_info.major = request.POST.get('major')
            unapproved_info.class_name = request.POST.get('class_name')
            unapproved_info.gender = request.POST.get('gender')
            unapproved_info.phone_number = request.POST.get('phone_number')
            unapproved_info.student_name = request.POST.get('student_name')
            unapproved_info.student_id_card = request.POST.get('student_id_card')
            unapproved_info.company_name = request.POST.get('company_name')
            unapproved_info.status = '待审核'
            unapproved_info.save()
            return JsonResponse({'status': 'success', 'message': '三方信息修改成功，等待审核'})
        else:
            return self.error()


'''
可视化
'''


class GraduateEmploymentAnalysisView(BaseView):
    def get(self, request, module, *args, **kwargs):
        if module == 'show':
            # 检查用户是否为管理员
            if request.session.get('type') != 0:
                return self.error()

            # 获取三方信息数据
            tripartite_info = TripartiteInfo.objects.all().values()
            df = pd.DataFrame(list(tripartite_info))

            # 获取每个学院的学生人数
            college_stats = models.TripartiteInfo.objects.all().values()
            df2 = pd.DataFrame(list(college_stats))

            # 获取岗位人数
            position_stats = models.TripartiteInfo.objects.all().values()
            df3 = pd.DataFrame(list(position_stats))

            # 数据统计和分析
            location_count = df['company_location'].value_counts()
            type_count = df['company_category'].value_counts()
            college_count = df2['college'].value_counts()
            position_count = df3['position_category'].value_counts()

            # 转换为适合 ECharts 使用的格式
            location_data = [{"name": key, "value": value} for key, value in location_count.items()]
            type_data = [{"name": key, "value": value} for key, value in type_count.items()]
            college_data = [{"name": key, "value": value} for key, value in college_count.items()]
            position_data = [{"name": key, "value": value} for key, value in position_count.items()]

            # 计算总计数量
            location_total = sum(location_count.values)
            type_total = sum(type_count.values)
            college_total = sum(college_count.values)
            position_total = sum(position_count.values)

            context = {
                'location_data': location_data,
                'type_data': type_data,
                'location_total': location_total,
                'type_total': type_total,

                'college_data': college_data,
                'college_total': college_total,
                'position_data': position_data,
                'position_total': position_total,
            }
            print(location_total, type_total, context)
            return render(request, 'analysistest.html', context)

        else:
            return self.error()
