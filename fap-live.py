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



routers = ["192.168.96.3","192.168.96.4"] 

##########Обрабатываем ID###############################################

try:
    db1 = pymysql.connect(host="localhost", user="root", passwd="iDirect", db="billing", charset="utf8", init_command="SET NAMES UTF8")
except (pymysql.OperationalError, pymysql.ProgrammingError):
    print ("Проблемы соединения с базой данных Billing!")
c1 = db1.cursor()  #Создаем единый курсор для DB Billing
modems=[] 

#################Формируем список модемов для ID#########################
    
sqlModem = "SELECT modems.modem_sn FROM fap_live, modems WHERE tariff RLIKE 'fap'  and status=0 ;" 
c1.execute(sqlModem)
data1 = c1.fetchall()
for d in data1:
#   print d[0]
   modems.append(int(d[0]))    # Добавляем модем в список  modems
    
#################Соединяемся с БД трафика################################

try:
    db2=pymysql.connect(host="localhost", user="root", passwd="iDirect", db="netflow") # DB для считывания трафика
except (pymysql.OperationalError, pymysql.ProgrammingError):
    print ("Проблемы соединения с базой данных Netflow!")
c2=db2.cursor()

################Обработка модемов########################################    

for m in modems:
#    print modems
    print (m)
    #############Считаем трафик для модема с 6:00  текущего дня
    sqlTraf = "SELECT  SUM( UPSTREAM_B ),SUM( DOWNSTREAM_B ) FROM traffic WHERE ID ='%d' AND  date(DATE)=date(now()) AND TIME( DATE ) BETWEEN TIME('06:00') AND TIME( NOW( ) ) ;" %(m)
    try:
        c2.execute(sqlTraf)
    except (pymysql.OperationalError, pymysql.ProgrammingError):
        print ("Ошибка чтения данных из табл Traffic!")
    data2 = c2.fetchall()
    for t in data2:    #Обработка запроса по трафику
        #prsqlWrSpeed = "UPDATE fap_live SET run_fap='%d' WHERE modem_sn='%d'; " %(run_speed,m)int data[0]
        #####Формируем отчет
        Up = int(t[0]/1024 /1024) 
        Dw = int(t[1]/1024 /1024)
        Summ = Up + Dw
    print ('Передано: %d МБ' %Up) 
    print ('Принято: %d МБ' %Dw) 	
    print ('Всего: %d МБ' %Summ) 
    
    #################Записываем значения скачанного трафика##################################### 

    sqlWrSumm = "UPDATE fap_live SET downloaded_mB=%d WHERE modem_sn=%d; " %(Summ,m)
    try:
        print "Записываю скачанный трафик!!!!!!!"
        c1.execute(sqlWrSumm) 
    except (pymysql.OperationalError, pymysql.ProgrammingError):
        print ('Проблемы с записью в таблицу Fap_Live!')
    
        
    ############Считываем название тарифа для текущего модема###################################
    sqlTarif = "SELECT tariff FROM modems WHERE modem_sn ='%d'; " %m
    try:
        c1.execute(sqlTarif)
    except (pymysql.OperationalError, pymysql.ProgrammingError):
        print ("Ошибка чтения данных из табл fap_tarif !!!")
    tariff = c1.fetchone()
    tariff = str(tariff[0])
    print ("Тариф модема:%s" %tariff)
   # speed1 = tariff.split('.')     
   # print (speed1[1])

    ############ Считываем  тарифную сетку для тарифа

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

    ########## Определяем текущую скорость#########################################

    sqlrunSpeed = "SELECT run_fap FROM fap_live WHERE modem_sn ='%d'; " %m
    try:
        c1.execute(sqlrunSpeed)
        data1 = c1.fetchone()
        run_speed = data1[0]
        print ('Текущая скорость: %s кБит/сек' %run_speed)

    except (pymysql.OperationalError, pymysql.ProgrammingError):
        print ("Ошибка чтения данных из табл fap_tarif !!!")

    #####Сравнение с лимитами и смена скорости#####################################

    if (run_speed == speed1):
        if Summ > trafLim1:  # Условие 1 Lim1
      # if Summ > (trafLim1+trafLim2):  # Условие 2 Lim1+Lim2
            run_speed = speed2          # Устанавливаем текущую скорость
            sqlWrSpeed = "UPDATE fap_live SET run_fap='%d' WHERE modem_sn='%d'; " %(run_speed,m)
        #sqlWrStatus = "UPDATE fap_live SET status='1' WHERE modem_sn='%d'; " %(m)
            sqlWrLim = "UPDATE fap_live SET traffic_lim='%d' WHERE modem_sn='%d'; " %(trafLim1 + trafLim2,m)
            try:
                c1.execute(sqlWrSpeed)  # Меняем скорость
                c1.execute(sqlWrLim) # Меняем лимит
            except (pymysql.OperationalError, pymysql.ProgrammingError):
                print ('Проблемы с записью в таблицу Fap_Live!')
            db1.commit() 
      
            ##########Juniper API###################################

            for i in routers:
                print i
                a_dev = Device(host=i, user="apipy", password="@pi2o16$")
                try:
                    a_dev.open()
                except Exception as err:
                    print ('Unable to connect to host: %s' %i)
                model = a_dev.facts['model']
                print (model)
                conf = Config(a_dev)
                set_cmdDw = 'set firewall family inet filter FROM-INTERNET term %s-DW then policer "%s"k ' %(m,run_speed)
                set_cmdUp = 'set firewall family inet filter TO-INTERNET term %s-UP then policer "%s"k ' %(m,run_speed/2)
                try:
                    conf.load(set_cmdDw,format='set')
                    conf.load(set_cmdUp,format='set') 
                except Exception as err:
                    print ('Fail to set config')
                try:
                    conf.commit()
                except Exception as err:
                    print ('Fail to commit') 


            ########################################################           

            print ('Новая текущая скорость: %s ' %run_speed)
            print ('speed changing......')
                

            ###########Фиксируем время смены скорости#########################

            sqlWrTime = "UPDATE fap_live SET last_modify=NOW() WHERE modem_sn='%d'; " %(m)
            try:
                c1.execute(sqlWrTime)  # Меняем скорость
            except (pymysql.OperationalError, pymysql.ProgrammingError):
                print ('Проблемы с записью в таблицу Fap_Live!')               

            db1.commit() 
            ##################################################################
             

   
    elif (run_speed == speed2):
        if Summ > (trafLim1+trafLim2):      
            run_speed = speed3
            sqlWrSpeed = "UPDATE fap_live SET run_fap='%d' WHERE modem_sn='%d'; " %(run_speed,m)
            try:
                c1.execute(sqlWrSpeed)  # Меняем скорость
            except (pymysql.OperationalError, pymysql.ProgrammingError):
                print ('Проблемы с записью в таблицу Fap_Live!')            
            print (run_speed)
            ##########Juniper API###################################

            for i in routers:
                print i
                a_dev = Device(host=i, user="apipy", password="@pi2o16$")
                try:
                    a_dev.open()
                except Exception as err:
                    print ('Unable to connect to host: %s' %i)
                model = a_dev.facts['model']
                print (model)
                conf = Config(a_dev)
                set_cmdDw = 'set firewall family inet filter FROM-INTERNET term %s-DW then policer "%s"k ' %(m,run_speed)
                set_cmdUp = 'set firewall family inet filter TO-INTERNET term %s-UP then policer "%s"k ' %(m,run_speed) 
                try:
                    conf.load(set_cmdDw,format='set')
                    conf.load(set_cmdUp,format='set') 
                except Exception as err:
                    print ('Fail to set config')
                try:
                    conf.commit()
                except Exception as err:
                    print ('Fail to commit')


            ########################################################
         
            ###########Фиксируем время смены скорости#########################

            sqlWrTime = "UPDATE fap_live SET last_modify=NOW() WHERE modem_sn='%d'; " %(m)
            try:
                c1.execute(sqlWrTime)  # Меняем скорость
            except (pymysql.OperationalError, pymysql.ProgrammingError):
                print ('Проблемы с записью в таблицу Fap_Live!')

            db1.commit() 
            ##################################################################    





    else:
        print ('Ни чего не меняем!!!')    
	

db2.close()
    
    #######################################

db1.commit()
db1.close()		


print ('The End....')





