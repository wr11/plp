fun_help() {
cat <<EOF
Usage:
$0 <COMMAND> [OPTION]

COMMANDS:
	init					# 初始化服务器配置
	start					# 启动服务进程
	shutdown				# 关闭服务进程
	status					# 查看服务进程状态
	log					# 查看服务日志
	kill					# 强制杀掉服务进程

OPTIONS:
	start:
	-A						#全部服务器
	-H <servernum> <index>				#单个服务器

	shutdown:
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
	echo "********** installing python3.11 and pip **********"
	echo " "
	sudo apt-get install python3.11 &&
	sudo apt-get install python3-pip &&
	sudo pip3 install -U pip &&

	echo " "
	echo "********** installing packages **********"
	echo " "
	python3.11 -m pip install colorama &&
	python3.11 -m pip install msgpack &&
	python3.11 -m pip install twisted --use-pep517 &&
	python3.11 -m pip install pymysql &&

	echo " "
	echo "********** installing mysql **********"
	echo " "
	sudo apt install -y  mysql-server
	sudo mysql -uroot -e "alter user 'root'@'localhost' identified with mysql_native_password by 'mytool2021';"

	echo " "
	echo "********** initializing db and tables **********"
	echo " "
	cd server/datahub/mysql/allocate
	sudo mysql -uroot -pmytool2021 < allocate.sql

	echo " "
	echo "********** init finish!!! **********"
}

fun_start_all() {
	echo "start begin"
}

fun_start_single() {
	serverNum=$1
	index=$2
	echo "${serverNum} ${index} start begin"
}

fun_shutdown_all(){
	echo "shutdown all finish"
}

fun_shutdown_single(){
	serverNum=$1
	index=$2
	echo "${serverNum} ${index} shutdown finish"
}

fun_status_all(){
	echo "status all"
}

fun_status_single(){
	serverNum=$1
	index=$2
	echo "${serverNum} ${index} status single"
}

fun_log(){
	type=$1
	filename=$2
	echo "${type} ${filename} log"
}

fun_kill_all(){
	echo "kill all"
}

fun_kill_single(){
	serverNum=$1
	index=$2
	echo "${serverNum} ${index} kill single"
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

	shutdown)
		case $# in
			2)
				case $2 in
					-A) fun_shutdown_all ; exit $? ;;
					*) fun_help ; exit $? ;;
				esac
			;;
			3) fun_shutdown_single $2 $3 ; exit $? ;;
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

	*) fun_help ; exit 1 ;;
esac