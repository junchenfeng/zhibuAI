# -*- encoding:utf-8 -*- 
import unittest

from util import *


class TestFindFirstWorkDayAfter(unittest.TestCase):
    def test_func(self):
        res = find_first_workday_after(2017,10,1)
        self.assertEqual(res,'2017-10-09')
        
class TestGetSeasonMonth(unittest.TestCase):
    def test_func(self):
        self.assertEqual(1,get_season_month(1))
        self.assertEqual(1,get_season_month(2))
        self.assertEqual(1,get_season_month(3))
        self.assertEqual(4,get_season_month(4))
        self.assertEqual(4,get_season_month(5))
        self.assertEqual(4,get_season_month(6))
        self.assertEqual(7,get_season_month(7))
        self.assertEqual(7,get_season_month(8))
        self.assertEqual(7,get_season_month(9))
        self.assertEqual(10,get_season_month(10))
        self.assertEqual(10,get_season_month(11))
        self.assertEqual(10,get_season_month(12))

class TestGetTimeReference(unittest.TestCase):
    def test_func(self):
        res = get_time_reference("2017-10-01")
        self.assertEqual(res[u"每月月初"], "2017-10-09")
        self.assertEqual(res[u"每季季初"], "2017-10-09")
        self.assertEqual(res[u"每月月中"], "2017-10-16")
        
if __name__=="__main__":
    unittest.main()