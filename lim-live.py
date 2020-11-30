#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
## SQL query data from netflow DB and write to billing DB (limit_live).
#

import pymysql

MODEMS = []

try:
    db_billing = pymysql.connect(host="172.26.0.53", user="root", passwd="Password", db="billing")
    db_netflow = pymysql.connect(host="172.26.0.53", user="root", passwd="Password", db="netflow")
    with db_billing.cursor() as cursor:
        sqlModem = "SELECT modem_sn FROM modems WHERE tariff RLIKE 'lim'"
        cursor.execute(sqlModem)
        modem_sn = cursor.fetchall()
        for sn in modem_sn:
            MODEMS.append(int(sn[0]))
    with db_netflow.cursor() as cursor:
        for modem in MODEMS:
            print(modem)
            sqlTraf = "SELECT SUM(UPSTREAM_B)/1024/1024 as ups, SUM(DOWNSTREAM_B)/1024/1024 as ds FROM netflow.traffic WHERE ID ='%s' AND MONTH(date) = MONTH(NOW()) AND YEAR(date) = YEAR(NOW())" % modem
            cursor.execute(sqlTraf)
            downloaded = cursor.fetchall()
            for download in downloaded:
                upstream_mb = int(download[0])
                downstream_mb = int(download[1])
                summ_mb = upstream_mb + downstream_mb
                print('Передано:', upstream_mb, 'МБ')
                print('Принято:', downstream_mb, 'МБ')
                print('Всего:', summ_mb, 'МБ')
            sqlLim = "SELECT tariff FROM billing.modems WHERE modem_sn='%s'" % modem
            cursor.execute(sqlLim)
            modem_tariff = cursor.fetchone()
            traffic_limit = int(modem_tariff[0].split('.')[1])
            if summ_mb > traffic_limit:
                over_mb = summ_mb - traffic_limit
                print('Перерасход:', over_mb, 'МБ')
            else:
                over_mb = 0
            try:
                sqlWrOver = "UPDATE limit_live SET overload_mB=%d WHERE modem_sn='%s'" % (over_mb, modem)
                sqlWrDwn = "UPDATE limit_live SET downloaded_mB=%d WHERE modem_sn='%s'" % (summ_mb, modem)
                sqlWrDate = "UPDATE limit_live SET date=now() WHERE modem_sn='%s'" % (modem)
                db_billing.cursor().execute(sqlWrOver)
                db_billing.cursor().execute(sqlWrDwn)
                db_billing.cursor().execute(sqlWrDate)
                db_billing.commit()
            except pymysql.OperationalError as err:
                print(err)
            except pymysql.InternalError as err:
                print(err)
    db_billing.close()
    db_netflow.close()
except pymysql.OperationalError as err:
    print(err)
except pymysql.InternalError as err:
    print(err)
