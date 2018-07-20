#!/usr/bin/python
# -*- coding: utf-8

import re
import string
#import MySQLdb
#import PyMySQL
import pymysql
import os
import sys
import smtplib   
import xlsxwriter
#import xlrd, xlwt 
from email.mime.text import MIMEText
#from unidecode import unidecode
from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos.exception import LockError
from pprint import pprint

receivers= [ 'alexbb@motivtelecom.ru' , '79043828661@sms.ycc.ru' ]
routers = ['192.168.96.3' ,  '192.168.96.4'] 

##########Обрабатываем ID###############################################

try:
    db1 = pymysql.connect(host="localhost", user="root", passwd="iDirect", db="billing", charset="utf8", init_command="SET NAMES UTF8")
except (pymysql.OperationalError, pymysql.ProgrammingError):
    print ("Проблемы соединения с базой данных Billing!")
    for r in receivers:
       os.system(' echo "Проблемы соединения с базой данных Billing! Script clear_fap.py" | mutt  -s  "Проблемы соединения с базой данных Billing!" %s ' %(r))

c1= db1.cursor()  #Создаем единый курсор для DB Billing
modems=[] 

#################Формируем список модемов для ID#########################
    
sqlModem = "SELECT modems.modem_sn FROM fap_live, modems WHERE tariff RLIKE 'fap'  and status=0 ;" 
c1.execute(sqlModem)
data1 = c1.fetchall()
for d in data1:
#   print d[0]
   modems.append(int(d[0]))    # Добавляем модем в список  modems
    
################Обработка модемов########################################    

for m in modems:
#    print modems
    print (m)
        
    ############Считываем название тарифа для текущего модема###################################
    sqlTarif = "SELECT modems.tariff as tariff, fap_tarif.speed1 as start_speed FROM billing.modems LEFT JOIN billing.fap_tarif ON fap_tarif.fap_name=modems.tariff WHERE modem_sn ='%d'; " %m
    try:
        c1.execute(sqlTarif)
    except (pymysql.OperationalError, pymysql.ProgrammingError):
        print ("Ошибка чтения данных из табл fap_tarif !!!")
    tariff_sql = c1.fetchone()
    tariff = str(tariff_sql[0])
    print ("Тариф модема:%s" %tariff)
    speed_start = int(tariff_sql[1])
    print (speed_start)

    sqlWrSpeed = "UPDATE fap_live SET run_fap='%s' WHERE modem_sn='%d'; " %(speed_start,m)
    sqlWrDownload = "UPDATE fap_live SET downloaded_mB=0 WHERE modem_sn='%d'; " %(m)
    sqlWrDate = "UPDATE fap_live SET last_modify=NOW()"
    try:
        c1.execute(sqlWrSpeed)  # Устанавливаем начальную скорость
        c1.execute(sqlWrDownload) # Обнуляем трафик
	c1.execute(sqlWrDate) # Текущая дата
    except (pymysql.OperationalError, pymysql.ProgrammingError):
        print ('Проблемы с записью в таблицу Fap_Live!')
        for r in receivers:
            os.system(' echo "Проблемы с записью в таблицу Fap_Live! Script clear_fap.py" | mutt  -s  "Проблемы с записью в таблицу Fap_Live! " %s ' %(r))


################### Считываем  тарифную сетку для тарифа текущего модема##################################

    sqlData = "SELECT speed1,speed2,speed3,traffic1,traffic2 FROM fap_tarif WHERE fap_name ='%s'; " %tariff
    try:
        c1.execute(sqlData)
        data1 = c1.fetchall()
        speed1 = data1[0][0]
        speed2 = (data1[0][1])
        speed3 = (data1[0][2])
        trafLim1 = (data1[0][3])
        trafLim2 = (data1[0][4])
        print ("-------Тарифная сетка--------")
        print (speed1)
        print (speed2)
        print (speed3)
        print ('Лимит1: %s МБ' %trafLim1)
        print ('Лимит2: %s МБ' %trafLim2)
        print ("-----------------------------")

    except (pymysql.OperationalError,pymysql.ProgrammingError):
        print ("Ошибка чтения данных из табл fap_tarif !!!")    
    sqlWrLim1 = "UPDATE fap_live SET traffic_lim='%s' WHERE modem_sn='%d'; " %(trafLim1,m)
    try:
        c1.execute(sqlWrLim1)  # Меняем значение лимита на исходное
    except (pymysql.OperationalError, pymysql.ProgrammingError):
        print ('Проблемы с записью в таблицу Fap_Live!') 
        for r in receivers:
            os.system(' echo "Проблемы cзаписью! Script clear_fap.py" | mutt  -s  "Проблемы с записью в таблицу Fap_Live! " %s ' %(r)) 

    db1.commit() 
      


######################Juniper API###################################

    for i in routers:
        print i
        a_dev = Device(host=i, user="apipy", password="@pi2o16$")
        try:
            a_dev.open()
        except Exception as err:
            print ('Unable to connect to host: %s' %i)
            for r in receivers:
                os.system(' echo "Unable to connect to host: %s " | mutt  -s  "Проблемы с подключением к рутеру!" %s'  %(i,r))
        hostname = a_dev.facts['hostname']
        print (hostname)
        conf = Config(a_dev)
        set_cmdDW = 'set firewall family inet filter FROM-INTERNET term %s-DW then policer "%s"k ' %(m,speed_start)
        set_cmdUP = 'set firewall family inet filter TO-INTERNET term %s-UP then policer "%s"k ' %(m,speed_start/2)
        try:
            conf.load(set_cmdDW,format='set')
            conf.load(set_cmdUP,format='set') 
        except Exception as err:
            print ('Fail to set config!')
        try:
            conf.commit()
        except Exception as err:
            print ('Fail to commit!') 


            ########################################################           
        print ("------------------------------------")  
        print ('Данные для модема  %d  обновлены' %m)
        print ('Тариф %s' %tariff)
        print ("------------------------------------")        


    
    #######################################

db1.commit()
db1.close()		


print ('The End....')





