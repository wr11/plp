#!/bin/bash

SERVER_NUM=1000

cmd_install="apt-get install"
python_version="python3.11"
python3_pip="python3-pip"
rootlog="log"
syslog="${rootlog}/syslog"
serverlog="${rootlog}/serverlog"

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
	help					# 查看帮助信息

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

	echo "********** initializing log file path **********"
	echo " "
	mkdir -p ${syslog}
	echo ${syslog}
	mkdir -p ${serverlog}
	echo ${serverlog}

	echo " "
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
		res=`ps -ef | grep -v grep | grep python3.11 | grep ${SERVER_NUM} | grep ${index} -w `
		if [ -z "${res}" ]
		then
			server_type=`${python_version} -B server/conf.py 2 ${SERVER_NUM} ${index}`
			if [ -z "${server_type}" ]
			then
				echo "error: cannot match type with server ${SERVER_NUM}, ${index}"
				exit
			else
				log_name="${syslog}/${server_type}.log"
				if [ -f ${log_name} ]
				then
					rm ${log_name}
					touch ${log_name}
				fi
				echo "starting ${SERVER_NUM} ${index} > log in ${log_name}"
				nohup ${python_version} -B server/main.py ${SERVER_NUM} ${index} > ${log_name} 2>&1 &
			fi
		else
			echo "error: server ${SERVER_NUM} ${index} is still running"
			exit
		fi
	done

	echo "server start finish !!!"
}

fun_start_single() {
	serverNum=$1
	index=$2
	res=`ps -ef | grep -v grep | grep python3.11 | grep ${serverNum} | grep ${index} -w `
	if [ -z "${res}" ]
	then
		server_type=`${python_version} -B server/conf.py 2 ${SERVER_NUM} ${index}`
		if [ -z "${server_type}" ]
		then
			echo "error: cannot match type with server ${SERVER_NUM}, ${index}"
			exit
		else
			log_name="${syslog}/${server_type}.log"
			if [ -f ${log_name} ]
			then
				rm ${log_name}
				touch ${log_name}
			fi
			echo "starting ${SERVER_NUM} ${index} > log in ${log_name}"
			nohup ${python_version} -B server/main.py ${SERVER_NUM} ${index} > ${log_name} 2>&1 &
		fi
		echo "server ${SERVER_NUM} ${index} start finish!!!"
	else
		echo "error: server ${SERVER_NUM} ${index} is still running"
		exit
	fi
}

fun_status_all(){
	echo "searching for server process ..."
	res1=`${python_version} -B server/conf.py 1`
	array_server=(${res1//,/ })
	for index in ${array_server[@]} 
	do
		echo "server process: ${SERVER_NUM} ${index}"
		res=`ps -ef | grep -v grep | grep python3.11 | grep ${SERVER_NUM} | grep ${index} -w `
		result=`${python_version} -B server/conf.py 3 ${res}`
		echo ${result}
		echo ""
	done
}

fun_status_single(){
	serverNum=$1
	index=$2
	server_type=`${python_version} -B server/conf.py 2 ${serverNum} ${index}`
	if [ -z "${server_type}" ]
	then
		echo "error: cannot match type with server ${serverNum}, ${index}"
		exit
	else
		echo "searching for server process ${serverNum} ${index} ..."
		res=`ps -ef | grep -v grep | grep python3.11 | grep ${serverNum} | grep ${index} -w `
		result=`${python_version} -B server/conf.py 3 ${res}`
		echo ${result}
	fi
}

fun_log(){
	# -D -E -N -W -S
	type=$1
	filename=$2
	path=""
	case ${type} in
		-D) path="${serverlog}/debug" ; break ;;
		-E) path="${serverlog}/error" ; break ;;
		-N) path="${serverlog}/notify" ; break ;;
		-W) path="${serverlog}/stack" ; break ;;
		-S) path="${serverlog}/warning" ; break ;;
		*) echo "error: invalid log type" ; exit 1 ;;
	esac
	cat ${path}/${filename}
}

fun_kill_all(){
	echo "killing all server process ..."
	ps -ef | grep "python3.11" | grep -v grep | awk '{print $2}' | xargs echo
	ps -ef | grep "python3.11" | grep -v grep | awk '{print $2}' | xargs kill -9
	echo "all server processes have been killed, quit"
}

fun_kill_single(){
	serverNum=$1
	index=$2
	server_type=`${python_version} -B server/conf.py 2 ${serverNum} ${index}`
	if [ -z "${server_type}" ]
	then
		echo "error: cannot match type with server ${serverNum}, ${index}"
		exit
	else
		res=`ps -ef | grep -v grep | grep python3.11 | grep ${serverNum} | grep ${index} -w `
		if [ -z "${res}" ]
		then
			echo "proccess ${SERVER_NUM} ${index} is not running"
			exit
		else
			echo "killing ${serverNum} ${index} process"
			ps -ef | grep -v grep | grep python3.11 | grep ${serverNum} | grep ${index} -w | awk '{print $2}' |xargs echo
			ps -ef | grep -v grep | grep python3.11 | grep ${serverNum} | grep ${index} -w | awk '{print $2}' |xargs kill -9
			echo "${serverNum} ${index} process has been killed"
		fi
	fi
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

	help) fun_help ; exit 1 ;;

	*) fun_help ; exit 1 ;;
esac