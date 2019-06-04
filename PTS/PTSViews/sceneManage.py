# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from PTS.models import sceneManager
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.db.models import Q
from django_web.api import Public
import json,os
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.conf import settings


def sceneAdd(request):
    return render(request, 'pts/scene-add.html')

def sceneList(request):
    page = request.GET.get('page', '1')
    rows = request.GET.get('limit', '10')
    i = (int(page) - 1) * int(rows)
    j = (int(page) - 1) * int(rows) + int(rows)
    key = request.GET.get('keyword')
    loginName = request.session.get('Username', '')
    q1 = Q()
    q1.connector = 'AND'
    if len(key) > 0:
        q1.children.append(('name__contains', key))
    p = sceneManager.objects.filter(q1, user=loginName).order_by('-CreateTime')
    resultdict = {}
    total = p.count()
    p = p[i:j]
    dict = []
    for a in p:
        dic = {}
        dic['id'] = a.id
        dic['sceneType'] = a.sceneType
        dic['status'] = a.status
        dic['threaduser'] = a.threaduser
        dic['name'] = a.name
        dic['preTime'] = a.preTime
        dic['intervaliTime'] = a.intervaliTime
        dic['updateTime'] = a.updateTime.strftime("%Y-%m-%d %H:%M:%S")
        dict.append(dic)
    resultdict['code'] = 0
    resultdict['msg'] = ''
    resultdict['count'] = total
    resultdict['data'] = dict
    # print resultdict
    return JsonResponse(resultdict, safe=False)