# -*- coding: utf-8 -*-
import requests
import json,csv
import codecs
from django_web.models import sqlManager,globalVariable
import MySQLdb
import logging
import sys;
import hashlib
import os
reload(sys);
sys.setdefaultencoding('utf8')



def execute(url, heads, params, method='POST', cookies=None, files=None):
    r = ''
    if files !=None:
        r=requests.request('post', url=url, headers=heads, data=params, cookies=cookies, files=files)
    elif method=='post' and files==None:
        r=requests.request('post', url=url, headers=heads, json=params, cookies=cookies, files=files)
    elif method=='get':
        r=requests.request('get', url=url, headers=heads, json=params, cookies=cookies)
    else:
        print '接口请求方式非法'
    return r

def _load_json_from_response(response):
    try:
        re = json.loads(response)
    except Exception as e:
        raise ValueError('Not a valid JSON\n' + e.message)
    return re

def get_value_from_response(response, json_path=''):
    """get value
    """
    if isinstance(response, (str, unicode)):
        response = _load_json_from_response(response)

    if json_path.find('.') > -1:
        key = json_path[0: json_path.index('.')]
        #print(key)
        if isinstance(response, list) and key.isdigit():
            dict1 = response[int(key)]
        elif isinstance(response, dict):
            dict1 = response.get(key)
            #print(dict1)
        else:
            return response
        key1 = json_path[json_path.index('.') + 1:]
        if key1.find('.') > -1:
            return get_value_from_response(dict1, key1)
        else:
            if isinstance(dict1, list) and key1.isdigit():
                return dict1[int(key1)]
            elif isinstance(dict1, dict):
                return dict1.get(key1)
            else:
                return dict1
    else:
        if isinstance(response, list) and json_path.isdigit():
            return response[int(json_path)]
        elif isinstance(response, dict):
            return response.get(json_path)
        else:
            return response

def write_csv_file(path, head, data):
    try:
        with open(path, 'wb') as csv_file:
            csv_file.write(codecs.BOM_UTF8)
            writer = csv.writer(csv_file, dialect='excel')
            if head is not None:
                writer.writerow(head)
            for row in data:
                writer.writerow(row)
            csv_file.close()
            print("Write a CSV file to path %s Successful." % path)
            logging.info("Write a CSV file to path %s Successful." % path)
    except Exception as e:
        logging.info("Write an CSV file to path: %s, Case: %s" % (path, e))

def excuteSQL(sqlId,sql):
    s = sqlManager.objects.get(id=sqlId)
    try:
        db = MySQLdb.connect(host=s.host, user=s.username, passwd=s.password, db=s.db, port=int(s.port), charset='utf8')
        cursor = db.cursor()
        re=cursor.execute(sql)
    except MySQLdb.Error, e:
        try:
            logging.info("Error %d:%s" % (e.args[0], e.args[1]))
        except IndexError:
            logging.info("MySQL Error:%s" % str(e))
        re =''
    return re

def uploadFileWithPath(File,path):
    resultdict = {}
    resultdict['code'] = 0
    resultdict['msg'] = ''
    if File is None:
        # return "没有需要上传的文件"
        resultdict['code'] = 2
        resultdict['name'] = ''
        resultdict['path'] = ''
    else:
        # with open("./django_web/temp_file/%s" % File.name, 'wb+') as f:
        with open(os.path.join(path, File.name), 'wb+') as f:
            # 分块写入文件
            for chunk in File.chunks():
                f.write(chunk)
        resultdict['name'] = File.name
        resultdict['path'] = os.path.join(path, File.name)
    return resultdict
"""
def qianming(request,jdata):
    sortedParam = sorted(jdata.items(), key=lambda d: d[0])
    paramStr = ''
    for param in sortedParam:
    paramStr = paramStr + str(param[0]) +"="+ str(param[1])+"&"
    print(paramStr)
    rparamStr = paramStr +"key=94fa9e393e1e6a5a73970db38d78c429"
    print(rparamStr)
    result = hashlib.md5(rparamStr.encode("utf-8")).hexdigest()
    return result
"""



