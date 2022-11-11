#!/bin/bash

SERVER_NUM=1000

cmd_install="apt-get install"
python_version="python3.11"
python3_pip="python3-pip"

gatelog="gate.log"
gpslog="gps.log"
dbslog="dbs.log"

fun_help() {
cat <<EOF
Usage:
$0 <COMMAND> [OPTION]

COMMANDS:
	init					# 初始化服务器配置
	start					# 启动服务进程
	status					# 查看服务进程状态
	log					# 查看服务日志
	kill					# 强制杀掉服务进程
	resetdb					# 重置数据库

OPTIONS:
	start:
	-A						#全部服务器
	-H <servernum> <index>				#单个服务器

	status:
	-A						#全部服务器
	-H <servernum> <index>				#单个服务器

	log:
	-[TYPE] <filename>				#查看某类型日志文件
	TYPE: -D -E -N -W -S -> debug error notify warning stack

	kill:
	-A						#全部服务器
	-H <servernum> <index>				#单个服务器
EOF
}

fun_init() {
	echo "********** installing ${python_version} and pip **********"
	echo " "
	sudo ${cmd_install} -y ${python_version} &&
	sudo ${cmd_install} -y ${python3_pip} &&
	pip3 install -U pip &&

	echo " "
	echo "********** installing packages **********"
	echo " "
	${python_version} -m pip install colorama &&
	${python_version} -m pip install msgpack &&
	${python_version} -m pip install twisted --use-pep517 &&
	${python_version} -m pip install pymysql &&

	echo " "
	echo "********** installing mysql **********"
	echo " "
	sudo ${cmd_install} -y  mysql-server &&
	sudo mysql -uroot -e "alter user 'root'@'localhost' identified with mysql_native_password by 'mytool2021';" &&

	echo " "
	echo "********** initializing db and tables **********"
	echo " "
	cd server/datahub/mysql/allocate &&
	sudo mysql -uroot -pmytool2021 < allocate.sql &&

	echo " "
	echo "********** init finish!!! **********"
}

fun_start_all() {
	echo "reading server config ..."
	res1=`${python_version} -B server/conf.py 1`
	array_server=(${res1//,/ })
	echo "server start list: "
	for index in ${array_server[@]} 
	do
		echo "servernum: ${SERVER_NUM} index: ${index}"
	done

	for index in ${array_server[@]} 
	do
		server_type=`${python_version} -B server/conf.py 2 ${SERVER_NUM} ${index}`
		if [ -z "${server_type}" ]
		then
			echo "error: cannot match type with server ${SERVER_NUM}, ${index}"
			exit
		else
			log_name="${server_type}.log"
			if [ -f ${log_name} ]
			then
				rm ${log_name}
			fi
			echo "starting ${SERVER_NUM} ${index} > log in ${log_name}"
			nohup ${python_version} -B server/main.py ${SERVER_NUM} ${index} > ${log_name} 2>&1 &
		fi
	done

	echo "server start finish !!!"
}

fun_start_single() {
	serverNum=$1
	index=$2
	echo "${serverNum} ${index} start begin"
	echo "waiting for support"
}

fun_status_all(){
	echo "status all"
	echo "waiting for support"
}

fun_status_single(){
	serverNum=$1
	index=$2
	echo "${serverNum} ${index} status single"
	echo "waiting for support"
}

fun_log(){
	type=$1
	filename=$2
	echo "${type} ${filename} log"
	echo "waiting for support"
}

fun_kill_all(){
	echo "killing all server process ..."
	ps -ef | grep "python3.11" | grep -v grep | awk '{print $2}' | xargs echo
	ps -ef | grep "python3.11" | grep -v grep | awk '{print $2}' | xargs kill -9
	echo "all server processes have been killed, quit..."
}

fun_kill_single(){
	serverNum=$1
	index=$2
	echo "${serverNum} ${index} kill single"
	echo "waiting for support"
}

fun_resetdb(){
	cd server/datahub/mysql/allocate &&
	sudo mysql -uroot -pmytool2021 < allocate.sql

	echo "resetdb finish!!!"
}

case $1 in
	init) fun_init ; exit $? ;;

	start)
		case $# in
			2)
				case $2 in
					-A) fun_start_all ; exit $? ;;
					*) fun_help ; exit $? ;;
				esac
			;;
			3) fun_start_single $2 $3 ; exit $? ;;
			*) fun_help ; exit 1 ;;
		esac
	;;

	status)
		case $# in
			2)
				case $2 in
					-A) fun_status_all ; exit $? ;;
					*) fun_help ; exit $? ;;
				esac
			;;
			3) fun_status_single $2 $3 ; exit $? ;;
			*) fun_help ; exit 1 ;;
		esac
	;;

	log)
		case $# in
			3) fun_log $2 $3 ; exit $? ;;
			*) fun_help ; exit 1 ;;
		esac
	;;

	kill)
		case $# in
			2)
				case $2 in
					-A) fun_kill_all ; exit $? ;;
					*) fun_help ; exit $? ;;
				esac
			;;
			3) fun_kill_single $2 $3 ; exit $? ;;
			*) fun_help ; exit 1 ;;
		esac
	;;

	resetdb) fun_resetdb ; exit $? ;;

	*) fun_help ; exit 1 ;;
esac