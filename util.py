# -*- encoding:utf-8 -*-
import os
import datetime
import json  
import urllib2  
import time
def comma_delimit_reader(path, is_skip = True, sep=','):
    output = []
    if not os.path.exists(path):
        raise Exception("The file %s does not exists" % path)
        
    with open(path) as f:
        for line in f:
            if line.strip('\n')=='':
                continue
            if is_skip:
                is_skip = False
                continue
            output.append(line.strip('\n').split(sep))
    return output
    
def task_execute_check(run_date, cycle, param):
    date = datetime.datetime.strptime(run_date, "%Y-%m-%d")
    
    if cycle == 'o':
        dates = param.split(";")
        for date in dates:
            if date == run_date:
                return True
    elif cycle=='w':
        weekday = date.weekday()
        for wds in param.split(';'):
            if weekday == (int(wds)-1): # 周日=0，周日=6
                return True
    elif cycle=='m':
        monthday = date.day
        for dts in param.split(";"):
            if monthday == int(dts):
                return True
    elif cycle=='s':
        ms, ds = date.strftime("%m-%d").split('-')
        if int(ms) in [1,4,7,10]:
            if ds in param.split(';'):
                return True
    elif cycle=='y':
        md = date.strftime("%m-%d")
        for mds in param.split(";"):
            if mds == md:
                return True
    else:
        raise Exception("%s is not a valid crontab cycle" % cycle)
    
    return False

def get_season_month(month):    
    if month <=3:
        season_month = 1
    elif month>3 and month<=6:
        season_month = 4
    elif month>6 and month<=9:
        season_month = 7
    elif month>9 and month<=12:
        season_month = 10
    return season_month

    
def get_time_reference(run_date):
    current_year = int(run_date.split('-')[0])
    current_month = int(run_date.split('-')[1])    
    
    month_begin_date = find_first_workday_after(current_year, current_month, 1)
    month_middle_date = find_first_workday_after(current_year, current_month, 15)
    season_month = get_season_month(current_month)
    season_begin_date = find_first_workday_after(current_year, season_month, 1)

    reference ={
        u"每月月初":month_begin_date,
        u"每月月中":month_middle_date,
        u"每季季初":season_begin_date,
    }
    return reference
    
def read_time_msg(time_msg, reference):
    
    if time_msg in [u'每月月初',u'每月月中',u'每季季初']:
        freq = 'o';
        day = reference[time_msg]
    elif time_msg == 'NA':
        freq = 'o'; day = '9999-99-99'
    else:
        if '-' in time_msg:
            segs = time_msg.split('-')
            if len(segs)==2:
                freq = 'y'
                day = time_msg
            elif len(segs) == 3:
                freq = 'o'
                day = time_msg
            else:
                raise Exception('日期必须为MM-DD或者YYYY-MM-DD')
        else:
            raise Exception('时间标签必须为“每月月初”，“每月月中”，“每季季初”，日期(MM-DD,YYYY-MM-DD)或者NA')
    return freq, day

def find_first_workday_after(year, month, day):
    test_date = datetime.date(year, month, day)
    if is_workday(test_date.strftime("%Y%m%d")):
        return test_date.strftime("%Y-%m-%d")
    
    is_wkd = False
    while not is_wkd:
        test_date = test_date + datetime.timedelta(days=1)
        #print(test_date.strftime("%Y%m%d"))
        #time.sleep(0.1)
        is_wkd = is_workday(test_date.strftime("%Y%m%d"))
        
    return test_date.strftime("%Y-%m-%d")
    
def is_workday(date):
    # YYYYMMDD
    server_url = "http://api.goseek.cn/Tools/holiday?date="  
    vop_url_request = urllib2.Request(server_url+date)  
    vop_response = urllib2.urlopen(vop_url_request)  
    vop_data= json.loads(vop_response.read())  
      
    #print vop_data  
      
    if vop_data[u"data"]==0:  
        return True  
    elif vop_data[u"data"]==1:  
        return False  
    elif vop_data[u"data"]==2:  
        return False  
    else:  
        raise Exception("cannot find the work day status of %s"%date)  
    
def get_role_org_ref(role_name, role_dict, role_org_ref):
    if role_name not in role_dict:
        raise Exception(u'角色定义必须是支部书记，组织委员，党员，党小组组长或者处长')
    role_id = role_dict[role_name]
    if role_id not in role_org_ref:
        raise Exception(u'%s 没有组织' % role_id)
    org_ids = role_org_ref[role_id]
    
    return role_id, org_ids
