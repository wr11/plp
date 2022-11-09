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
	echo "init finish"
}

fun_start_all() {
	echo "start begin"
}

fun_start_single() {
	serverNum=$1
	index=$2
	echo "${serverNum} ${index} start begin"
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

	*) fun_help ; exit 1 ;;
esac