#!/usr/bin/python
# -*- coding: utf-8

import re
import string
import pymysql
import os
import sys
import smtplib
from email.mime.text import MIMEText
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import LockError
from pprint import pprint 




##########Juniper API###################################
routers = ["192.168.96.4","192.168.96.3"]
m = 109093
run_speed = 1024

for i in routers:
    print i
    a_dev = Device(host=i, user="apipy", password='pswd')
    try:
        a_dev.open()
    except Exception as err:
        print ('Unable to connect to host: %s' %i)
        
    model = a_dev.facts
    print (model)
    conf = Config(a_dev)
    #set_cmdDwn = 'set firewall family inet filter FROM-INTERNET term %s-DW then policer "%s"k ' %(m,run_speed)
    #set_cmdUp = 'set firewall family inet filter TO-INTERNET term %s-UP then policer "%s"k ' %(m,run_speed/2)
    #try:
    #    conf.load(set_cmdDwn,format='set')
    #    conf.load(set_cmdUp,format='set')
    #except Exception as err:
    #    print ('Fail to set config')
    try:
        conf.commit()
    except Exception as err:
        print ('Fail to commit')


########################################################            



'''
conf = Config(a_dev)
set_cmd = 'set system login message "No Hello USERSDSDSDD!"'
try:
    conf.load(set_cmd, format='set')
except Exception as err:
    print ('Fail to set config')
    sys.exit(1)

try:
    conf.commit()
except Exception as err:
    print ('Fail to set config')
    sys.exit(1)

#interfaces status
inIf = a_dev.cli("show interfaces terse")
print (inIf)

'''

a_dev.close()
quit()
