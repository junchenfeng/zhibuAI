# -*- encoding:utf-8 -*-
from task_manager import members, roles, task_execute_check, tasks, birtdayTasks, orgs, task_manager, msg_client, mock_msg_client
from task_reader import taskReader
import os
proj_dir = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    import sys
    date = sys.argv[1]
    mode = sys.argv[2]
    
    # 读入数据
    reader_instance = taskReader(proj_dir+'/data/input/roles.csv', proj_dir+'/data/input/role_org_ref.csv', proj_dir+'/data/input/task.csv', proj_dir+'/data/input/birthday_task.csv')
    reader_instance.read(date)

    # 生成控制器
    task_instance = tasks(proj_dir+'/data/output/tasks.txt', proj_dir+'/data/output/task_details.txt')
    birthday_task_instance = birtdayTasks(proj_dir+'/data/output/birthday_task_details.txt')
    member_instance = members(proj_dir+"/data/input/members.csv",proj_dir+"/data/output/member_zw_ref.txt")
    role_instance = roles(member_instance, proj_dir+"/data/output/member_role_ref.txt")
    
    if mode == 'test':
        msg_client = mock_msg_client(proj_dir+"/log/test_log.txt")
    elif mode in ('staging','production'):
        msg_client = msg_client()
    else:
        raise Exception('启动模式为test, staging, production。现在是%s\n'%mode)
        
    instance = task_manager(task_instance, birthday_task_instance, role_instance, msg_client)    
    
    if mode == 'test':
        instance.run_test(date, max_sent=100)
        msg_client.list()
        msg_client.close()
    elif mode == 'staging':
        instance.run_test(date, test_phone_num='13051644352')
    elif mode == 'production':
        instance.run(date)
