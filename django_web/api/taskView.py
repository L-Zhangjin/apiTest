# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django_web.models import Project,Env,task,taskCase
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db.models import Q
from django_web.models import Env,Project,Case,AutoApiCase,autoApiHead,autoAPIParameter,task,taskCase,AutoTaskRunTime
from django.shortcuts import render
import json,re
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django_web.api import Public
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.events import EVENT_JOB_EXECUTED,EVENT_JOB_ERROR,EVENT_SCHEDULER_PAUSED,EVENT_SCHEDULER_SHUTDOWN
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
jobstores = {
       'default': SQLAlchemyJobStore(url='mysql://root:yhh12345678@localhost/autoapi')
       # 'default': SQLAlchemyJobStore(url='mysql+mysqlconnector://root:yhh12345678@localhost/autoapi')
   }
executors = {
       'default': ThreadPoolExecutor(20),
       'processpool': ProcessPoolExecutor(5),
    }
job_defaults = {
       'coalesce': True,
       'max_instances': 10,
   }
# scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
scheduler= BackgroundScheduler()
try:
    logging.basicConfig(
        level=logging.DEBUG,  # 控制台打印的日志级别
        filename='taskRun.log',
        filemode='w',  ##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
        # a是追加模式，默认如果不写的话，就是追加模式
        format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    )
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    scheduler.shutdown()


def task_index(request):
    return render(request, 'main/task.html')

def taskList(request):
    page = request.GET.get('page', '1')
    rows = request.GET.get('limit', '10')
    i = (int(page) - 1) * int(rows)
    j = (int(page) - 1) * int(rows) + int(rows)
    key = request.GET.get('keyword')
    q1 = Q()
    q1.connector = 'AND'
    if len(key) > 0:
        q1.children.append(('name__contains', key))
    p = task.objects.filter(q1).order_by('-CreateTime')
    resultdict = {}
    total = p.count()
    p = p[i:j]
    dict = []
    for a in p:
        dic = {}
        dic['id'] = a.id
        dic['env_id'] = a.env_id
        r = Env.objects.get(id=a.env_id)
        dic['envName'] = r.env_name
        dic['name'] = a.name
        dic['createTime'] = a.CreateTime.strftime("%Y-%m-%d %H:%M:%S")
        dic['desc'] = a.desc
        dic['user'] = a.user
        dic['type'] = a.type
        dic['status'] = a.status
        dict.append(dic)
    resultdict['code'] = 0
    resultdict['msg'] = ''
    resultdict['count'] = total
    resultdict['data'] = dict
    return JsonResponse(resultdict, safe=False)

def taskDelete(request):
    if request.method == "POST":
        u = json.loads(request.body)
        id=u.get('id')
        task.objects.filter(id=id).delete()
        taskCase.objects.filter(task_id=id).delete()
        resultdict = {
            'code': 0,
            'msg': 'success',
            'data': {'id': id}
        }
        return JsonResponse(resultdict, safe=False)
    else:
        resultdict = {
            'code': 1,
            'msg': '删除失败',
            'data': {}
        }
        return JsonResponse(resultdict, safe=False)

def removeTask(request):
    u = json.loads(request.body)
    tid = u.get('id')
    if scheduler.get_job(str(tid)):
        scheduler.remove_job(str(tid))
        task.objects.filter(id=tid).update(status=2)
        resultdict = {
            'code': 0,
            'msg': 'success',
            'data': {'id': tid}
        }
    else:
        task.objects.filter(id=tid).update(status=2)
        resultdict = {
            'code': 1,
            'msg': '无法终止，请检查任务状态',
            'data': {'id': tid}
        }
    return JsonResponse(resultdict, safe=False)

def caseTaskPost(request):
    if request.method == "POST":
        u = json.loads(request.body)
        print u
        envid =u.get('envid')
        env = Env.objects.get(id=envid)
        if env.evn_port:
            url = env.env_url+':'+env.evn_port
        else:
            url = env.env_url

        cases=u.get('cases')
        user=u.get('user')
        name=u.get('name')
        desc=u.get('desc')
        ty=u.get('type')
        startTime=u.get('startTime')
        endTime=u.get('endTime')
        min = u.get('min')
        hour=u.get('hour')
        day=u.get('day')
        month=u.get('month')
        week=u.get('week')
        print startTime
        print endTime
        t = task.objects.create(name=name, desc=desc, type=ty, startTime=startTime, endTime=endTime, user=user,
                                min=min, hour=hour, day=day, month=month, week=week, CreateTime=timezone.now(),
                                env_id=u.get('envid'))
        t.save()
        tasks = []
        d = re.sub("u'", "\"", cases)
        d = re.sub("'", "\"", d)
        ca = json.loads(d)
        if min=='':
            min=None
        if hour=='':
            hour=None
        if day=='':
            day=None
        if month=='':
            month=None
        if week=='':
            week=None
        if endTime=='':
            endTime=None
        if startTime=='':
            startTime=None

        for c in ca:
            tasks.append(taskCase(task_id=t.id, case_id=c.get('id')))
        taskCase.objects.bulk_create(tasks)
        taskStartTime = timezone.now()
        url = url.encode('unicode-escape').decode('string_escape')

        def job():
            for c in ca:
                api = AutoApiCase.objects.filter(case_id=c.get('id'))
                for i in api:
                    he = autoApiHead.objects.filter(autoApi_id=i.id)
                    pa = autoAPIParameter.objects.filter(autoApi_id=i.id)
                    headers = {}
                    params = {}
                    for p in he:
                        name = p.name
                        value = p.value
                        headers[name] = value
                    for p in pa:
                        name = p.name
                        value = p.value
                        params[name] = value
                    ur = url+ i.apiAddress
                    try:
                        r = Public.execute(url=ur, params=params, method=i.method, heads=headers)
                        print r.text
                    except:
                        print '接口请求出错，请检查'

        def my_listener(event):
            if event.exception:
                print('The job crashed :(')
            else:
                print('运行中')
                task.objects.filter(id=t.id).update(status=1)
                if scheduler.get_job(job_id=str(t.id))==None:
                    task.objects.filter(id=t.id).update(status=2)
                    taskEndTime = timezone.now()
                    AutoTaskRunTime.objects.create(startTime=taskStartTime, endTime=taskEndTime, task_id=t.id)


        ty = int(ty.encode("utf-8"))
        if ty==1:
            print '定时'
            scheduler.add_job(job, 'cron', id=str(t.id), day_of_week=week, hour=hour, minute=min, day=day, month=month)
            scheduler.add_listener(my_listener,EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        else:
            print '循环'
            scheduler.add_job(job, 'cron', id=str(t.id), start_date=startTime, end_date=endTime)
            scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        resultdict = {
            'code': 0,
            'msg': '运行成功',
            'data': {}
        }
        return JsonResponse(resultdict, safe=False)
    else:
        resultdict = {
            'code': 1,
            'msg': 'fail',
            'data': {}
        }
        return JsonResponse(resultdict, safe=False)

def taskRun(request):
    u = json.loads(request.body)
    tid = u.get('id')
    cases = taskCase.objects.filter(task_id=tid)
    tasks = task.objects.get(id=tid)
    ty = tasks.type
    ev= Env.objects.get(id=tasks.env_id)
    taskStartTime = timezone.now()
    if ev.evn_port:
        url = ev.env_url + ':' + ev.evn_port
    else:
        url = ev.env_url
    if tasks.min == '':
        tasks.min = None
    if tasks.hour == '':
        tasks.hour = None
    if tasks.day == '':
        tasks.day = None
    if tasks.month == '':
        tasks.month = None
    if tasks.week == '':
        tasks.week = None
    if tasks.endTime == '':
        tasks.endTime = None
    if tasks.startTime == '':
        startTime = None
    def job():
        for c in cases:
            api = AutoApiCase.objects.filter(case_id=c.case_id)
            for i in api:
                he = autoApiHead.objects.filter(autoApi_id=i.id)
                pa = autoAPIParameter.objects.filter(autoApi_id=i.id)
                headers = {}
                params = {}
                for p in he:
                    name = p.name
                    value = p.value
                    headers[name] = value
                for p in pa:
                    name = p.name
                    value = p.value
                    params[name] = value
                ur = url + i.apiAddress
                try:
                    r = Public.execute(url=ur, params=params, method=i.method, heads=headers)
                    print r.text
                except:
                    print '接口请求出错，请检查'

    def my_listener(event):
        if event.exception:
            print('The job crashed :(')
        else:
            print('运行中')
            print scheduler.get_jobs()
            task.objects.filter(id=tid).update(status=1)
            if scheduler.get_job(job_id=str(tid)) == None:
                task.objects.filter(id=tid).update(status=2)
                taskEndTime = timezone.now()
                AutoTaskRunTime.objects.filter(task_id=tid).update(startTime=taskStartTime, endTime=taskEndTime)

    ty = int(ty.encode("utf-8"))
    if ty == 1:
        print '定时'
        scheduler.add_job(job, 'cron', id=str(tid), day_of_week=tasks.week, hour=tasks.hour, minute=tasks.min,
                          day=tasks.day, month=tasks.month)
        scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    else:
        print '循环'
        print tasks.endTime
        if tasks.endTime>timezone.now():
            scheduler.add_job(job, 'cron', id=str(tid), start_date=tasks.startTime, end_date=tasks.endTime)
            scheduler.add_listener(my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        else:
            resultdict = {
                'code': 1,
                'msg': '无法运行，请检查设置运行时间！',
                'data': {'tid': tid}
            }
            return JsonResponse(resultdict, safe=False)
    resultdict = {
        'code': 0,
        'msg': '运行成功',
        'data': {'tid': tid}
    }
    return JsonResponse(resultdict, safe=False)

def schedule_start():
    try:
        logging.basicConfig(
                    level=logging.DEBUG,#控制台打印的日志级别
                    filename='taskRun.log',
                    filemode='a',##模式，有w和a，w就是写模式，每次都会重新写日志，覆盖之前的日志
                    #a是追加模式，默认如果不写的话，就是追加模式
                    format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                            )
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()

def taskPause(request):
    u = json.loads(request.body)
    tid = u.get('id')
    if scheduler.get_job(str(tid)):
        scheduler.pause_job(str(tid))
        task.objects.filter(id=tid).update(status=3)
        resultdict = {
            'code': 0,
            'msg': 'success',
            'data': {'id': tid}
        }
    else:
        task.objects.filter(id=tid).update(status=2)
        resultdict = {
            'code': 1,
            'msg': '无法暂停，请检查任务状态',
            'data': {'id': tid}
        }
    return JsonResponse(resultdict, safe=False)

def taskResume(request):
    u = json.loads(request.body)
    tid = u.get('id')
    if scheduler.get_job(str(tid)):
        scheduler.resume_job(str(tid))
        task.objects.filter(id=tid).update(status=1)
        resultdict = {
            'code': 0,
            'msg': 'success',
            'data': {'id': tid}
        }
    else:
        task.objects.filter(id=tid).update(status=2)
        resultdict = {
            'code': 1,
            'msg': '无法继续执行，请检查任务状态',
            'data': {'id': tid}
        }
    return JsonResponse(resultdict, safe=False)

def taskEdit(request,tid):
    tasks = task.objects.get(id=tid)
    name = tasks.name
    user = tasks.user
    desc = tasks.desc
    projectId = tasks.project_id
    r = Project.objects.get(id=projectId)
    data = {
        'caseId': eid,
        'name': name,
        'desc': desc,
        'projectId': projectId,
        'user': user,
        'projectName': r.name
    }
    return render(request, 'main/case-edit.html', data)
