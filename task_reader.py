# -*- encoding:utf-8 -*-
'''
输入:
(1) task.csv
taskID(int),时间(character),内容,msgID

(2)roles.txt
角色ID，定义

(3)role_org_ref
角色ID,组织ID

输出:
(1) task.txt
任务ID,执行周期,执行时间

(2)task_details.txt
任务ID,组织ID,角色ID,消息模板ID
'''
import os, sys
from collections import defaultdict
proj_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(proj_dir)
from util import comma_delimit_reader, read_time_msg, get_role_org_ref, get_time_reference

class taskReader(object):
    def __init__(self, role_path, role_org_ref_path, task_path, birthday_task_path):
        self.role_org_ref = defaultdict(list)
        res = comma_delimit_reader(role_org_ref_path)
        for entry in res:
            self.role_org_ref[entry[1]].append(entry[0])
            
        self.role_dict = {}
        res = comma_delimit_reader(role_path)
        for entry in res:
            role_name = entry[1].decode('utf-8')
            self.role_dict[role_name] = entry[0]
        
        self.task_path = task_path
        self.birthday_task_path = birthday_task_path
    
    def read(self, run_date):
        res = comma_delimit_reader(self.task_path, is_skip=False)
        time_reference = get_time_reference(run_date)
        # 定时任务
        with open(proj_dir+'/data/output/tasks.txt', 'w') as f1, open(proj_dir+'/data/output/task_details.txt','w') as f2:
            f1.write('任务ID,执行周期,执行时间\n')
            f2.write('任务ID,组织ID,角色ID,消息模板ID\n')
            
            for entry in res:
                task_id = 't'+entry[0]    
                time_msg = entry[1].decode('utf-8')
                freq, day = read_time_msg(time_msg, time_reference)
                f1.write('%s,%s,%s\n'%(task_id, freq, day))
                
                role_name = entry[2].decode('utf-8')
                role_id, org_ids = get_role_org_ref(role_name, self.role_dict, self.role_org_ref)
                
                msgID =  entry[4]
                f2.write('%s,%s,%s,%s\n'%(task_id, ';'.join(org_ids),role_id,msgID))
        # 生日任务
        res = comma_delimit_reader(self.birthday_task_path, sep=',')
        with open(proj_dir+'/data/output/birthday_task_details.txt', 'w') as f3:
            f3.write('任务ID,党员消息ID，组委消息ID\n')
            for entry in res:
                task_name = entry[0].strip()
                if task_name == '政治生日':
                    taskID = 'pb'
                elif task_name == '生日':
                    taskID = 'b'
                else:
                    raise Exception('生日任务只能有“政治生日”或者“生日”')
                f3.write('%s,%s,%s\n'%(taskID, entry[1],entry[2]))  

                
                
                
            
            
                

        