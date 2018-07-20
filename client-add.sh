 
#!/bin/bash

## Structure ###    start_service:last_modify:modem_sn:start_fap:acl_num:acl_ip:acl_ipmask #####
## $1 - modem_sn
## $2 - name
## $3 - tarif (fap256 or limit1024)
## $4 - ip address of network
## $5 - id
## $6 - oid1

if  [ "$1" ]
then

	echo "$1" 
	echo "$2"
	echo "$3"
	echo "$4"
	echo "$5"
	echo "$6"
mysql -u root -piDirect billing <<EOF
INSERT INTO clients (start_service,last_modify,modem_sn,name,tarif,ip_address,id,oid1) VALUES ( now(),now(),'$1','$2','$3','$4','$5','$6');
EOF
else 

echo '!!!PLEASE input the  modem_sn:name:tarif(fap256 or limit1024):ip_address:id:snmp_oid(from juniper)!!!'

fi

#######For FAP tarifs###############################################################

	if [[ $3 == fap* ]]
	then
	case  $3 in
	fap256)
		fap=256
	;;
	fap512)
                fap=512
        ;;
	fap1024)
                fap=1024
        ;;
	fap2048)
                fap=2048
        ;;
	fap4096)
                fap=4096
        ;;
	fapS1024)
		fap=S1024
	;;
	*)
		echo "Введите правильные значения"
		break 
	;;
	esac

#if [ "$3=fap256 || $3=fap512 || $3=fap1024 || $3=fap2048 || $3=fap4096 " ] 
#then

MYSQLcon="mysql -u root -piDirect billing"  ##connection to db
FAP_START=`echo "SELECT speed1 FROM fap_tarif WHERE fap_name='$fap' " | $MYSQLcon | tail -n1` ##get value form db


mysql -u root -piDirect billing <<EOF
INSERT INTO  fap_live (last_modify,modem_sn,run_fap) VALUES (now(),'$1','$FAP_START');
EOF

mysql -u root -piDirect billing <<EOF
INSERT INTO  fap_client (start_service,last_modify,modem_sn,name,start_fap,ip_address,id,oid1) VALUES (now(),now(),'$1','$2','$fap','$4','$5','$6');
EOF
	fi
#############For Lim Tarifs#######################################################

	if [[ $3 == lim* ]]
	then
	case  $3 in
        lim1024)
                lim=1024
        ;;
        lim2000)
                lim=2000
        ;;
        lim3000)
                lim=3000
        ;;
        lim4000)
                lim=4000
        ;;
        lim5000)
                lim=5000
        ;;
	lim3072)
		lim=3072
	;;
	lim70000)
		lim=70000
	;;
	*)
        echo "Введите правильные значения"
	break
        ;;

	esac

#elif  [ "$3=lim[1000-10000] " ]
#then


echo Tarif Limit
mysql -u root -piDirect billing <<EOF
INSERT INTO  limit_client (date_start,modem_sn,name,tarif,ip_address,id,oid1) VALUES (now(),'$1','$2','$lim','$4','$5','$6');
EOF
mysql -u root -piDirect billing <<EOF
INSERT INTO  limit_live (name,modem_sn,downloaded_mB)  VALUES ('$2','$1',0);
EOF


	fi


exit 0
