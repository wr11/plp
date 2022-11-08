fun_help() {
cat <<EOF
Usage:
    $0 init                       # 初始化服务器配置
    $0 start                      # 启动所有服务进程
    $0 shutdown                   # 关闭所有服务进程
    $0 status                     # 查看所有服务状态
    $0 log                        # 查看所有服务日志
    $0 kill                       # 强制杀掉所有进程
EOF
}

case $# in
    1)
        case $1 in
            init) fun_init ; exit $? ;;
            start) fun_start ; exit $? ;;
            status) fun_status ; exit $? ;;
            log) fun_log ; exit $? ;;
            kill) fun_kill ; exit $? ;;
            shutdown) fun_shutdown ; exit $? ;;

            *) fun_help; exit 1 ;;
        esac
    ;;
    2)
        case $1 in
            zdump) fun_zdump $2 ; exit $? ;;

            *) fun_help; exit 1 ;;
        esac
    ;;
    4)
        case $1 in
            db) fun_db $2 $3 $4 ; exit $? ;;

            *) fun_help; exit 1 ;;
        esac
    ;;
    *)
        case $1 in
            *)  fun_help ; exit 1 ;;
        esac
    ;;
esac