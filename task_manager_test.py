# -*- encoding:utf-8 -*- 

import unittest
from task_manager import members, roles, task_execute_check, tasks, orgs, task_manager, msg_client
proj_dir = "C:\\Users\\junchen\\Documents\\GitHub\\pydjmsg"

class TestMembers(unittest.TestCase):
    def test_func(self):
        testInstance = members(proj_dir+"/test_data/members.csv")
        res = testInstance.get_info("m1")
        self.assertEqual(res["name"],u"张三")

class TestOrgs(unittest.TestCase):
    def test_func(self):
        testInstance = orgs(proj_dir+'/test_data/orgs.csv')
        res = sorted(testInstance.get_children("o1"))
        self.assertTrue(res,["o2","o3","o4"])
             
class TestRoles(unittest.TestCase):
    def test_func(self):
        test_member_instance = members(proj_dir+"/test_data/members.csv")
        test_role_instance = roles(test_member_instance, proj_dir+"/test_data/roles.csv", proj_dir+"/test_data/member_role_ref.txt")
        self.assertEqual(len(test_role_instance.get_member_info("o3","r4")),5)

class TestTaskExecuteCheck(unittest.TestCase):
    def test_s(self):
        self.assertEqual(task_execute_check("2017-09-20",'s','2017-09-20'), True)
        self.assertEqual(task_execute_check("2017-09-20",'s','2017-09-21'), False)
        self.assertEqual(task_execute_check("2017-09-20",'s','2017-09-20;2017-09-21'), True)
    
    def test_w(self):
        self.assertEqual(task_execute_check("2017-09-20",'w','3'), True)
        self.assertEqual(task_execute_check("2017-09-20",'w','4'), False)
        self.assertEqual(task_execute_check("2017-09-20",'w','3;4'), True)
    
    def test_m(self):
        self.assertEqual(task_execute_check("2017-09-20",'m','20'), True)
        self.assertEqual(task_execute_check("2017-09-20",'m','21'), False)
        self.assertEqual(task_execute_check("2017-09-20",'m','20;21'), True)   
        
    def test_y(self):
        self.assertEqual(task_execute_check("2017-09-20",'y','09-20'), True)
        self.assertEqual(task_execute_check("2017-09-20",'y','09-21'), False)
        self.assertEqual(task_execute_check("2017-09-20",'y','09-20;09-21'), True)   
 
class TestTask(unittest.TestCase):
    def test_get_task_ids(self):
        testInstance = tasks(proj_dir+'/test_data/tasks.txt', proj_dir+'/test_data/task_details.txt')
        res = sorted(testInstance.get_task_ids("2017-09-20"))
        self.assertTrue(res,["t1","t2","t3","t4"])
    
    def test_get_details(self):
        testInstance = tasks(proj_dir+'/test_data/tasks.txt', proj_dir+'/test_data/task_details.txt')
        org_id, role_ids, msg_id = testInstance.get_details("t4")
        self.assertEqual(org_id,'o3')
        self.assertEqual(sorted(role_ids),['r3','r4'])
        self.assertEqual(msg_id,'msg4')
   

class TestTaskMamager(unittest.TestCase):
    def test_t4(self):
        test_task_instance = tasks(proj_dir+'/test_data/tasks.txt', proj_dir+'/test_data/task_details.txt')
        test_member_instance = members(proj_dir+"/test_data/members.csv")
        test_role_instance = roles(test_member_instance, proj_dir+"/test_data/roles.csv", proj_dir+"/test_data/member_role_ref.txt")
        test_msg_client = msg_client()
        
        test_instance = task_manager(test_task_instance, test_role_instance, test_msg_client)
        
        test_instance.run('2017-09-20')
   
if __name__=="__main__":
    unittest.main()