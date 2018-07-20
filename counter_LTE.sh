#!/bin/bash

TIME_RANGE=" `date --date "60 minute ago" +%H:%M`-`date +%H:%M`"
MYSQLdb="netflow"
MYSQLtb="MOB_5MIN"
FLOW_OUTkb="0"
FLOW_INkb="0"
TOTALkb="0"
name="lte_s1"
###FILTERdir="/etc/flow-tools/scripts/flows/filters/mobifon.acl"

EMAIL1="alexxgruzdov@gmail.com"
EMAIL2="79043828661@sms.ycc.ru"

R1="192.168.96.3"
R2="192.168.96.4"

OID_n="iso.3.6.1.4.1.2636.3.5.2.1.7"
OID_c="iso.3.6.1.4.1.2636.3.5.2.1.5."

RJ1oid="$R1 iso.3.6.1.4.1.2636.3.5.2.1.7"
RJ1cnt="$R1 iso.3.6.1.4.1.2636.3.5.2.1.5."

RJ2oid="$R2 iso.3.6.1.4.1.2636.3.5.2.1.7"
RJ2cnt="$R2 iso.3.6.1.4.1.2636.3.5.2.1.5."


MYSQLcon1="mysql -u root -piDirect billing"
MYSQLcon2="mysql -u root -piDirect netflow"


##########Read from Mysql DB serial number#############
mysql -D billing -u root -piDirect -e "SELECT modem_sn FROM modems_lte where error=0" -N > modem_lte_sn.txt
sleep 1

cat modem_lte_sn.txt

###########Start script###############################
index=0

############Read from file modem_sn.txt ################
while read line; do
    array[$index]="$line"
    index=$(($index+1))
echo $line

SN=("$line")       
for i in $SN ; do
echo $i


###########Juniper1############################


echo "FROM JUNIPER1"

OIDin_R1="` snmpwalk -c oss-router -v 1 $RJ1oid | grep X7_EC_"$i"_UDP_IN | awk '{print $1}' |  sed -e 's/^.\{29\}//' `"
OIDout_R1="`snmpwalk -c oss-router -v 1 $RJ1oid | grep X7_EC_"$i"_UDP_OUT | awk '{print $1}' |  sed -e 's/^.\{29\}//' `" 

if [ "$OIDin_R1" ] && [ "$OIDout_R1" ]
	then 
		echo OIDin_R1:"$OIDin_R1"
		echo OIDout_R1:"$OIDout_R1"
	BYTES_IN_R1="`snmpget -Os -c oss-router  -v 1 $RJ1cnt"$OIDin_R1" | awk '{print $4}' `"
	echo BYTES_IN_R1: $BYTES_IN_R1
	BYTES_OUT_R1="`snmpget -Os -c oss-router  -v 1 $RJ1cnt"$OIDout_R1" | awk '{print $4}' `"
	echo BYTES_OUT_R1: $BYTES_OUT_R1
else 
	echo "Error get data for $i from $R1"	
	echo "Error get data for $i from $R1" | mail -s "Mobifon-2000_Vsat__Service" "$EMAIL1"  
	echo "Error get data for $i from $R1" | mail -s "OSS_Service" "$EMAIL2"
fi


############Juniper2###################################
 
echo "FROM JUNIPER2"

OIDin_R2="0"
OIDout_R2="0"

###OIDin_R2="` snmpwalk -c oss-router -v 1 $RJ2oid | grep X7_EC_"$i"_UDP_IN | awk '{print $1}' |  sed -e 's/^.\{29\}//' `"
###OIDout_R2="`snmpwalk -c oss-router -v 1 $RJ2oid | grep X7_EC_"$i"_UDP_OUT | awk '{print $1}' |  sed -e 's/^.\{29\}//' `"

if [ "$OIDin_R2" ] && [ "$OIDout_R2" ]
        then 
		echo OIDin_R2:"$OIDin_R2"
        	echo OIDout_R2:"$OIDout_R2"
        BYTES_IN_R2="0"
	#BYTES_IN_R2="`snmpget -Os -c oss-router  -v 1 $RJ2cnt"$OIDin_R2" | awk '{print $4}' `"
        echo BYTES_IN_R2: $BYTES_IN_R2
	BYTES_OUT_R2="0"
        #BYTES_OUT_R2="`snmpget -Os -c oss-router  -v 1 $RJ2cnt"$OIDout_R2" | awk '{print $4}' `"
        echo BYTES_OUT_R2: $BYTES_OUT_R2
else 
       OIDin_R2="0"
       OIDout_R2="0"


fi
##############START Count Data#########################################

echo "----TOTAL------"

if [ $BYTES_IN_R1 ] && [ $BYTES_OUT_R1 ] && [ $BYTES_IN_R2 ] && [ $BYTES_OUT_R2 ]
	then 
		BYTES_IN_t=$(($BYTES_IN_R1 + $BYTES_IN_R2))
		echo BYTES_IN_t:$BYTES_IN_t
		BYTES_OUT_t=$(($BYTES_OUT_R1 + $BYTES_OUT_R2))
		echo BYTES_OUT_t:$BYTES_OUT_t
#BYTES_OUT=0
		KBYTES_IN_t=$(($BYTES_IN_t / 1024))
		KBYTES_OUT_t=$(($BYTES_OUT_t / 1024))
		TOTALkb=$(($KBYTES_IN_t + $KBYTES_OUT_t))
		echo KBYTES_IN:$KBYTES_IN_t
		echo KBYTES_OUT:$KBYTES_OUT_t
		echo TOTALkb:$TOTALkb

####################Read old counters DATA from MYSQL##################################################
echo "Reading from DB..........."

BYTES_IN_t_old=`echo "SELECT DOWNSTREAM_B FROM counters  WHERE ID='$i' " | $MYSQLcon2 | tail -n1`
echo OLD-IN:$BYTES_IN_t_old

BYTES_OUT_t_old=`echo "SELECT UPSTREAM_B FROM counters  WHERE ID='$i' " | $MYSQLcon2 | tail -n1`
echo OLD-OUT:$BYTES_OUT_t_old

    if [ "$BYTES_IN_t_old" -gt "$BYTES_IN_t" ] && [ "$BYTES_OUT_t_old" -gt  "$BYTES_OUT_t"  ]
         then 
               TRAFFICb_in=0
               TRAFFICb_out=0
         echo "OLD TRAFFIC > NEW TRAFFIC"
    else
        TRAFFICb_in=$(($BYTES_IN_t - $BYTES_IN_t_old))
        TRAFFICb_out=$(($BYTES_OUT_t - $BYTES_OUT_t_old))
    fi

echo TRAFFIC-IN:$TRAFFICb_in
echo TRAFFIC-OUT:$TRAFFICb_out 

#####################Write DATA to MYSQL##################################################################

echo "Writing to DB..........."

mysql -u flowuser -pnetflow $MYSQLdb <<EOF
INSERT INTO traffic (DATE,ID,UPSTREAM_B,DOWNSTREAM_B) VALUES (now(),"$i",$TRAFFICb_out,$TRAFFICb_in)
EOF

sleep 1

mysql -u flowuser -pnetflow $MYSQLdb <<EOF
UPDATE counters SET DATE=now(),UPSTREAM_B=$BYTES_OUT_t,DOWNSTREAM_B=$BYTES_IN_t WHERE ID="$i"
EOF

###########################################################################

else echo "NO DATA  COUNT!!!"	
#mysql -u root -piDirect billing <<EOF
#UPDATE client_modems SET error="1" WHERE modem_sn="$i"
#EOF


fi

done

done < /usr/traffic-counter/counters/modem_lte_sn.txt

exit 0
