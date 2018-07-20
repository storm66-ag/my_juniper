#!/usr/bin/python
# -*- coding: utf-8

import string
import MySQLdb
import os
import smtplib   
import xlrd, xlwt 
from email.mime.text import MIMEText
from prettytable import PrettyTable 

##### Генерация Даты###################################
month1 = os.popen("date --date '-1 month' +%B").read()
lenMonth = len(month1)
month2 = month1[:lenMonth -1]
print month1
print month2
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

#Очищаем список модемов
modems = [ ]

#####Парметры Mysql Генерация списка модемов###########

db1=MySQLdb.connect(host="localhost", user="root", passwd="iDirect", db="billing")
#Создали курсор c1 для считывания модемов
c1=db1.cursor() 
sql = "SELECT  modem_sn FROM limit_client ; " 
c1.execute(sql)  
#Результат запроса в переменную в виде кортежа
data = c1.fetchall() #Считывание кортежа
for i in data:
#	print i[0] 
	modems.append(int(i[0])) # добавление модема в список modem
db1.close()
#print modems

######################################################

########Заготовка таблицы############################# 
x = PrettyTable(['Модем S/N', 'Передано MБ', 'Получено MБ', 'Всего МБ', 'Лимит МБ', 'Перерасход', 'Сумма за перерасход' ])


#################Xls start############################
startString = 2
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


wb = xlwt.Workbook()
ws = wb.add_sheet('Report')
ws.write(0, 1, '%s' %date, _style)
ws.write(1, 1, u"Клиент", _style1)
ws.write(1, 2, u"Модем", _style1)
ws.write(1, 3, u"Тариф",_style1)
ws.write(1, 4, u"Передано МБ", _style1)
ws.write(1, 5, u"Принято МБ", _style1)
ws.write(1, 6, u"Всего", _style1)     
ws.write(1, 7, u"Перерасход", _style1)

col = [ 1,2,3,4,5,6,7]
for c in col:
    ws.col(c).width = 5000


######################################################

########### Циклы обработки данных для каждого модема из списка modems#####################################################

db2=MySQLdb.connect(host="localhost", user="root", passwd="iDirect", db="netflow") # Подключаемся к DB внутри цикла
c2=db2.cursor()
db3=MySQLdb.connect(host="localhost", user="root", passwd="iDirect", db="billing", charset="utf8", init_command="SET NAMES UTF8")
c3=db3.cursor() 

for m in modems:
#	print m
	sql = "SELECT  SUM( UPSTREAM_B ),SUM( DOWNSTREAM_B ) FROM traffic WHERE ID ='%s' AND DATE BETWEEN DATE_SUB(NOW(), INTERVAL 30 DAY)  AND NOW(); " %(m) 
	sqlLim = "SELECT tarif FROM limit_client WHERE modem_sn='%s'; " %(m)
	sqlTariff = "SELECT tarif FROM clients WHERE modem_sn='%s'; " %(m)
	sqlName = "SELECT name FROM clients WHERE modem_sn='%s'; " %(m)
	request2 = [sql]
	request3 = [sqlLim]
	request4 = [sqlTariff]
	request5 = [sqlName]
	for i in request2:    #Обработка запроса 
#	#	print i
		c2.execute(i)
		data = c2.fetchone()
		TxMB = int(data[0] /1024 /1024)
		RxMB = int(data[1] /1024 /1024)
		Summ = TxMB + RxMB		
	#	print 'Передача:%s MB' %(TxMB)		
	#	print 'Прием:%s MB' %(RxMB)
	for t in request4:    #обработка запроса
                c3.execute(t)
                data = c3.fetchall()
                tariff = data[0]    	

	for n in request5:    #обработка запроса
                c3.execute(n)
                data = c3.fetchall()
                name = data[0]
		#print name
	for l in  request3:   # Обработка запроса
		c3.execute(l)
	        data = c3.fetchall()
		limMB = data[0]
		if limMB > Summ:
			Over = 0
		else:
			Over = Summ - limMB

		#print 'Лимит трафика:%s MB' % limMB	
	       	x.add_row([m, TxMB, RxMB, Summ, limMB[0], Over, 0 ])		
		
		#############XLS##############
		startString +=1
		ws.write(startString,1, name, _style2)
		ws.write(startString,2, m, _style2)
		ws.write(startString,3, tariff, _style2)
		ws.write(startString,4, TxMB, _style2)
		ws.write(startString,5, RxMB, _style2)
		ws.write(startString,6, Summ, _style2)  
		ws.write(startString,7, Over, _style2)			
# закрываем соединение с БД
db2.close()
db3.close()

#######################################################################################

##########Файл отчета##################################################################

wb.save('/usr/traffic-counter/tarifs/limit/month_report/python/%s.xls' %date) ###xls end#########

f = open("/usr/traffic-counter/tarifs/limit/month_report/python/%s.txt" % date, 'a')
f.writelines( "--%s--\n" % date )
f.writelines( "%s"  %x )
f.close()
print(open("%s.txt" % date ).read())
f.close()
print "Hello"

############Отправка email#############################################################

os.system(' echo "Данные по трафику" | mutt  -s  "Услуги передачи данных за %s"  alexbb@motivtelecom.ru -a /usr/traffic-counter/tarifs/limit/month_report/python/%s.xls' % (month,date) )

print "Hello1"

#######################################################################################

#os.system('/usr/traffic-counter/tarifs/limit/month_report/python/send.sh')  # Отправка на email






