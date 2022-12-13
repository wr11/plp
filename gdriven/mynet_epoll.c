#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/epoll.h>
#include <errno.h>
#include <time.h>
#include <libgen.h>
#include <fcntl.h>

#define PRINTERRR(ERROR) ({printf("ERROR[%s-%s-%d]:%s\n",__FILE__,__FUNCTION__,__LINE__,ERROR);})
#define CLOSE "close\n"

int set_non_blocking(int socket_fd);

int main(int argc, char *argv[])
{
    if (argc != 3){
        printf("Usage: ip, port\n");
        exit(EXIT_FAILURE);
    }

    char *ip = argv[1];
    int port = atoi(argv[2]);
    in_addr_t ip_net = inet_addr((const char *)ip);
    if (ip_net == INADDR_NONE)
    {
        PRINTERRR("invalid ip");
        exit(EXIT_FAILURE);
    }
    if (port <= 0 || port >= 65535)
    {
        PRINTERRR("invalid port");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in *addr = (struct sockaddr_in *)malloc(sizeof(struct sockaddr_in));
    memset(addr, 0, sizeof(*addr));
    addr->sin_family = AF_INET;
    addr->sin_port = htons(port);
    addr->sin_addr.s_addr = ip_net;

    int socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    set_non_blocking(socket_fd);
    if (socket_fd == -1) {
        perror("socket");
        exit(EXIT_FAILURE);
    }
    if (bind(socket_fd, (const struct sockaddr*)addr, sizeof(*addr)) == -1)
    {
        perror("bind");
        exit(EXIT_FAILURE);
    }
    if (listen(socket_fd, 10) == -1)
    {
        perror("listen");
        exit(EXIT_FAILURE);
    }
    printf("server start listening on port: %d\n", port);

    int epoll_fd = epoll_create(1);
    struct epoll_event *ev = (struct epoll_event *)malloc(sizeof(struct epoll_event));
    memset(ev, 0, sizeof(*ev));
    (ev->data).fd = socket_fd;
    ev->events = EPOLLIN|EPOLLET;
    if (epoll_ctl(epoll_fd, EPOLL_CTL_ADD, socket_fd, ev) == -1)
    {
        perror("epoll_ctl");
        exit(EXIT_FAILURE);
    }

    struct epoll_event *ev2 = (struct epoll_event *)malloc(sizeof(struct epoll_event)*1024);
    memset(ev2, 0, sizeof(*ev2));
    struct sockaddr_in *client_addr = (struct sockaddr_in *)malloc(sizeof(struct sockaddr_in));
    memset(client_addr, 0, sizeof(*client_addr));
    char *buffer = (char *)malloc(sizeof(char)*4096);
    int num_of_fds = 0;
    int bytes = 0;
    socklen_t sock_len = sizeof(struct sockaddr_in);
    while(1)
    {
        num_of_fds = epoll_wait(epoll_fd, ev2, 1024, 1000);
        if (num_of_fds == -1)
        {
            perror("epoll_wait");
            exit(EXIT_FAILURE);
        }
        for (int i = 0; i < num_of_fds; i++)
        {
            if (ev2[i].data.fd == socket_fd)
            {
                int client_fd = accept(socket_fd, (struct sockaddr *)client_addr, &sock_len);
                if (client_fd == -1)
                {
                    printf("client accept failed");
                    continue;
                }
                set_non_blocking(client_fd);
                char *client_ip = inet_ntoa(client_addr->sin_addr);
                int client_port = client_addr->sin_port;
                printf("client connect from %s:%d\n", client_ip, client_port);
                ev->events = EPOLLOUT|EPOLLIN|EPOLLET;
                (ev->data).fd = client_fd;
                epoll_ctl(epoll_fd, EPOLL_CTL_ADD, client_fd, ev);
            }
            else if (ev2[i].events & EPOLLIN)
            {
                printf("epoll in\n");
                int fd = ev2[i].data.fd;
                bytes = recv(fd, buffer, 4096, 0);
                switch(bytes)
                {
                    case -1:
                        break;
                    case 0:
                        printf("disconnect with %d\n", fd);
                        close(fd);
                        ev->events = EPOLLIN|EPOLLET;
                        (ev->data).fd = fd;
                        epoll_ctl(fd, EPOLL_CTL_DEL, fd, ev);
                        break;
                    default:
                        buffer[bytes] = '\0';
                        printf("recv from %d\n[msg_bytelen]: %d\n[msg_content]: %s", fd, bytes, buffer);
                        char *p = (char *)&CLOSE;
                        if ( strcmp((const char *)p, (const char *)buffer) == 0 )
                        {
                            printf("disconnect with %d\n", fd);
                            close(fd);
                            ev->events = EPOLLIN|EPOLLET;
                            (ev->data).fd = fd;
                            epoll_ctl(fd, EPOLL_CTL_DEL, fd, ev);
                        }
                        else{
                            char *result = "server respond\n";
                            int rc = send(fd, (const void *)result, 16, 0);
                        }
                        break;
                }
            }
            else if (ev2[i].events & EPOLLOUT){
                printf("epoll out\n");
            }
        }
    }
}

int set_non_blocking(int socket_fd)
{
    int flags = fcntl(socket_fd, F_GETFL);
    if (flags < 0)
    {
        PRINTERRR("fcntl error");
        exit(EXIT_FAILURE);
    }
    int new_flags = flags | O_NONBLOCK;
    if (fcntl(socket_fd, F_SETFL, new_flags) < 0)
    {
        PRINTERRR("fcntl error");
        exit(EXIT_FAILURE);
    }
    return new_flags;
}