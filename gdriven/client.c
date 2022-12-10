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

int main(int argc, char *argv[])
{
    if (argc != 3){
        printf("usage: ./%s [ip] [port]\n", basename(argv[0]));
        exit(EXIT_FAILURE);
    }

    char *ip = argv[1];
    short port = atoi(argv[2]);
    if (port <= 0 || port >= 65536)
    {
        PRINTERRR("invalid port\n");
        exit(EXIT_FAILURE);
    }
    int addr = inet_addr(ip);
    if (addr == INADDR_NONE)
    {
        PRINTERRR("invalid ip");
        exit(EXIT_FAILURE);
    }

    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0)
    {
        PRINTERRR("get socket error");
        exit(EXIT_FAILURE);
    }

    struct sockaddr_in *cliaddr = (struct sockaddr_in *)malloc(sizeof(struct sockaddr_in));
    memset(cliaddr, 0, sizeof(*cliaddr));
    cliaddr->sin_family = AF_INET;
    cliaddr->sin_addr.s_addr = addr;
    cliaddr->sin_port = htons(port);

    if (connect(sockfd, (const struct sockaddr *)cliaddr, sizeof(*cliaddr)) == -1)
    {
        PRINTERRR("connect failed");
        exit(EXIT_FAILURE);
    }

    printf("connect with server on port %d\n", port);
    char *buffer = (char *)malloc(sizeof(char)*4096);
    while(1)
    {
        memset(buffer, 0, sizeof(char)*4096);
        scanf("%s", buffer);
        write(sockfd, (const void *)buffer, strlen((const char *)buffer));
    }
}