#!/usr/bin/python
# -*- coding: utf-8

import re
import string
import MySQLdb
import os
import sys
import smtplib   
import xlrd, xlwt 
from email.mime.text import MIMEText
from prettytable import PrettyTable 
from unidecode import unidecode
import datetime


##### Генерация Даты###################################
my_date = datetime.date.today()
my_year = my_date.year
#print my_year


month1 = os.popen("date --date '-1 month' +%B").read()  # Считвем дату из консоли
lenMonth = len(month1)
month2 = month1[:lenMonth -1]
#print month1
#print month2
if month2 == "January":
    month = "Январь"
elif month2 == "February":
    month = "Февраль"
elif month2 == "Match":
    month = "Март"
elif month2 == "January":
    month = "Апрель"
elif month2 == "May":
    month = "Май"
elif month2 == "June":
    month = "Июнь"
elif month2 == "July":
    month = "Июль"
elif month2 == "August":
    month = "Август"
elif month2 == "September":
    month = "Сентябрь"
elif month2 == "October":
    month = "Октябрь"
elif month2 == "November":
    month = "Ноябрь"
elif month2 == "December":
    month = "Декабрь" 
else:
   print "No Month"

date1 = os.popen("date --date '-1 month' +%B-%Y").read()
date2 = str(date1) # Дата в строку
lenDate = len(date2) # Число символов в строке
#print lenDate
date = date1[:lenDate -1] # Форматирование даты
#print date

#######################################################

################XLS###############################################
######Создание стилей#############################################
startRow = 1

font0 = xlwt.Font()
font0.name = 'Arial'
font1 = xlwt.Font()
font1.bold = True
font1.name = 'Arial'
pattern = xlwt.Pattern() # Create the Pattern
pattern.pattern = xlwt.Pattern.SOLID_PATTERN # May be: NO_PATTERN, SOLID_PATTERN, or 0x00 through 0x12
pattern.pattern_fore_colour = 26 # May be: 8 through 63. 0 = Black, 1 = White, 2 = Red, 3 = Green, 4 = Blue, 5 = Yellow, 6 = Magenta, 7 = Cyan, 16 = Maroon,$
borders = xlwt.Borders() # Create Borders
borders.left = xlwt.Borders.THIN # May be: NO_LINE, THIN, MEDIUM, DASHED, DOTTED, THICK, DOUBLE, HAIR, MEDIUM_DASHED, THIN_DASH_DOTTED, MEDIUM_DASH_DOTTED, $
borders.right = xlwt.Borders.THIN
borders.top = xlwt.Borders.THIN
borders.bottom = xlwt.Borders.THIN
alignment = xlwt.Alignment() # Create Alignment
alignment.horz = xlwt.Alignment.HORZ_CENTER # May be: HORZ_GENERAL, HORZ_LEFT, HORZ_CENTER, HORZ_RIGHT, HORZ_FILLED, HORZ_JUSTIFIED, HORZ_CENTER_ACROSS_SEL,$
alignment.vert = xlwt.Alignment.VERT_CENTER # May be: VERT_TOP, VERT_CENTER, VERT_BOTTOM, VERT_JUSTIFIED, VERT_DISTRIBUTED
_style = xlwt.XFStyle() # Create Style
_style.alignment = alignment
_style.font = font0
_style.borders = borders
_style1 = xlwt.XFStyle()
_style1.pattern = pattern
_style1.borders = borders
_style1.alignment = alignment
_style1.font = font1
_style2 = xlwt.XFStyle()
_style2.borders = borders
_style2.font = font0
_style2.alignment = alignment


wb = xlwt.Workbook()  #Создание рабочей книги            

###############################################################

##########Собираем ID###############
id = [ ]
try:
    dbId = MySQLdb.connect(host="localhost", user="root", passwd="iDirect", db="billing", charset="utf8", init_command="SET NAMES UTF8")
except (MySQLdb.OperationalError, MySQLdb.ProgrammingError), e:
    print "Проблемы соединения с базой данных Billing!"
    sys.exit()
cId = dbId.cursor()
sql = "SELECT id FROM clients; "
cId.execute(sql)
data = cId.fetchall()
for i in data:
    id.append(int(i[0])) 
dbId.close()
print id

#########################

##########Обрабатываем ID###########################

try:
    dbCon = MySQLdb.connect(host="localhost", user="root", passwd="iDirect", db="billing", charset="utf8", init_command="SET NAMES UTF8")
except (MySQLdb.OperationalError, MySQLdb.ProgrammingError), e:
    print "Проблемы соединения с базой данных Billing!"
c1 = dbCon.cursor()  #Создаем единый курсор для DB Billing
 
for i in id:          
    modems=[]    # Готовим список модемов для текущего ID
    sql = "SELECT contracts.uid FROM contracts WHERE id=%s;" %i
    #sql = "SELECT clients.name,contracts.num,orders.num,client_modems.modem_sn,orders.tarif,orders.cost FROM contracts,clients,orders,client_modems WHERE clients.id=%s and clients.id=contracts.id and contracts.uid=orders.uid and  clients.id = client_modems.id;" %i
    c1.execute(sql)
    data = c1.fetchall()
    
    ###############Имя компании###############################
    sqlCName = "SELECT name FROM clients WHERE id='%s'; " %(i)
    c1.execute(sqlCName)
    dataName = c1.fetchone()
    for e in dataName:
        name = e
        print "########START###############"
        print name
        cName = name  
    ##########################################################
    #########################Загатовка таблицы XLS##################################
    ws = wb.add_sheet(cName)  # Новый лист для клиента сName 
    startString = 2

    #############Собираем UID для данного ID##########
    
    uid = [ ] # Создали пустой список uid'ОВ
    print "Номер ID: %s" %i
    for d in data:
	uid.append(int(d[0]))   #Добавляем uid в список для текущего ID
    print "Список UID для ID %s: %s" %(i,uid)

    #############################################################################
    ws.write(1, 1, (month.decode('utf-8')), _style1)
	# #    ws.write(1, 1, '%s' %date, _style1)
    ws.write(1, 2, '%s' %my_year, _style1)
    ws.write(1, 3, '%s' %cName, _style1)
    col = [ 1,2,3,4,5,6]
	# ####Ширина колонок
    for row in col:
        ws.col(row).width = 5000
        ws.col(7).width = 7000 #### Отдельное значение для 7Й 
    #############Собираем Номера заказов для ID###########
    startString_M=4
    ws.write(startString_M, 1, u"Договор", _style1)
    ws.write(startString_M, 2, u"Дата", _style1)
    ws.write(startString_M, 3, u"Заказ",_style1)
    ws.write(startString_M, 4, u"Дата", _style1)
    ws.write(startString_M, 5, u"Абонентская РУБ", _style1)
    ws.write(startString_M, 6, u"За превыш. РУБ", _style1)
    ws.write(startString_M, 7, u"Итого РУБ", _style1)
    #Обработка UID для текщего ID#
    print "Обработка UID"
    for a in uid:
	    
        sqlCONTRACT = "SELECT contracts.num,contracts.date,orders.num,orders.date,orders.cost,orders.c_over FROM contracts,orders WHERE  contracts.uid=orders.uid and contracts.uid=%s;" %a
        c1.execute(sqlCONTRACT)
        data = c1.fetchall()
        for c in data:
            numCon = str(c[0])
            datCon = str(c[1])
            numOrder = str(c[2])
            datOrder = str(c[3])
            costOrder = float(c[4])
            costOver = float(c[5]) / 100
            print "Номер договора %s" %(str(c[0]))
            print "Дата соглашения: %s" %(str(c[1]))
            print "Номер заказа:%s" %(str(c[2]))
            print "Дата заказа:%s"  %(str(c[3]))
            print "Стоимость заказа: %g" %(c[4])
        #startString+= 1
        # ws.write(startString, 1, numCon, _style2)
        # ws.write(startString, 2, datCon, _style2)
        # ws.write(startString, 3, numOrder, _style2)
        # ws.write(startString, 4, datOrder, _style2)
        # ws.write(startString, 5, costOrder, _style2)
				# if Over > 0:
					# sumOver = Over * costOver  #### Стоимость сверх Лимита
					# sumAll = sumOver + costOrder   #### Общая сумма 
					# ws.write(startString, 6, float(sumOver), _style2) 
					# ws.write(startString, 7, float(sumAll), _style2)
				# else:
					# ws.write(startString, 6,"-" , _style2) 
					# ws.write(startString, 7, costOrder, _style2)
        
        sql = "SELECT orders.num,orders.date,cost FROM orders WHERE uid=%s;" %a
        sqlOverCost = "SELECT c_over FROM orders WHERE uid=%s;" %a 
        c1.execute(sql)
        data = c1.fetchall()
        print "Цикл!!!!!!!!!!!!"
    ######################################################
    
    #################Список модемов для ID#########################
        modems = []
        sqlModem = "SELECT modem_sn FROM client_modems WHERE uid=%s;" %a
        c1.execute(sqlModem)
        data2 = c1.fetchall()
        for d in data2:
		   #print d[0]
            modems.append(int(d[0]))    
        print "Список модемов:"
        print modems
        modem_id = len(modems)   
        
        if modem_id > 0: 
	   ################################################################
	   #################Считываем трафик для каждого модема из списка#####################################################
            try:
				db2=MySQLdb.connect(host="localhost", user="root", passwd="iDirect", db="netflow") # DB для считывания трафика
            except (MySQLdb.OperationalError, MySQLdb.ProgrammingError), e:
				print "Проблемы соединения с базой данных Netflow!"
            c2=db2.cursor() 
            startString+=startString_M+4
            
            ws.write(startString, 1, u"Модем", _style1)
            ws.write(startString, 2, u"Тариф",_style1)
            ws.write(startString, 3, u"Передано МБ", _style1)
            ws.write(startString, 4, u"Принято МБ", _style1)
            ws.write(startString, 5, u"Всего МБ", _style1)
            ws.write(startString, 6, u"Перерасход МБ", _style1)
            ws.write(startString, 7, u"За превышение РУБ/МБ", _style1)
            col = [ 1,2,3,4,5,6]
	####Ширина колонок
            for row in col:
				ws.col(row).width = 5000
				ws.col(7).width = 7000 #### Отдельное значение для 7Й        


	################Обработка статистики для модемов##############################################    

            for m in modems:
                print m
                sqlOverCost = "SELECT orders.c_over,client_modems.modem_sn FROM orders,client_modems WHERE orders.uid=client_modems.uid and client_modems.modem_sn=%s;" %m
                c1.execute(sqlOverCost)
                data = c1.fetchall()
                for y in data:
                    costOver = float(y[0]) / 100
                    print "Стоимость за превышение:"
                    print costOver   

                sql = "SELECT  SUM( UPSTREAM_B ),SUM( DOWNSTREAM_B ) FROM traffic WHERE ID ='%s' AND DATE BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY)  AND NOW(); " %(m)
                sqlLim = "SELECT tarif FROM limit_client WHERE modem_sn='%s'; " %(m)
                sqlTariff = "SELECT tariff FROM client_modems WHERE modem_sn='%s'; " %(m)
	#sqlName = "SELECT name FROM clients WHERE modem_sn='%s'; " %(m)
                request2 = [sql]
                request4 = [sqlTariff]

                for t in request4:    #запроса по трафику
					c1.execute(t)
					data = c1.fetchone()
	   #print data[0]
					tariff = data[0]
					print 'Тариф:'
					print tariff	
                if re.search(r'lim*|LIMIT*|LIM*',str(tariff)):
					print "Тариф с подсчетом!!!"
					for c in request2:    #запрос лимита
						c2.execute(c)
						data = c2.fetchone()
						TxMB = int(data[0] /1024 /1024)
						RxMB = int(data[1] /1024 /1024)
						Summ = TxMB + RxMB
						print 'Передача:%s MB' %(TxMB)
						print 'Прием:%s MB' %(RxMB)
						print 'Общий трафик:%s MB' %(Summ) 
						limMB1 = tariff.split('.')  ### Определяем лимит из названия тарифа
						limMB = int(limMB1[1])
						print 'Лимит трафика:%s MB' %limMB
						if limMB > Summ:
							Over = 0
						else:
							Over = Summ - limMB
							print 'Перерасход: %s MB' %(Over)
						startString +=1
						ws.write(startString,1, m, _style2)
						ws.write(startString,2, tariff, _style2)
						ws.write(startString,3, TxMB, _style2)
						ws.write(startString,4, RxMB, _style2)
						ws.write(startString,5, Summ, _style2)
						ws.write(startString,6, Over, _style2)
						ws.write(startString,7, costOver, _style2)
						startString+= 2
						
						
                else:
					print "Тариф без подсчета трафика!"
					for p in request2:
						Over = 0
						c2.execute(p)
						data = c2.fetchone()
						TxMB = int(data[0] /1024 /1024)
						RxMB = int(data[1] /1024 /1024)
						Summ = TxMB + RxMB
						startString +=1
						ws.write(startString,1, m, _style2)
						ws.write(startString,2, tariff, _style2)
						ws.write(startString,3, TxMB, _style2)
						ws.write(startString,4, RxMB, _style2)
						ws.write(startString,5, Summ, _style2)
						ws.write(startString,6, "-", _style2)
						ws.write(startString,7, "-", _style2)
						startString+= 2

	##########Собираем номера договоров,заказов и их стоимость###################
            sqlCONTRACT = "SELECT contracts.num,contracts.date,orders.num,orders.date,orders.cost,orders.c_over FROM contracts,orders WHERE  contracts.uid=orders.uid and contracts.uid=%s;" %a
            c1.execute(sqlCONTRACT)
            data = c1.fetchall()
            for c in data:
                numCon = str(c[0])
                datCon = str(c[1])
                numOrder = str(c[2])
                datOrder = str(c[3])
                costOrder = float(c[4])
                costOver = float(c[5]) / 100
                startString_M+= 1
	#####Заполнение ячеек данными из переменных
                ws.write(startString_M, 1, numCon, _style2)
                ws.write(startString_M, 2, datCon, _style2)
                ws.write(startString_M, 3, numOrder, _style2)
                ws.write(startString_M, 4, datOrder, _style2)
                ws.write(startString_M, 5, costOrder, _style2)
                if Over > 0:
                    sumOver = Over * costOver  #### Стоимость сверх Лимита
                    sumAll = sumOver + costOrder   #### Общая сумма 
                    ws.write(startString_M, 6, float(sumOver), _style2) 
                    ws.write(startString_M, 7, float(sumAll), _style2)
                else:
                    ws.write(startString_M, 6,"-" , _style2) 
                    ws.write(startString_M, 7, costOrder, _style2)  
        else: 
            #print "В договоре  %s нет Модемов!" %(numCon)
		    #print "Собираю номера заказов и стоимость!!!"
            sqlCONTRACT = "SELECT contracts.num,contracts.date,orders.num,orders.date,orders.cost FROM contracts,orders WHERE contracts.uid=%s and contracts.uid=orders.uid;" %a
            c1.execute(sqlCONTRACT)
            data = c1.fetchall()
            for c in data:
                numCon = str(c[0])
                datCon = str(c[1])
                numOrder = str(c[2])
                datOrder = str(c[3])
                costOrder = float(c[4])
                print "Номер договора %s" %(str(c[0]))
                print "Дата соглашения: %s" %(str(c[1]))
                print "Номер заказа:%s" %(str(c[2]))
                print "Дата заказа:%s"  %(str(c[3]))
                print "Стоимость заказа: %g" %(c[4])
                startString_M+=1
                ws.write(startString_M, 1, numCon, _style2)
                ws.write(startString_M, 2, datCon, _style2)
                ws.write(startString_M, 3, numOrder, _style2)
                ws.write(startString_M, 4, datOrder, _style2)
                ws.write(startString_M, 5, costOrder, _style2)
                ws.write(startString_M, 6,"-" , _style2) 
                ws.write(startString_M, 7, costOrder, _style2)
    
    # startString+= modem_id
    # ws.write(startString, 1, u"Договор", _style1)
    # ws.write(startString, 2, u"Дата", _style1)
    # ws.write(startString, 3, u"Заказ",_style1)
    # ws.write(startString, 4, u"Дата", _style1)
    # ws.write(startString, 5, u"Абонентская РУБ", _style1)
    # ws.write(startString, 6, u"За превыш. РУБ", _style1)
    # ws.write(startString, 7, u"Итого РУБ", _style1)
		############################################################################# 


db2.close()
    
    #######################################
		

###########XLS###################################################################################

#wb.save('/usr/traffic-counter/tarifs/limit/month_report/reports/TESTING_REPORT.xls')
print "Сохраняю в файл........"
wb.save('/usr/traffic-counter/tarifs/limit/month_report/reports/%s.xls' %date) 

dbCon.close()

#################################################################################################

############Отправка email#############################################################


receivers = ['alexxgruzdov@gmail.com']
for r in receivers:
    os.system(' echo "Письмо создано автоматически" | mutt  -s  "Cеть  Связи.Услуги за %s"  %s -a /usr/traffic-counter/tarifs/limit/month_report/reports/%s.xls' % (month,r,date) )
os.system(' echo "Отчет успешно создан!" | mutt  -s  "Услуги за %s" 79043828661@sms.ru ' %(month))

print "Hello1"
print month

#######################################################################################

#os.system('/usr/traffic-counter/tarifs/limit/month_report/python/send.sh')  # Отправка на email





