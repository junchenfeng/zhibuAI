#-*- coding:UTF-8 -*-
'''
配置文件
(1)memebers.csv
成员ID，姓名，电话，入党日期，生日

(2)roles.txt
角色ID，定义

(3)orgs.txt
组织ID，定义

(4) role_org_ref
角色ID, 组织ID

(5) role_member_ref
成员ID，组织ID，角色ID

(6) task.txt
任务ID,执行周期,执行时间

(7)task_details.txt
任务ID, 组织ID, 角色ID, 消息模板ID

'''


import os, sys
from collections import defaultdict
from datetime import datetime
from submail.message_xsend import MESSAGEXsend
from submail.app_configs import MESSAGE_CONFIGS
import time
proj_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(proj_dir)
from util import comma_delimit_reader, task_execute_check
    

class tasks(object):
    def __init__(self, task_init_path, task_detail_init_path):
        # 注册任务执行日期
        self.task_crontab_dict={}
        res = comma_delimit_reader(task_init_path)
        for entry in res:
            task_id, task_cycle, crontab_param = entry
            if task_cycle not in ["w","m","s","y","o"]:
                raise Exception(u"任务周期必须为w(每周),m(每月),s(每季),y(每年),o(一次性)。现在是%s" % task_cycle)
            # TODO:增加参数检测
            self.task_crontab_dict[task_id]={'cycle':task_cycle,"param":crontab_param}
        
        # 注册任务执行范围
        self.task_details={}
        res = comma_delimit_reader(task_detail_init_path)
        for entry in res:
            task_id, org_id, role_ids, msg_id = entry
            self.task_details[task_id] = {'org':org_id, 'roles':role_ids.split(';'), 'msg':msg_id}
        
    def get_task_ids(self, date):
        # date必须是YYYY-MM-DD的形式
        task_id_list = []
        for task_id, scheme in self.task_crontab_dict.items():
            if task_execute_check(date, scheme['cycle'], scheme['param']):
                task_id_list.append(task_id)
        return task_id_list

    def get_details(self, task_id):
        details = self.task_details[task_id]
        return details['org'], details['roles'], details['msg']

class birtdayTasks(object):
    def __init__(self, task_detail_init_path):    
        # 注册任务执行范围
        self.task_details={}
        res = comma_delimit_reader(task_detail_init_path)
        for entry in res:
            task_id, msg_id, zw_msg_id = entry
            self.task_details[task_id] = {'zw_msg':zw_msg_id, 'msg':msg_id}
            
    def get_details(self, task_id):
        details = self.task_details[task_id]
        return details['msg'], details['zw_msg']    
        
class members(object):
    def __init__(self, info_path, zw_path):
        self.member_dict = {}
        # 读入个人信息
        res = comma_delimit_reader(info_path)
        for entry in res:
            member_id, member_name, phone_no_str, rudang_date_s, birth_date_s = entry
            phone_no = int(phone_no_str)
            if member_id in self.member_dict:
                raise Exception("%s has duplicates" % member_id)
            if rudang_date_s != '':
                pb_md = datetime.strptime(rudang_date_s, "%Y/%m/%d").strftime("%m-%d")
            else:
                pb_md = ''
            if birth_date_s != '':
                b_md = datetime.strptime(birth_date_s, "%Y/%m/%d").strftime("%m-%d")
            else:
                b_md = ''
            self.member_dict[member_id]={"name":member_name.decode("gbk"),"phone":phone_no,'rudang':pb_md,'birth':b_md}
        
        # 读入组织委员对应关系
        res = comma_delimit_reader(zw_path)
        for entry in res:
            self.member_dict[entry[0]]['zw'] = entry[1]
    
    def get_info(self, member_id):    
        if member_id not in self.member_dict:
            raise Exception("%s is not registered" % member_id)
        return self.member_dict[member_id]
    
    def find_birthday_member(self, date, bd_type):
        ids = []
        if bd_type == 'b':
            key = 'birth'
        elif bd_type ==  'pb':
            key = 'rudang'
        for member_id in self.member_dict:
            if self.member_dict[member_id][key] == datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d"):
                ids.append(member_id)
        return ids
    

    
    def find_zw(self, member_id):
        return self.member_dict[member_id]['zw'].split(';')
    
class roles(object):
    def __init__(self, members, member_role_ref_init_path):
        self.members = members
        self.member_role_ref = {}
        res = comma_delimit_reader(member_role_ref_init_path)
        for entry in res:
            member_id, org_id, role_id = entry
            if org_id not in self.member_role_ref:
                self.member_role_ref[org_id] = defaultdict(list)
            self.member_role_ref[org_id][role_id].append(member_id)
    
    def _get_member_id(self, org_id, role_id):
        return self.member_role_ref[org_id][role_id]
        
    def get_member_info(self, org_id, role_id):
        member_id_list = self._get_member_id(org_id, role_id)
        return [self.members.get_info(member_id) for member_id in member_id_list]
        
class orgs(object):
    def __init__(self, org_init_path):
        self.org_dict = {}
        self.org_tree = defaultdict(list)
        res = comma_delimit_reader(org_init_path)
        for entry in res:
            org_id, org_name, parent_org_id = entry
            self.org_dict[org_id] = org_name.decode('utf-8')
            if parent_org_id != '':
                self.org_tree[parent_org_id].append(org_id)
    
    def get_children(self, org_id):
        children_org_id_list = []
        if len(self.org_tree[org_id]) >= 0:
            for child_id in self.org_tree[org_id]:
                children_org_id_list += self.org_tree[child_id]
        return children_org_id_list
        
class msg_client(object):
    def __init__(self):
        self.client = MESSAGEXsend(MESSAGE_CONFIGS)
    
    def _send(self, msg_id, name, phone_no, date):
        if len(self.client.to) != 0:
            self.client.to = []
        # check if the log exists
        log_file_dir = proj_dir + '/log/%s/' %date
        log_file_path = log_file_dir + '%s.txt' % msg_id
        should_send = True
        if os.path.exists(log_file_path):
            with open(log_file_path) as f:
                for line in f:
                    if line.strip('\n') == '':
                        continue
                    if line.strip('\n').split(',')[1] == str(phone_no):
                        should_send = False
        if should_send:            
            self.client.add_to(str(phone_no))
            self.client.set_project(msg_id)
            self.client.add_var('name',name)
            res = self.client.xsend()
            print(name)
            print(phone_no)
            time.sleep(3)
            if res['status'] == 'success':
                # 增加log
                if not os.path.exists(log_file_dir):
                    os.makedirs(log_file_dir)
                if not os.path.exists(log_file_path):
                    with open(log_file_path, 'w') as f:
                        f.write('%s,%s\n'%(name.encode('utf-8'), phone_no))
                else:
                    with open(log_file_path, 'a') as f:
                        f.write('%s,%s\n'%(name.encode('utf-8'), phone_no))
                
                return True
            else:
                return False
        else:
            return True
        
    def notify(self, task_id, name, phone_no, msg_id, date):
        return self._send(msg_id, name, phone_no, date)
        
class mock_msg_client(object):
    def __init__(self, log_path):
        self.log_path = log_path
        
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
            
        self.file_handler = open(log_path,'a')
        
    def notify(self, task_id, name, phone_no, msg_id, date):
        self.file_handler.write('%s\t%s\t%s\t%s\n'%(task_id, name.encode('utf-8'),phone_no, msg_id))
        return True
    
    def list(self):
        with open(self.log_path,'r') as f:
            for line in f:
                print(line)
    
    def close(self):
        self.file_handler.close()


class task_manager(object):
    def __init__(self, tasks, birthday_tasks, roles, msg_client):
        self.tasks = tasks
        self.birthday_tasks = birthday_tasks
        self.roles = roles
        self.msg_client = msg_client

    def send_birthday(self, date, bd_type, test_phone_num=None):
        if bd_type not in ['b','pb']:
            raise Exception('生日任务只能是b(生日)或者pb(政治生日)')   
        birthday_members = self.roles.members.find_birthday_member(date, bd_type)

        msg_id, zw_msg_id = self.birthday_tasks.get_details(bd_type)
        send_list = []
        for member_id in birthday_members:
            member_name = self.roles.members.get_info(member_id)['name']
            send_list.append((member_id, msg_id, member_name))
            zw_member_ids = self.roles.members.find_zw(member_id)
            for zw_member_id in zw_member_ids:
                send_list.append((zw_member_id, zw_msg_id, member_name))

        for send_info in send_list:
            member_id = send_info[0]; msg_id = send_info[1]; member_name = send_info[2]
            member_info = self.roles.members.get_info(member_id)
            if test_phone_num is None:
                phone_num = member_info['phone']
            else:
                phone_num = test_phone_num 
            is_sent = self.msg_client.notify(bd_type, member_name, phone_num, msg_id, date)
            if not is_sent:
                print('member %s birthday msg sent failed.' %(member_info['name']) )
        
    def run(self, date):
        # 根据日期扫描任务列表，获得当天任务
        task_id_list = self.tasks.get_task_ids(date)
        # 根据任务列表获取对应的党委和支部
        for task_id in sorted(task_id_list):
            org_id, role_ids, msg_id = self.tasks.get_details(task_id)
            # 获取信息所需要的列表
            for role_id in role_ids:
                # 获取角色对应的成员信息
                member_info_list = self.roles.get_member_info(org_id, role_id)
                if len(member_info_list) == 0:
                    raise Exception('Task %s org %s role %s has no members' %(task_id, org_id, role_id))
                for member_info in member_info_list[::-1]:  # 倒着发，避免拿领导做测试
                    is_sent = self.msg_client.notify(task_id, member_info['name'], member_info['phone'], msg_id, date)
                    if not is_sent:
                        print('Task %s org %s role %s member %s msg sent failed.' %(task_id, org_id, role_id, member_info['name']) )
        
        # 生日
        self.send_birthday(date, 'b')
        self.send_birthday(date, 'pb')    
    
    
    def run_test(self, date, test_phone_num=None, max_sent = 1):
        # 根据日期扫描任务列表，获得当天任务
        task_id_list = self.tasks.get_task_ids(date)
        # 根据任务列表获取对应的党委和支部
        for task_id in sorted(task_id_list):
            org_id, role_ids, msg_id = self.tasks.get_details(task_id)
            print(task_id)
            time.sleep(1)
            msg_cnt = 0
            # 获取信息所需要的列表
            for role_id in role_ids:
                # 获取角色对应的成员信息
                member_info_list = self.roles.get_member_info(org_id, role_id)
                if len(member_info_list) == 0:
                    raise Exception('Task %s org %s role %s has no members' %(task_id, org_id, role_id))
                for member_info in member_info_list:
                    if msg_cnt>=max_sent:
                       break
                    if test_phone_num is None:
                        phone_num = member_info['phone']
                    else:
                        phone_num = test_phone_num
                    is_sent = self.msg_client.notify(task_id, member_info['name'], phone_num, msg_id, date)
                    if not is_sent:
                        print('Task %s org %s role %s member %s msg sent failed.' %(task_id, org_id, role_id, member_info['name']) )
                    msg_cnt += 1
        # 生日
        
        self.send_birthday(date, 'b', test_phone_num=test_phone_num)
        self.send_birthday(date, 'pb', test_phone_num=test_phone_num)
    