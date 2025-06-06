from django.db import models

class Colleges(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('学院名称',  max_length=32, null=False)
    createTime = models.CharField('建立时间', db_column='create_time', max_length=19)
    class Meta:
        db_table = 'colleges'

class Majors(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('专业名称',  max_length=32, null=False)
    createTime = models.CharField('建立时间', db_column='create_time', max_length=19)
    college = models.ForeignKey(Colleges, on_delete=models.CASCADE, db_column='college_id')
    class Meta:
        db_table = 'majors'

class Class(models.Model):
    class_id = models.AutoField('班级编号', primary_key=True)
    class_name = models.CharField('班级名称', max_length=32, null=False)
    major = models.ForeignKey(Majors, on_delete=models.CASCADE, db_column='major_id')
    class Meta:
        db_table = 'class'

class Companies(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('企业名称', max_length=30, null=False)
    introduce = models.CharField('公司简介', max_length=200, null=False,default="公司创立于2000年,是行业领先的基础设施和智能终端供应商。")
    phone = models.CharField('联系电话', max_length=11, null=False)
    address = models.CharField('联系地址', max_length=64, null=False)
    class Meta:
        db_table = 'companies'

class Jobs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('岗位名称', max_length=30, null=False)
    duty = models.CharField('岗位职责', max_length=125, null=False)
    ask = models.CharField('岗位要求', max_length=125, null=False)
    company = models.ForeignKey(Companies, db_column='company_id', on_delete=models.CASCADE)
    class Meta:
        db_table = 'jobs'

class Users(models.Model):
    id = models.AutoField('用户id', primary_key=True)
    userName = models.CharField('用户账号', db_column='user_name', max_length=32, null=False)
    passWord = models.CharField('用户密码', db_column='pass_word', max_length=32, null=False)
    name = models.CharField('用户姓名', max_length=20, null=False)
    gender = models.CharField('用户性别', max_length=4, null=False)
    age = models.IntegerField('用户年龄', null=False)
    phone = models.CharField('联系电话', max_length=11, null=False)
    type = models.IntegerField('用户身份', null=False)
    class Meta:
        db_table = 'users'

class Students(models.Model):
    id = models.CharField('学生学号', max_length=20, primary_key=True)
    address = models.CharField('学生籍贯', max_length=64, null=False)
    birthday = models.CharField('出生日期', max_length=10, null=False)
    status = models.IntegerField('学生状态', null=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='user_id')  # 外键关联用户表
    college = models.ForeignKey(Colleges, on_delete=models.CASCADE, db_column='college_id') # 外键关联Colleges表
    major = models.ForeignKey(Majors, on_delete=models.CASCADE, db_column='major_id') # 外键关联Majors表
    # 新增字段
    phone_number = models.CharField('联系电话', max_length=11, null=False)
    name = models.CharField('姓名', max_length=20, null=False)
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_column='class_id')
    gender = models.CharField('用户性别', max_length=4,default='女', null=False)
    class Meta:
        db_table = 'students'
# 新增班级表

class TripartiteInfo(models.Model):
    company_location = models.CharField(max_length=200, verbose_name='公司所在地')
    company_scale = models.CharField(max_length=100, verbose_name='公司规模')
    salary = models.CharField(max_length=50, verbose_name='薪资')
    position_name = models.CharField(max_length=100, verbose_name='岗位名称')
    position_category = models.CharField(max_length=100, verbose_name='岗位类别')
    company_category = models.CharField(max_length=100, verbose_name='公司类别')
    school = models.CharField(max_length=200, verbose_name='学生所在学校')
    college = models.CharField(max_length=200, verbose_name='学院')
    major = models.CharField(max_length=200, verbose_name='专业名称')
    student_name = models.CharField(max_length=100, verbose_name='学生姓名')
    student_id_card = models.CharField(max_length=18, verbose_name='学生身份证号')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, verbose_name='学生')
    status = models.CharField(max_length=20, default='待审核', verbose_name='审核状态')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tripartite_info'
        verbose_name = '三方信息'
        verbose_name_plural = verbose_name

class EducationLogs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('学校名称', max_length=20, null=False)
    startTime = models.CharField('开始时间', max_length=10, null=False)
    endTime = models.CharField('结束时间', max_length=10, null=False)
    student = models.ForeignKey(Students, on_delete=models.CASCADE, db_column='student_id')
    class Meta:
        db_table = 'education_logs'

class ProjectLogs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    name = models.CharField('项目名称', max_length=20, null=False)
    duty = models.CharField('工作职责', max_length=64, null=False)
    detail = models.CharField('项目详情', max_length=64, null=False)
    student = models.ForeignKey(Students, on_delete=models.CASCADE, db_column='student_id')
    class Meta:
        db_table = 'project_logs'

class SendLogs(models.Model):
    id = models.AutoField('记录编号', primary_key=True)
    snedTime = models.CharField('发送时间', db_column='sned_time', max_length=19, null=False)
    status = models.IntegerField('处理状态', null=False)
    job = models.ForeignKey(Jobs, on_delete=models.CASCADE, db_column='job_id')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, db_column='student_id')
    class Meta:
        db_table = 'send_logs'  #

# studentYC/app/models.py
from django.db import models
from .models import Students  # 假设 Students 模型已定义

class TripartiteInfo(models.Model):
    company_location = models.CharField(max_length=200, verbose_name='公司所在地')
    company_scale = models.CharField(max_length=100, verbose_name='公司规模')
    company_name = models.CharField(max_length=200, default='西安腾讯云计算有限公司',verbose_name='公司名称')
    salary = models.CharField(max_length=50, verbose_name='薪资')
    position_name = models.CharField(max_length=100, verbose_name='岗位名称')
    position_category = models.CharField(max_length=100, verbose_name='岗位类别')
    company_category = models.CharField(max_length=100, verbose_name='公司类别')
    school = models.CharField(max_length=200, verbose_name='学生所在学校')
    college = models.CharField(max_length=200, verbose_name='学院')
    major = models.CharField(max_length=200, verbose_name='专业名称')
    student_name = models.CharField(max_length=100, verbose_name='学生姓名')
    student_id_card = models.CharField(max_length=18, verbose_name='学生身份证号')
    student = models.ForeignKey(Students, on_delete=models.CASCADE, verbose_name='学生')
    status = models.CharField(max_length=20, default='待审核', verbose_name='审核状态')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    class_id = models.ForeignKey(Class, on_delete=models.CASCADE, db_column='class_id', verbose_name='班级')
    class_name = models.CharField(max_length=20, default='计算机214', db_column='class_name', verbose_name='所在班级')
    gender = models.CharField(max_length=20, default='西安腾讯云计算有限公司',verbose_name='性别')
    phone_number = models.IntegerField(verbose_name='电话')
    class Meta:
        db_table = 'tripartite_info'

