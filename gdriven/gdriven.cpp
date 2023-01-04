#include <iostream>
#include <string.h>
#include <string>
#include <memory>
#include <unistd.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <sys/epoll.h>
#include <errno.h>
#include <time.h>
#include <fcntl.h>
#include <thread>
#include <vector>
#include <malloc.h>
#include <unordered_map>

#define EPOLL_OS __linux__ || __unix__

#ifdef __win__
#include <ws2tcpip.h>
#endif

#if EPOLL_OS
#include <linux/version.h>
#include <arpa/inet.h>
#define VERSION_MIN = KERNEL_VERSION(4,5,0)
#endif

using namespace std;

// region conf
static const bool _DEBUG = true;
static const bool _NONBLOCK = true;
static const bool _REUSEPORT = true;
static const bool _ALLOW_THREAD_INCOMPLETE = true;
static const int _MAX_EPOLL_WAIT_EVENT_SIZE = 1024;
static const int _MAX_RECEIVE_ONCE_SIZE = 1024;
static const int _MAX_RECEIVE_BUFFER_SIZE = 4104;
static const int _MAX_SEND_BUFFER_SIZE = 4104;
static const int _IP_INFO_LEN = 17;
// end region conf

struct NetParam
{
    in_addr_t ip;
    unsigned short port;
    unsigned short thread_num;

    string raw_ip;
    string raw_port;
    string raw_thread_num;
};

#if EPOLL_OS
struct NetThread_Linux
{
    bool writable;
    int fd_socket;
    int fd_epoll;
};
#else
struct NetThread_Other {};
#endif

// region print
#define TIMESTRSIZE 80

char* GetTimeStr()
{
    time_t raw_time;
    struct tm *info;
    static char buffer[TIMESTRSIZE];
    time(&raw_time);
    info = localtime(&raw_time);
    strftime(buffer, TIMESTRSIZE, "%Y-%m-%d %H:%M:%S", info);
    return buffer;
}

namespace Print{
    void Warn(string file, string function, int line, string msg){
        char *time = GetTimeStr();
        cout << "[" << this_thread::get_id() << "]" << "[" << time << "]" \
            << "[" << file << ":" << line << " in " << function << "]" << "[WARN]" << msg << endl;
    }

    void Error(string file, string function, int line, string msg){
        char *time = GetTimeStr();
        cout << "[" << this_thread::get_id() << "]" << "[" << time << "]" \
            << "[" << file << ":" << line << " in " << function << "]" << "[ERROR]" << msg << endl;
    }

    void Notify(string file, string function, int line, string msg){
        char *time = GetTimeStr();
        cout << "[" << this_thread::get_id() << "]" << "[" << time << "]" \
            << "[" << file << ":" << line << " in " << function << "]" << "[NOTE]" << msg << endl;
    }

    void Debug(string file, string function, int line, string msg){
        char *time = GetTimeStr();
        if (_DEBUG)
        {
            cout << "[" << this_thread::get_id() << "]" << "[" << time << "]" \
                << "[" << file << ":" << line << " in " << function << "]" << "[DEBUG]" << msg << endl;
        }
    }
}

#define GPRINTW(MSG) ({Print::Warn(__FILE__, __FUNCTION__,__LINE__,MSG);})
#define GPRINTE(MSG) ({Print::Error(__FILE__,__FUNCTION__,__LINE__,MSG);})
#define GPRINTN(MSG) ({Print::Notify(__FILE__,__FUNCTION__,__LINE__,MSG);})
#define GPRINTD(MSG) ({Print::Debug(__FILE__,__FUNCTION__,__LINE__,MSG);})
// end region print

// region auto buffer
class CLoopBuffer
{
    public:
        CLoopBuffer(int size);
        ~CLoopBuffer();
        void Reset();
        bool Write(char* content, int size);
        bool Read(char* content, int size);
        int GetReadSize();
        int GetWriteableSize();
        int GetReadableSize();
    private:
        char* _read_ptr;
        char* _write_ptr;
        char* _malloc_start_ptr;
        char* _malloc_end_ptr;
        int _malloc_real_size;
        void _PrintPtr();
};

CLoopBuffer::CLoopBuffer(int size)
{
    this->_malloc_start_ptr = (char *)malloc(sizeof(char) * size);
    this->_malloc_real_size = malloc_usable_size(this->_malloc_start_ptr);
    this->_read_ptr = this->_malloc_start_ptr;
    this->_write_ptr = this->_malloc_start_ptr;
    this->_malloc_end_ptr = this->_malloc_start_ptr + this->_malloc_real_size - 1;
}

CLoopBuffer::~CLoopBuffer()
{
    free(this->_malloc_start_ptr);
    this->_malloc_start_ptr = NULL;
    this->_malloc_end_ptr = NULL;
    this->_read_ptr = NULL;
    this->_write_ptr = NULL;
}

void CLoopBuffer::_PrintPtr()
{
    cout << "_malloc_start_ptr: " << (void *)this->_malloc_start_ptr << endl \
        << "_malloc_end_ptr: " << (void *)this->_malloc_end_ptr << endl \
        << "_read_ptr: " << (void *)this->_read_ptr << endl \
        << "_write_ptr: " << (void *)this->_write_ptr << endl;
}

void CLoopBuffer::Reset()
{
    this->_read_ptr = this->_malloc_start_ptr;
    this->_write_ptr = this->_malloc_start_ptr;
}

int CLoopBuffer::GetWriteableSize()
{
    if (this->_write_ptr > this->_read_ptr || this->_write_ptr == this->_read_ptr)
    {
        return (this->_malloc_end_ptr - this->_write_ptr + 1) + (this->_read_ptr - this->_malloc_start_ptr);
    }
    else
    {
        return (this->_read_ptr - this->_write_ptr);
    }
}

int CLoopBuffer::GetReadableSize()
{
    if (this->_read_ptr < this->_write_ptr || this->_read_ptr == this->_write_ptr)
    {
        return (this->_write_ptr - this->_read_ptr);
    }
    else
    {
        return (this->_malloc_end_ptr - this->_read_ptr + 1) + (this->_write_ptr - this->_malloc_start_ptr);
    }
}

int CLoopBuffer::GetReadSize()
{
    int readable_size = this->GetReadableSize();
    if (readable_size == 0) return 0;
    else{
        int size = 0;
        if (this->_read_ptr < this->_write_ptr)
        {
            for (int i = 0; i < readable_size; i++)
            {
                if (*(this->_read_ptr + i) == '\0'){
                    return size+1;
                }
                else{
                    size = size + 1;
                }
            }
            return size;
        }
        else
        {
            int to_end_size = this->_malloc_end_ptr - this->_read_ptr + 1;
            int start_to_size = this->_write_ptr - this->_malloc_start_ptr;
            for (int i = 0; i < to_end_size; i++)
            {
                if (*(this->_read_ptr + i) == '\0')
                {
                    return size+1;
                }
                else{
                    size = size + 1;
                }
            }
            for (int i = 0; i < start_to_size; i++)
            {
                if (*(this->_malloc_start_ptr + i) == '\0')
                {
                    return size+1;
                }
                else{
                    size = size + 1;
                }
            }
            return size;
        }
    }
}

bool CLoopBuffer::Write(char* content, int size)
{
    if (this->GetWriteableSize() < size)
    {
        GPRINTE("size tool large");
        return false;
    }
    if (this->_write_ptr + size > this->_malloc_end_ptr)
    {
        int to_end_size = this->_malloc_end_ptr - this->_write_ptr + 1;
        int start_to_size = size - to_end_size;
        void* ret1 = memmove(this->_write_ptr, content, to_end_size);
        void* ret2 = memmove(this->_malloc_start_ptr, content + to_end_size, start_to_size);
        if (ret1 && ret2){
            this->_write_ptr = this->_malloc_start_ptr + start_to_size;
            return true;
        }
        else{
            GPRINTE("memmove failed");
            return false;
        }
    }
    else
    {
        void* ret3 = memmove(this->_write_ptr, content, size);
        if (ret3)
        {
            this->_write_ptr = this->_write_ptr + size;
            return true;
        }
        else{
            GPRINTE("memmove failed");
            return false;
        }
    }
    return true;
}

bool CLoopBuffer::Read(char *content, int size)
{
    int readable_size = this->GetReadableSize();
    if (readable_size == 0)
    {
        GPRINTE("nothing to read");
        return false;
    }
    if (this->_read_ptr + size < this->_malloc_end_ptr || this->_read_ptr + size == this->_malloc_end_ptr)
    {
        void* ret = memmove(content, this->_read_ptr, size);
        if (ret)
        {
            this->_read_ptr = this->_read_ptr + size;
            return true;
        }
        else{
            GPRINTE("memmove failed");
            return false;
        }
    }
    else
    {
        int to_end_size = this->_malloc_end_ptr - this->_read_ptr + 1;
        int start_to_size = size - to_end_size;
        void* ret1 = memmove(content, this->_read_ptr, to_end_size);
        void* ret2 = memmove(content+to_end_size, this->_malloc_start_ptr, start_to_size);
        if (ret1 && ret2)
        {
            this->_read_ptr = this->_malloc_start_ptr + (size - to_end_size);
            return true;
        }
        else{
            GPRINTE("memmove failed");
            return false;
        }
    }
}
// end region auto buffer

// region os
class CNetBase;

class COSHandler
{
    public:
        virtual void CheckOS(struct NetParam* np) = 0;
        virtual int CreateSocket(struct NetParam* np) = 0;
        virtual int SetSocketNonBlocking(int socket) = 0;
        virtual bool Bind(int socket, struct NetParam* np) = 0;
        virtual bool Listen(int socket, int backlog_len) = 0;
        virtual bool GenerateSocketEvent(int socket, struct NetThread_Linux* nt) = 0;
        virtual void EventLoop(struct NetThread_Linux* nt, CNetBase *net_base) = 0;
        virtual void Accept(int socket, struct sockaddr_in* client_addr, socklen_t* addr_len, \
                int epoll_fd, struct NetThread_Linux* nt) = 0;
        virtual void Receive(struct NetThread_Linux* nt, char* buffer, CNetBase *net_base) = 0;
        virtual void Disconnect(struct NetThread_Linux* nt) = 0;
        virtual bool Send(struct NetThread_Linux* nt, char* buffer, int size, int flag) = 0;
        virtual bool HandleSocketListener(struct NetThread_Linux* nt, int events, int type)=0;
    protected:
        void _WrongOS(){GPRINTE("Unsupport operate system!");exit(EXIT_FAILURE);};
};

class CLinuxHandler : public COSHandler
{
    public:
        virtual void CheckOS(struct NetParam* np);
        virtual int CreateSocket(struct NetParam* np);
        virtual int SetSocketNonBlocking(int socket);
        virtual bool Bind(int socket, struct NetParam* np);
        virtual bool Listen(int socket, int backlog_len);
        virtual bool GenerateSocketEvent(int socket, struct NetThread_Linux* nt);
        virtual void EventLoop(struct NetThread_Linux* nt, CNetBase *net_base);
        virtual void Accept(int socket, struct sockaddr_in* client_addr, socklen_t* addr_len, \
                int epoll_fd, struct NetThread_Linux* nt);
        virtual void Receive(struct NetThread_Linux* nt, char* buffer, CNetBase *net_base);
        virtual void Disconnect(struct NetThread_Linux* nt);
        virtual bool Send(struct NetThread_Linux* nt, char* buffer, int size, int flag);
        virtual bool HandleSocketListener(struct NetThread_Linux* nt, int events, int type);
        int SetSocketReusePort(int socket);
        void Writeable(struct NetThread_Linux* nt, CNetBase *net_base);
};

class COtherOSHandler : public COSHandler
{
    public:
        virtual void CheckOS(struct NetParam* np){this->_WrongOS();};
};

class CSocketUser: public std::enable_shared_from_this<CSocketUser>
{
    public:
        CSocketUser(struct NetThread_Linux* nt);
        ~CSocketUser(){free(this->_nt);};
        static shared_ptr<CSocketUser> GetSocketUser(int fd_socket);
        static size_t DelSocketUser(int fd_socket);

        bool Send(string buffer, int flag);
        void Disconnect();

        void ResetRecvBuffer();
        void ResetSendBuffer();
        string Read();
        string ReadAll();
        int GetReadableSize();
        int GetReadSize();
        bool Read(char* content, int size);
        void SetWriteable();
        void AddSocketUser();
        void SetAddr(struct sockaddr *addr);
        const char* GetIP(char *buff, int size);
        int GetPort();
        int GetSocketFD();

        shared_ptr<CLoopBuffer> _GetRecvBuffer();
        shared_ptr<CLoopBuffer> _GetSendBuffer();
    private:
        struct sockaddr* _addr;
        struct NetThread_Linux* _nt;
        shared_ptr<COSHandler> _os_handler;
        shared_ptr<CLoopBuffer> _recv_buffer;
        shared_ptr<CLoopBuffer> _send_buffer;
        static thread_local unordered_map<uint64_t, shared_ptr<CSocketUser>> __all_socket_map;
};

void CLinuxHandler::CheckOS(struct NetParam* np)
{
    uint32_t cpu_num = thread::hardware_concurrency();
    int os_version = LINUX_VERSION_CODE;

#if LINUX_VERSION_CODE < KERNEL_VERSION(4,5,0)
    GPRINTE("your kernel version is not satisfied, please update!");
    exit(EXIT_FAILURE);
#endif

    if ((np->thread_num == 0 || np->thread_num > 2 * cpu_num) && !_DEBUG)
    {
        np->thread_num = cpu_num;
    }
    string thread_num_change = np->raw_thread_num + "->" + to_string(np->thread_num);

    string os_info = "current os info\nos:\t\t linux\nversion code:\t";
    os_info = os_info + to_string(os_version) + "\ncpu num:\t" + to_string(cpu_num) + \
        "\nip:\t\t" + np->raw_ip + "\nport:\t\t" + np->raw_port + "\nthread num:\t" + thread_num_change + \
        "\nos check finish, the server process is ready ...";
    GPRINTN(os_info);
}

int CLinuxHandler::CreateSocket(struct NetParam* np)
{
    int socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (socket_fd < 0)
    {
        GPRINTE("create socket error");
        perror("create socket");
        return -1;
    }
    if (_NONBLOCK)
    {
        this->SetSocketNonBlocking(socket_fd);
    }
    if (_REUSEPORT)
    {
        this->SetSocketReusePort(socket_fd);
    }
    return socket_fd;
}

int CLinuxHandler::SetSocketNonBlocking(int socket)
{
    int old_option = fcntl(socket, F_GETFL);
    if (old_option < 0)
    {
        GPRINTE("get fcntl flag error");
        perror("get fcnt");
        return -1;
    }
    int new_option = old_option | O_NONBLOCK;
    if (fcntl(socket, F_SETFL, new_option) < 0)
    {
        GPRINTE("set fcntl non blocking error");
        perror("set fcnt");
        return -1;
    }
    return old_option;
}

int CLinuxHandler::SetSocketReusePort(int socket) {
    int opt = 1;
    int ret = setsockopt(socket, SOL_SOCKET, SO_REUSEPORT,
        &opt, static_cast<socklen_t>(sizeof(opt)));
    return ret;
}

bool CLinuxHandler::Bind(int socket, struct NetParam* np)
{
    struct sockaddr_in *server_addr = (struct sockaddr_in *)malloc(sizeof(struct sockaddr_in));
    memset(server_addr, 0, sizeof(struct sockaddr_in));

    server_addr->sin_family = AF_INET;
    server_addr->sin_addr.s_addr = np->ip;
    server_addr->sin_port = htons(np->port);

    if (bind(socket, (const struct sockaddr *)server_addr, sizeof(*server_addr)) < 0)
    {
        GPRINTE("socket bind failed!");
        perror("bind");
        free(server_addr);
        close(socket);
        return false;
    }
    free(server_addr);
    return true;
}

bool CLinuxHandler::Listen(int socket, int backlog_len)
{
    if (backlog_len < 1)
    {
        backlog_len = SOMAXCONN;
    }
    int ret = listen(socket, backlog_len);
    if (ret < 0)
    {
        GPRINTE("socket listen failed!");
        perror("listen");
        close(socket);
        return false;
    }
    return true;
}

bool CLinuxHandler::GenerateSocketEvent(int socket, struct NetThread_Linux* nt)
{
    int epoll_fd = epoll_create(2);
    if (epoll_fd < 0)
    {
        GPRINTE("epoll_create failed!");
        perror("epoll_create");
        close(socket);
        return false;
    }
    nt->fd_socket = socket;
    nt->fd_epoll = epoll_fd;
    nt->writable = false;
    return true;
}

bool CLinuxHandler::HandleSocketListener(struct NetThread_Linux* nt, int events, int type)
{
    struct epoll_event ev;
    ev.events = events;
    ev.data.ptr = nt;
    int ret;
    if (type == 0){
        ret = epoll_ctl(nt->fd_epoll, EPOLL_CTL_MOD, nt->fd_socket, &ev);
    }
    else if (type < 0)
    {
        ret = epoll_ctl(nt->fd_epoll, EPOLL_CTL_DEL, nt->fd_socket, &ev);
    }
    else{
        ret = epoll_ctl(nt->fd_epoll, EPOLL_CTL_ADD, nt->fd_socket, &ev);
    }
    if (ret < 0)
    {
        GPRINTE("epollctl add failed! closing ...");
        perror("epollctl add failed");
        close(nt->fd_epoll);
        close(nt->fd_socket);
        return false;
    }
    return true;
}

void CLinuxHandler::EventLoop(struct NetThread_Linux* nt, CNetBase *net_base)
{
    GPRINTD("Loop Start");
    struct epoll_event *ev = (struct epoll_event *)malloc(sizeof(struct epoll_event)*_MAX_EPOLL_WAIT_EVENT_SIZE);
    struct sockaddr_in *client_addr = (struct sockaddr_in *)malloc(sizeof(struct sockaddr_in));
    struct NetThread_Linux *client_nt = (struct NetThread_Linux *)malloc(sizeof(struct NetThread_Linux));
    socklen_t sock_len = sizeof(struct sockaddr_in);
    char *buffer = (char *)malloc(sizeof(char)*_MAX_RECEIVE_ONCE_SIZE);
    while(true)
    {
        memset(ev, 0, sizeof(struct epoll_event)*_MAX_EPOLL_WAIT_EVENT_SIZE);
        int num_fds = epoll_wait(nt->fd_epoll, ev, _MAX_EPOLL_WAIT_EVENT_SIZE, -1);
        if (num_fds < 0)
        {
            if (errno == EINTR)
            {
                continue;
            }
            else
            {
                GPRINTE("epoll wait error!");
                perror("epoll wait");
                return;
            }
        }
        else if (num_fds == 0)
        {
            continue;
        }
        else
        {
            for (int i = 0; i < num_fds; i++)
            {
                struct NetThread_Linux* nt_new = (struct NetThread_Linux*)ev[i].data.ptr;
                if (nt_new->fd_socket == nt->fd_socket)
                {
                    GPRINTD("wake up");
                    memset(client_addr, 0, sizeof(sizeof(struct sockaddr_in)));
                    memset(client_nt, 0, sizeof(struct NetThread_Linux));
                    this->Accept(nt->fd_socket, client_addr, &sock_len, nt->fd_epoll, client_nt);
                }
                else if (ev[i].events & EPOLLIN)
                {
                    if (ev[i].events & EPOLLRDHUP)
                    {
                        this->Disconnect(nt_new);
                        continue;
                    }
                    this->Receive(nt_new, buffer, net_base);
                }
                else if (ev[i].events & EPOLLOUT)
                {
                    this->Writeable(nt_new, net_base);
                }
            }
        }
    }
    free(ev);
    free(client_addr);
    free(client_nt);
}

bool CLinuxHandler::Send(struct NetThread_Linux* nt, char* buffer, int size, int flag)
{
    int ret = send(nt->fd_socket, buffer, size, 0);
    if (ret < 0)
    {
        GPRINTW("send failed, put in cache, send agian when receive epoll out event");
        return false;
    }
    return true;
}

thread_local unordered_map<uint64_t, shared_ptr<CSocketUser>> CSocketUser::__all_socket_map;

CSocketUser::CSocketUser(struct NetThread_Linux* nt)
{
#if EPOLL_OS
    this->_os_handler = make_shared<CLinuxHandler>();
#else
    this->_os_handler = make_shared<COtherOSHandler>();
#endif

    this->_nt = (struct NetThread_Linux*)malloc(sizeof(struct NetThread_Linux));
    this->_nt->fd_epoll = nt->fd_epoll;
    this->_nt->fd_socket = nt->fd_socket;
    this->_nt->writable = nt->writable;

    this->_addr = (struct sockaddr *)malloc(sizeof(struct sockaddr));

    this->_recv_buffer = make_shared<CLoopBuffer>(_MAX_RECEIVE_BUFFER_SIZE);
    this->_send_buffer = make_shared<CLoopBuffer>(_MAX_SEND_BUFFER_SIZE);
}

void CSocketUser::SetAddr(struct sockaddr *addr)
{
    memmove(this->_addr, addr, sizeof(struct sockaddr));
}

void CSocketUser::AddSocketUser()
{
    CSocketUser::__all_socket_map[this->_nt->fd_socket] = shared_from_this();
}

shared_ptr<CLoopBuffer> CSocketUser::_GetRecvBuffer()
{
    return this->_recv_buffer;
}

shared_ptr<CLoopBuffer> CSocketUser::_GetSendBuffer()
{
    return this->_send_buffer;
}

shared_ptr<CSocketUser> CSocketUser::GetSocketUser(int fd_socket)
{
    bool in_map = CSocketUser::__all_socket_map.find(fd_socket) != CSocketUser::__all_socket_map.end()? true:false;
    if (in_map)
    {
        return CSocketUser::__all_socket_map.at(fd_socket);
    }
    else
    {
        return NULL;
    }
}

size_t CSocketUser::DelSocketUser(int fd_socket)
{
    return CSocketUser::__all_socket_map.erase(fd_socket);
}

bool CSocketUser::Send(string buffer, int flag = 0)
{
    int size = buffer.length() + 1;
    const char* send_const = buffer.c_str();
    char* send = nullptr;
    send = const_cast<char *>(send_const);
    if (this->_nt->writable)
    {
        bool ret = this->_os_handler->Send(this->_nt, send, size, flag);
        if (ret){
            return true;
        }
    }
    this->_nt->writable = false;
    bool ret = (this->_GetSendBuffer())->Write(send, size);
    this->_os_handler->HandleSocketListener(this->_nt, EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET|EPOLLONESHOT, 0);
    if (ret){
        return true;
    }
    else{
        return false;
    }
}

void CSocketUser::Disconnect()
{
    this->_os_handler->Disconnect(this->_nt);
}

void CSocketUser::ResetRecvBuffer()
{
    (this->_GetRecvBuffer())->Reset();
}

void CSocketUser::ResetSendBuffer()
{
    (this->_GetSendBuffer())->Reset();
}

string CSocketUser::Read()
{
    int size = (this->_GetRecvBuffer())->GetReadSize();
    char* content = (char *)malloc(sizeof(char) * size);
    string result;
    if ((this->_GetRecvBuffer())->Read(content, size))
    {
        result = content;
    }
    return result;
}

string CSocketUser::ReadAll()
{
    int size = (this->_GetRecvBuffer())->GetReadableSize();
    char* content = (char *)malloc(sizeof(char) * size);
    string result;
    if ((this->_GetRecvBuffer())->Read(content, size))
    {
        result = content;
    }
    return result;
}

int CSocketUser::GetReadableSize()
{
    return (this->_GetRecvBuffer())->GetReadableSize();
}

int CSocketUser::GetReadSize()
{
    return (this->_GetRecvBuffer())->GetReadSize();
}

bool CSocketUser::Read(char* content, int size)
{
    return (this->_GetRecvBuffer())->Read(content, size);
}

void CSocketUser::SetWriteable()
{
    this->_nt->writable = true;
}

const char* CSocketUser::GetIP(char *buff, int size)
{
    struct sockaddr_in *addr = (struct sockaddr_in*)this->_addr;
    return inet_ntop(AF_INET, &addr->sin_addr, buff, size);
}

int CSocketUser::GetPort()
{
    struct sockaddr_in *addr = (struct sockaddr_in*)this->_addr;
    return addr->sin_port;
}

int CSocketUser::GetSocketFD()
{
    return this->_nt->fd_socket;
}
//end region os

typedef std::shared_ptr<CSocketUser> SocketUser;

// region net
class CNetBase
{
    public:
        CNetBase(struct NetParam* np);
        ~CNetBase(){
            free(_net_param);
            _net_param = NULL;
            for (int i = 0; i < this->vec_event.size(); i++)
            {
                close(vec_event[i].fd_socket);
                close(vec_event[i].fd_epoll);
            }
        };
        void PrintNetParam(){cout << this->_net_param->ip << " " << this->_net_param->port << " " << this->_net_param->thread_num << endl;};
        struct NetParam* GetPeer(){return this->_net_param;};
        void Run();
        static void ThreadBoot(CNetBase* net_base, struct NetThread_Linux* nt);

    private:
        struct NetParam* _net_param;
        shared_ptr<COSHandler> _os_handler;
#if EPOLL_OS
        vector<struct NetThread_Linux> vec_event;
#else
        vector<struct NetThread_Other> vec_event;
#endif
};

CNetBase::CNetBase(struct NetParam* np)
{
    this->_net_param = np;
    np = NULL;
#if EPOLL_OS
    this->_os_handler = make_shared<CLinuxHandler>();
#else
    this->_os_handler = make_shared<COtherOSHandler>();
#endif
    this->_os_handler->CheckOS(this->_net_param);
}

void CNetBase::Run()
{
    int socket;
    for (int i = 0; i < this->_net_param->thread_num; i++)
    {
        socket = this->_os_handler->CreateSocket(this->_net_param);
        if (socket < 0)
        {
            exit(EXIT_FAILURE);
        }
        if (!this->_os_handler->Bind(socket, this->_net_param))
        {
            exit(EXIT_FAILURE);
        }
        if (!this->_os_handler->Listen(socket, 0))
        {
            exit(EXIT_FAILURE);
        }
        struct NetThread_Linux nt;
        if (this->_os_handler->GenerateSocketEvent(socket, &nt))
        {
            this->vec_event.push_back(nt);
        }
        else
        {
            close(socket);
            continue;
        }
    }

    if (this->_net_param->thread_num != this->vec_event.size() && !_ALLOW_THREAD_INCOMPLETE)
    {
        string notify = "plan to start thread num is ";
        notify = notify + to_string(this->_net_param->thread_num) + ", ";
        notify = notify + "but in fact start thread num is " + to_string(this->vec_event.size());
        GPRINTN(notify);
        GPRINTE("because of _ALLOW_THREAD_INCOMPLETE(false), server will quit ...");
        for (int i = 0; i < this->vec_event.size(); i++)
        {
            close(this->vec_event[i].fd_socket);
            close(this->vec_event[i].fd_epoll);
        }
        exit(EXIT_FAILURE);
    }

    vector<shared_ptr<thread>> _thread_vec;
    for (int i = 0; i < this->vec_event.size(); i++)
    {
        shared_ptr<thread> thd(new thread(CNetBase::ThreadBoot, this, &(this->vec_event[i])));
        _thread_vec.push_back(thd);
    }
    for (size_t i = 0; i < _thread_vec.size(); i++) {
        _thread_vec[i]->join();
    }
}

void CNetBase::ThreadBoot(CNetBase* net_base, struct NetThread_Linux* nt)
{
    if (!net_base->_os_handler->HandleSocketListener(nt, EPOLLIN|EPOLLRDHUP|EPOLLET|EPOLLONESHOT, 1))
    {
        GPRINTE("epoll add listener error!");
        perror("epoll add listener");
        return;
    }
    net_base->_os_handler->EventLoop(nt, net_base);
}

class CNet
{
    public:
        CNet(){};
        ~CNet(){};

        void CheckNetParam(char* ip, char* port, char* thread_num, struct NetParam* np);
        void Init(char* ip, char* port, char* thread_num);
        void PrintNetParam(){this->_net_base->PrintNetParam();};
        void Run();

        static void(* cb_accept)(shared_ptr<CSocketUser> socket_user);
        static void(* cb_receive)(shared_ptr<CSocketUser> socket_user);
        static void(* cb_disconnect)(shared_ptr<CSocketUser> socket_user);
        static void(* cb_writeable)(shared_ptr<CSocketUser> socket_user);

        static void ExcuteAcceptCallBack(SocketUser socket_user);
        static void ExcuteReceiveCallBack(SocketUser socket_user);
        static void ExcuteDisconnectCallBack(SocketUser socket_user);
        static void ExcuteWriteableCallBack(SocketUser socket_user);

        static void SetAcceptCallBack(void(* cb_accept)(shared_ptr<CSocketUser> socket_user));
        static void SetReceiveCallBack(void(* cb_receive)(shared_ptr<CSocketUser> socket_user));
        static void SetDisconnectCallBack(void(* cb_disconnect)(shared_ptr<CSocketUser> socket_user));
        static void SetWriteableCallBack(void(* cb_writeable)(shared_ptr<CSocketUser> socket_user));

    private:
        shared_ptr<CNetBase> _net_base;
};

// region cb func

void AcceptCallBack(SocketUser socket_user)
{
    GPRINTD("accept callback");
    char buff[_IP_INFO_LEN];
    cout << "IP: " << socket_user->GetIP(buff, _IP_INFO_LEN) << endl;
    cout << "Port: " << socket_user->GetPort() << endl;
    cout << "fd: " << socket_user->GetSocketFD() << endl;
}

void ReceiveCallBack(SocketUser socket_user)
{
    GPRINTD("receive callback");
    string result = socket_user->Read();
    cout << "receive: " << result << endl;

    socket_user->Send(result);
}

void DisconnectCallBack(SocketUser socket_user)
{
    GPRINTD("disconnect callback");
}

void WritetableCallBack(SocketUser socket_user)
{
    GPRINTD("writeable callback");
}
// end region cb func

void(* CNet::cb_accept)(shared_ptr<CSocketUser> socket_user) = AcceptCallBack;
void(* CNet::cb_receive)(shared_ptr<CSocketUser> socket_user) = ReceiveCallBack;
void(* CNet::cb_disconnect)(shared_ptr<CSocketUser> socket_user) = DisconnectCallBack;
void(* CNet::cb_writeable)(shared_ptr<CSocketUser> socket_user) = WritetableCallBack;

void CNet::ExcuteAcceptCallBack(SocketUser socket_user)
{
    if (CNet::cb_accept)
    {
        CNet::cb_accept(socket_user);
    }
}

void CNet::ExcuteReceiveCallBack(SocketUser socket_user)
{
    if (CNet::cb_receive)
    {
        CNet::cb_receive(socket_user);
    }
}

void CNet::ExcuteDisconnectCallBack(SocketUser socket_user)
{
    if (CNet::cb_disconnect)
    {
        CNet::cb_disconnect(socket_user);
    }
}

void CNet::ExcuteWriteableCallBack(SocketUser socket_user)
{
    if (CNet::cb_writeable)
    {
        CNet::cb_writeable(socket_user);
    }
}

void CNet::SetAcceptCallBack(void(* cb_accept)(shared_ptr<CSocketUser> socket_user))
{
    CNet::cb_accept = cb_accept;
}

void CNet::SetReceiveCallBack(void(* cb_receive)(shared_ptr<CSocketUser> socket_user))
{
    CNet::cb_receive = cb_receive;
}

void CNet::SetDisconnectCallBack(void(* cb_disconnect)(shared_ptr<CSocketUser> socket_user))
{
    CNet::cb_disconnect = cb_disconnect;
}

void CNet::SetWriteableCallBack(void(* cb_writeable)(shared_ptr<CSocketUser> socket_user))
{
    CNet::cb_writeable = cb_writeable;
}

void CNet::CheckNetParam(char* ip, char* port, char* thread_num, struct NetParam* np)
{
    np->raw_ip = ip;
    np->raw_port = port;
    np->raw_thread_num = thread_num;
    in_addr_t addr = inet_addr(ip);
    if (addr == INADDR_NONE)
    {
        GPRINTE("invalid ip");
        exit(EXIT_FAILURE);
    }

    short nport = atoi(port);
    if ((nport <= 0) || (nport >= 65535))
    {
        GPRINTE("invalid port");
        exit(EXIT_FAILURE);
    }

    short nthread_num = atoi(thread_num);

    np->ip = addr;
    np->port = nport;
    np->thread_num = nthread_num;
}

void CNet::Init(char* ip, char* port, char* thread_num){
    struct NetParam* np = (struct NetParam*)malloc(sizeof(struct NetParam));
    if (np == NULL)
    {
        free(np);
        GPRINTE("memory malloc netparam failed");
        exit(EXIT_FAILURE);
    }
    memset(np, 0, sizeof(struct NetParam));
    this->CheckNetParam(ip, port, thread_num, np);
    if (!this->_net_base)
    {
        this->_net_base = make_shared<CNetBase>(np);
    }
    else{
        GPRINTW("repeat init net!");
    }
}

void CNet::Run()
{
    this->_net_base->Run();
}

void CLinuxHandler::Accept(int socket, struct sockaddr_in* client_addr, socklen_t* addr_len, int epoll_fd, \
        struct NetThread_Linux* client_nt)
{
    while(true)
    {
        int client_fd = accept(socket, (struct sockaddr *)client_addr, addr_len);
        if (client_fd < 0)
        {
            if (errno == EAGAIN) break;
            GPRINTE("accept failed!");
            perror("accept failed");
            break;
        }
        this->SetSocketNonBlocking(client_fd);

        client_nt->fd_epoll = epoll_fd;
        client_nt->fd_socket = client_fd;
        client_nt->writable = true;
        this->HandleSocketListener(client_nt, EPOLLIN|EPOLLRDHUP|EPOLLET|EPOLLONESHOT, 1);

        shared_ptr<CSocketUser> socket_user = make_shared<CSocketUser>(client_nt);
        socket_user->AddSocketUser();
        socket_user->SetAddr((struct sockaddr *)client_addr);

        //cb(socket);
        GPRINTD("accept success");
        CNet::ExcuteAcceptCallBack(socket_user);
    }
}

void CLinuxHandler::Disconnect(struct NetThread_Linux* nt)
{
    GPRINTN("client close socket positively fd: " + to_string(nt->fd_socket));
    this->HandleSocketListener(nt, EPOLLIN|EPOLLOUT|EPOLLRDHUP|EPOLLET|EPOLLONESHOT, -1);
    close(nt->fd_socket);

    CNet::ExcuteDisconnectCallBack(CSocketUser::GetSocketUser(nt->fd_socket));
    CSocketUser::DelSocketUser(nt->fd_socket);
}

void CLinuxHandler::Receive(struct NetThread_Linux* nt, char* buffer, CNetBase *net_base)
{
    while(true)
    {
        memset(buffer, 0, sizeof(*buffer));
        int byte_len = recv(nt->fd_socket, buffer, _MAX_RECEIVE_ONCE_SIZE, 0);
        switch(byte_len)
        {
            case -1:
                this->HandleSocketListener(nt, EPOLLIN|EPOLLRDHUP|EPOLLET|EPOLLONESHOT, 0);
                CNet::ExcuteReceiveCallBack(CSocketUser::GetSocketUser(nt->fd_socket));
                return;
            case 0:
                return;
            default:
                if (byte_len < _MAX_RECEIVE_ONCE_SIZE){
                    if (buffer[byte_len-1] != '\0'){
                        buffer[byte_len] = '\0';
                        byte_len = byte_len + 1;
                    }
                }
                auto socket_user = CSocketUser::GetSocketUser(nt->fd_socket);
                if (socket_user){
                    (socket_user->_GetRecvBuffer())->Write(buffer, byte_len);
                    //cb(socket_user);
                }
                else{
                    GPRINTE("no socket_user!");
                    return;
                }
        }
    }
}

void CLinuxHandler::Writeable(struct NetThread_Linux* nt, CNetBase *net_base)
{
    auto socket_user = CSocketUser::GetSocketUser(nt->fd_socket);
    if (socket_user != NULL)
    {
        GPRINTN("set socket writable"+to_string(nt->fd_socket));
        socket_user->SetWriteable();
        this->HandleSocketListener(nt, EPOLLIN|EPOLLRDHUP|EPOLLET|EPOLLONESHOT, 0);
        CNet::ExcuteWriteableCallBack(socket_user);
    }
}
// end region net

void AcceptCallBack2(SocketUser socket_user)
{
    GPRINTD("accept callback22222");
    char buff[_IP_INFO_LEN];
    cout << "IP: " << socket_user->GetIP(buff, _IP_INFO_LEN) << endl;
    cout << "Port: " << socket_user->GetPort() << endl;
    cout << "fd: " << socket_user->GetSocketFD() << endl;
}

int main(int argc, char* argv[])
{
    // parameters check
    if(argc != 4)
    {
        cout<< "usage: ./" << basename(argv[0]) << " [ip] [port] [thread_num]\n";
        exit(EXIT_FAILURE);
    }

    CNet net;
    net.Init(argv[1], argv[2], argv[3]);
    CNet::SetAcceptCallBack(AcceptCallBack2);

    net.Run();
    return 0;
}