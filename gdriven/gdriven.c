#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/epoll.h>
#include <signal.h>
#include <errno.h>
#include <time.h>
#include <libgen.h>
#include <fcntl.h>

#define PRINTERRR(ERROR) ({printf("ERROR[%s-%s-%d]:%s\n",__FILE__,__FUNCTION__,__LINE__,ERROR);})
#define CLOSE "close\n"

int32_t SocketNoblocking(uint64_t sock);
void del_fdlist_element(int32_t *array, int32_t);
void close_socket(int *fdlist, int socket_fd);

int main(int argc, char *argv[])
{
    if(argc != 3)
    {
        printf("usage: ./%s [ip] [port]\n", basename(argv[0]));
        exit(EXIT_FAILURE);
    }

    char *ip = argv[1];
    short port = atoi(argv[2]);
    if ((port <= 0) || (port >= 65535))
    {
        PRINTERRR("invalid port");
        exit(EXIT_FAILURE);
    }
    in_addr_t addr = inet_addr(ip);
    if (addr == INADDR_NONE)
    {
        PRINTERRR("invalid ip");
        exit(EXIT_FAILURE);
    }

    int32_t sock_fd;
    int32_t socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_fd < 0)
    {
        PRINTERRR("get socket error");
        exit(EXIT_FAILURE);
    }
    SocketNoblocking(socket_fd);

    struct sockaddr_in *server_addr = (struct sockaddr_in *)malloc(sizeof(struct sockaddr_in));
    memset(server_addr, 0, sizeof(struct sockaddr_in));
    server_addr->sin_family = AF_INET;
    server_addr->sin_addr.s_addr = addr;
    server_addr->sin_port = htons(port);
    
    if (bind(socket_fd, (const struct sockaddr *)server_addr, sizeof(*server_addr)))
    {
        printf("error: %s\n", strerror(errno));
        printf("error: %d\n", errno);
        PRINTERRR("bind error");
        exit(EXIT_FAILURE);
    }

    if (listen(socket_fd, 10) == -1)
    {
        PRINTERRR("listen error");
        exit(EXIT_FAILURE);
    }

    printf("listening on port %d\n", port);

    int32_t *fd_list = (int32_t *)malloc(sizeof(int32_t)*1024);
    memset(fd_list, 0, sizeof(*fd_list));
    int16_t flag = 0;

    char *buffer = (char *)malloc(sizeof(char)*4096);

    while (1)
    {
        struct sockaddr_in *cli_addr = (struct sockaddr_in *)malloc(sizeof(struct sockaddr_in));
        memset(cli_addr, 0 , sizeof(struct sockaddr_in));
        socklen_t len = sizeof(struct sockaddr_in);
        int32_t cli_fd = accept(socket_fd, (struct sockaddr *)cli_addr, &len);
        free(cli_addr);
        if (cli_fd != -1){
            printf("cli_fd %d connect \n", cli_fd);
            fd_list[flag] = cli_fd;
            flag = flag + 1;
        }
        for(int i = 0; i < flag; i++){
            int16_t cur_fd = fd_list[i];
            if (cur_fd <= 0){
                printf("unknown error");
                continue;
            }
            memset(buffer, 0 ,sizeof(*buffer));
            int nbytes = recv(cur_fd, buffer, 4096, 0);
            switch(nbytes)
            {
                case -1:
                    printf("error: %s\n", strerror(errno));
                    close_socket(fd_list, cur_fd);
                    flag = flag - 1;
                    break;
                case 0:
                    printf("disconnect with %d\n", cur_fd);
                    close_socket(fd_list, cur_fd);
                    flag = flag - 1;
                    break;
                default:
                    buffer[nbytes] = '\0';
                    printf("recv from %d\n[msg_bytelen]: %d\n[msg_content]: %s", cur_fd, nbytes, buffer);
                    char *p = (char *)&CLOSE;
                    if ( strcmp((const char *)p, (const char *)buffer) == 0 )
                    {
                        printf("disconnect with %d\n", cur_fd);
                        close_socket(fd_list, cur_fd);
                        flag = flag - 1;
                    }
                    break;
            }
        }
    }

}

int32_t SocketNoblocking(uint64_t sock) {
    int32_t old_option = fcntl(sock, F_GETFL);
    if (old_option < 0)
    {
        PRINTERRR("fcntl error");
        exit(EXIT_FAILURE);
    }
    int32_t new_option = old_option | O_NONBLOCK;
    if (fcntl(sock, F_SETFL, new_option) < 0)
    {
        PRINTERRR("fcntl error");
        exit(EXIT_FAILURE);
    }
    return old_option;
}

void del_fdlist_element(int32_t *array, int32_t n)
{
    int32_t len = sizeof(*array) / sizeof(int32_t);
    int16_t flag = 0;
    for (int i = 0; i < len; i++){
        if (flag == 1){
            array[i - 1] = array[i];
            array[i] = 0;
        }
        if ( array[i] == n ){
            flag = 1;
        }
    }
}

void close_socket(int *fdlist, int socket_fd)
{
    close(socket_fd);
    del_fdlist_element(fdlist, socket_fd);
}