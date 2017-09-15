# -*- encoding:utf-8 -*-
'''
Submail message/xsend API demo
SUBMAIL SDK Version 1.0.1 --python
copyright 2011 - 2014 SUBMAIL
'''
from message_xsend import MESSAGEXsend
from app_configs import MESSAGE_CONFIGS
from address_book_message import ADDRESSBOOKMessage

'''
init MESSAGEXsend class
'''
submail = MESSAGEXsend(MESSAGE_CONFIGS)

'''
Optional para
recipient cell phone number
@Multi-para
'''
submail.add_to('18811006983')
'''
Optional para
set addressbook sign : Optional
add addressbook contacts to Multi-Recipients
@Multi-para
'''
#addressbook = ADDRESSBOOKMessage(MESSAGE_CONFIGS)
#addressbook.set_address('13051644352')
#addressbook.set_address('18811006983')
#import ipdb;ipdb.set_trace()
#submail.add_address_book(addressbook)

'''
Required para
set message project sign
'''
submail.set_project('jDJeK2')

'''
Optional para
submail email text content filter
@Multi-para
'''
#submail.add_var('receiver','陈剑锋')
#submail.add_var('deadline','8月18日')
#submail.add_var('task','两会一课')
print submail.xsend()
submail.to = []
submail.add_to('13051644352')
print submail.to
print submail.xsend()
