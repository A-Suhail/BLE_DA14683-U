/**
 ****************************************************************************************
 *
 * @file gdb_server_cmds.c
 *
 * @brief GDB Server interface
 *
 * Copyright (C) 2015-2018 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */
#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <fcntl.h>
#include <ctype.h>
#include <errno.h>
#include <time.h>
#ifdef WIN32
#include <winsock.h>
#include <shlwapi.h>
#include <tlhelp32.h>
#include <winternl.h>
#include <setupapi.h>
#include <cfgmgr32.h>
#include <windows.h>
#include <ntstatus.h>
#define inline __inline
#define sleep(s) Sleep((s) * 1000)
#define strdup _strdup
#define socket_error() WSAGetLastError()
#ifdef EADDRINUSE /* Occasional conflict with POSIX error code in errno.h */
#undef EADDRINUSE
#endif
#define EADDRINUSE WSAEADDRINUSE
#else
#include <unistd.h>
#include <netdb.h>
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <signal.h>
#include <sys/wait.h>
#define closesocket close
#define socket_error() errno
#endif
#include "programmer.h"
#include "gdb_server_cmds.h"

#define ACK '\x06'
#define NAK '\x15'

#ifndef GDB_RECONNECT_MAX_TIME_MS
#define GDB_RECONNECT_MAX_TIME_MS       2000
#endif
#define GDB_SERVER_CLOSE_MAX_TIME_MS    4000
#define GDB_LOCAL_CMD_EXE               "qRcmd"
#define GDB_CONTINUE                    "$c#63"
#define GDB_STEP                        "$s#73"
#define SOH                             '\x01'
/*
 * Buffer should contain 64kB of data (size of OTP memory) encoded 2 bytes per each data byte and
 * additional frame characters
 */
#define MAX_BUF_LEN                     132000
#define MAX_READ_SIZE                   0x10000
#define ADDRESS_TMP                     (0xFFFFFFFF)
#define GDB_SERVER_REPEATS_LIMIT        3
#define DBG_GDB_SERVER                  0
#define ACK_CHAR                        '+'
#define NACK_CHAR                       '-'
#define CHUNK_SIZE                      0x2000

#define GDB_SERVER_INSTANCES_LIMIT      100
#define GDB_SERVER_DEFAULT_PORT         2331
#define JLINK_DEVICE_LIMIT              100
#define TARGET_LEN_LIMIT                100000
#define HANDLES_START_NUM               10000
#define JLINK_VID                       "1366"
#define JLINK_PRO_PID                   "0101"
#define JLINK_LITE_PID                  "0105"
#define JLINK_PRO_PREFIX                "USB#VID_" JLINK_VID "&PID_" JLINK_PRO_PID "#"
#define JLINK_LITE_PREFIX               "USB#VID_" JLINK_VID "&PID_" JLINK_LITE_PID "&"
#define JLINK_PARENT_PREFIX             "USB\\VID_" JLINK_VID "&PID_" JLINK_LITE_PID "\\"
#define JLINK_INTERFACE                 "54654e76-dcf7-4a7f-878a-4e8fca0acc9a"

#define UARTBOOT_LIVE_MARKER            "Live"

typedef struct {
        uint32_t run_swd_addr;
        uint32_t cmd_num_addr;
        uint32_t cmd_buf_addr;
        uint32_t buf_addr;
        uint32_t ack_nak_addr;
} swd_if_addr_t;

typedef struct {
        uint32_t len;
        uint8_t buf[MAX_BUF_LEN];
} recv_buf_t;

#ifdef WIN32
typedef struct {
        long long sn;
        char dev_name[100];
} jlink_dev_t;
#endif

const char marker[] = "DBGP";

static uint8_t *boot_loader_code;
static size_t boot_loader_size;

/* struct with swd important addresses in uartboot */
static swd_if_addr_t swd_addr;
/* local copy of command number from uartboot */
static uint32_t cmd_num_cp;
/* GDB Server socket */
static int gdb_server_sock = -1;
/* buffer for GDB Server responses */
static recv_buf_t gdb_server_recv_buf = {/* .len = */ 0};
/* flag indicates that the uartboot code was loaded on platform */
static bool uartboot_loaded = false;
/* GDB Server configuration */
static prog_gdb_server_config_t configuration;
#ifdef WIN32
/* GDB Server handle */
static DWORD gdb_server_pid;
static HANDLE gdb_server_handle = INVALID_HANDLE_VALUE;
#else
/* GDB Server PID */
static pid_t gdb_server_pid = -1;
#endif
/* Target reset command */
extern char *target_reset_cmd;

static int gdb_server_send_swd_cmd_header(uint32_t data_len, const uint8_t *data);
int gdb_server_connect(const char *host_name, int port, bool reset);

#ifdef WIN32
typedef ULONGLONG time_ms_t;
#define gdb_server_get_current_time_ms GetProcAddress(GetModuleHandle("kernel32.dll"), "GetTickCount64")
#else
typedef long long time_ms_t;
static time_ms_t gdb_server_get_current_time_ms(void)
{
        struct timespec spec;

        clock_gettime(CLOCK_REALTIME, &spec);
        return spec.tv_sec * 1000 + spec.tv_nsec / 1000000;

}
#endif

/* set fields in swd_addr structure */
static void set_swd_addresses(void)
{
        uint32_t i;

        /* find marker "DBGP" in uartboot code */
        for (i = 0; i < boot_loader_size - 4; i++) {
                if (!memcmp(&boot_loader_code[i], marker, 4)) {
                        swd_addr.run_swd_addr = i + 4;
                        break;
                }
        }

        swd_addr.cmd_num_addr = swd_addr.run_swd_addr + sizeof(uint32_t);
        swd_addr.cmd_buf_addr = *((uint32_t *) &boot_loader_code[swd_addr.cmd_num_addr +
                                                                          sizeof(uint32_t)]);
        /* on 680 platform is 32-bits addressing */
        swd_addr.buf_addr = *((uint32_t *) &boot_loader_code[swd_addr.cmd_num_addr +
                                                                             sizeof(uint32_t) * 2]);

        swd_addr.ack_nak_addr = swd_addr.cmd_num_addr + 3 * sizeof(uint32_t);
}

/* save memory to file specified by file_path */
static int memory_to_file(const char *file_path, uint8_t *memory, uint32_t len)
{
        FILE *file = fopen(file_path, "wb");

        if (!file) {
                return ERR_FILE_OPEN;
        }

        if (fwrite(memory, 1, len, file) == -1) {
                fclose(file);
                return ERR_FILE_WRITE;
        }

        return (!fclose(file) ? 0 : ERR_FILE_CLOSE);
}

/* calculation of checksum from data */
static uint8_t checksum(const char *data, uint32_t len)
{
        uint8_t cs = 0;

        for (; len > 0; len--) {
                cs += data[len - 1];
        }

        return cs;
}

/*
 * create uint8_t from 2 characters, if cannot convert characters to number set status
 * to false and return 0xFF, otherwise return converted value and set status to true
 */
static inline uint8_t chars_to_uint8(const char up_char, const char low_char, bool *status)
{
        char digit_char[] = {up_char, low_char, '\0'};

        if (!(isxdigit(up_char) && isxdigit(low_char))) {
                *status = false;
                return 0xFF;
        }

        *status = true;
        return (uint8_t) strtoul(digit_char, NULL, 16);
}

#ifndef WIN32
/* convert upper-case characters in string to lower-case */
static void str_to_lower(const char *src, char *dest)
{
        for (; *src != '\0'; ++src) {
                *dest = tolower(*src);
                ++dest;
        }

        *dest = '\0';
}
#endif

/* check that a host_name is the localhost */
static bool is_localhost(const char *host_name)
{
        uint32_t addr = 0;

        /* try resolve host_name as address */
        if ((addr = inet_addr(host_name)) == INADDR_NONE) {
                /* get address from host_name*/
                struct hostent *host = gethostbyname(host_name);

                addr = *(uint32_t *) host->h_addr_list[0];
        }

        return htonl(addr) == INADDR_LOOPBACK;
}

/* get program name from specified path */
static void get_name_from_path(const char *path, char *name_buf)
{
#ifdef WIN32
        char path_buf[MAX_PATH];
        const char *end;
        const char *ext;
        if (*path == '"') {
                path++; /* Skip " */
                end = strchr(path, '"');
        } else {
                end = strchr(path, ' ');
        }
        if (end != NULL) {
                /* Copy till space or " */
                strncpy(path_buf, path, end - path);
                path_buf[end - path] = '\0';
        } else {
                strcpy(path_buf, path);
        }
        /* Copy just file name, discard folder if any */
        strcpy(name_buf, PathFindFileName(path_buf));

        /* Make sure file name ends with .exe since this always should be an executable */
        ext = PathFindExtension(name_buf);
        if (ext == NULL || strcasecmp(ext, ".exe")) {
                strcat(name_buf, ".exe");
        }
#else
        int i;
        int last_slash_pos = -1;
        int name_length = 0;
        int start = (path[0] == '\"') ? 1 : 0;

        /* find start of program name in path */
        for (i = start; i < strlen(path) - 1; i++) {
                if (path[i] == '/') {
                        last_slash_pos = i;
                }

                if (start && path[i] == '\"') {
                        /* end of file path */
                        break;
                } else if (!start && path[i] == ' ' && memcmp(&path[i-1], "\\ ", 2)) {
                        /* space in file path */
                        break;
                }
        }

        /* copy name from path */
        name_length = i - (last_slash_pos + 1);
        memcpy(name_buf, &path[last_slash_pos + 1], name_length);
        name_buf[name_length] = '\0';
#endif
}

/* create temporary file name */
static int get_tmp_file_name(char *name)
{
#ifdef WIN32
        char path[MAX_PATH];

        if (!GetTempPath(MAX_PATH, path) || !GetTempFileName(path, "", 0, name)) {
                return ERR_FILE_OPEN;
        }

        return 0;
#else
        /* The last six characters must be XXXXXX and will be replaced with a string
         * that makes the filename unique.
         */
        char template[] = "/tmp/cli_programmer_XXXXXX";
        memcpy(name, template, sizeof(template));
        return (mkstemp(name) ? 0 : ERR_FILE_OPEN);
#endif
}

#ifdef WIN32
static bool check_gdb_server_port(int pid, int port)
{
        FILE *fp;
        char buf[50];
        bool data_started = false;
        int cnt = 0;
        int netstat_port = -1;
        int netstat_pid = -1;

        fp = _popen("netstat -nao", "r");

        while (fscanf(fp, "%s", buf) == 1) {
                if (!data_started) {
                        if (!strcmp(buf, "PID")) {
                                data_started = true;
                        }

                        continue;
                }

                switch (cnt) {
                case 1:
                        /* local address - get port */
                        netstat_port = atoi(strchr(buf, ':') + 1);
                        break;
                case 2:
                        /*
                         * The '*:*' value of foreign address is appearing in case of UDP protocol.
                         * In this protocol the state value doesn't exist - state column should be
                         * skipped.
                         */
                        if (!strcmp(buf, "*:*")) {
                                ++cnt;
                        }
                        break;
                case 4:
                        /* pid */
                        netstat_pid = atoi(buf);

                        if (netstat_port == port && netstat_pid == pid) {
                                _pclose(fp);
                                return true;
                        }
                        break;
                }

                cnt = (cnt + 1) % 5;
        }

        _pclose(fp);
        return false;
}
#endif

static int get_gdb_server_pid(const char *gdb_cmdline, int port)
{
#ifndef WIN32
        char cmd[100];  /* netstat command buffer */
        char gdb_name[300]; /* expected gdbserver name taken from gdb_cmdline */
        char *proc_name;
        int pid = -1;
        int ret;
        FILE *fp;
        time_ms_t time_start_ms;
        time_ms_t time_check_ms;

        get_name_from_path(gdb_cmdline, gdb_name);

        time_start_ms = gdb_server_get_current_time_ms();

        do {
                /*
                 * Use netstat to find process listening on given port. The value is returned as
                 * PID/Name pair, however it is possible that the name will be stripped if output
                 * is too wide. For this reason we only get PID here.
                 */
                snprintf(cmd, sizeof(cmd), "netstat -lpnt4 2>/dev/null | awk '/:%d / { print $7 }'",
                                                                                        port);
                fp = popen(cmd, "r");
                if (!fp) {
                        return -1;
                }
                ret = fscanf(fp, "%d/", &pid);
                pclose(fp);

                if (ret >= 1 && pid > 0) {
                        goto pid_obtained;
                }

                time_check_ms = gdb_server_get_current_time_ms();
        } while ((time_check_ms - time_start_ms) <= GDB_RECONNECT_MAX_TIME_MS);

        return -1;

pid_obtained:
        /* Now we use ps to retrieve full process name for given pid. */
        snprintf(cmd, sizeof(cmd), "ps -p %d -o comm=", pid);
        fp = popen(cmd, "r");
        if (!fp) {
                return -1;
        }
        ret = fscanf(fp, "%ms", &proc_name);
        pclose(fp);

        if (ret < 1 || strcmp(gdb_name, proc_name)) {
                free(proc_name);
                return -1;
        }

        free(proc_name);

        return pid;
#else
        HANDLE snap_shot;
        PROCESSENTRY32 proc_entry;
        char gdb_server_cmd[MAX_PATH];
        int pid = -1;

        get_name_from_path(gdb_cmdline, gdb_server_cmd);

        proc_entry.dwSize = sizeof(PROCESSENTRY32);
        snap_shot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if ((snap_shot !=  INVALID_HANDLE_VALUE) && Process32First(snap_shot, &proc_entry)) {
                do {
                        if (_stricmp(gdb_server_cmd, proc_entry.szExeFile) == 0) {
                                pid = proc_entry.th32ProcessID;

                                if (!check_gdb_server_port(pid, port)) {
                                     pid = -1;
                                } else {
                                        break;
                                }
                        }

                } while (Process32Next(snap_shot, &proc_entry));
        }

        if (snap_shot !=  INVALID_HANDLE_VALUE) {
                CloseHandle(snap_shot);
        }

        return pid;
#endif
}

/* stop all GDB Server instances - specified by name in path to new GDB Server */
static void stop_gdb_server_instances(const char *new_path, int port)
{
        char pkill_cmd[300];
        int ret = 0;
#ifdef WIN32
        strcpy(pkill_cmd, "%WINDIR%\\system32\\TASKKILL /F /IM >nul 2>nul ");
        get_name_from_path(new_path, &pkill_cmd[strlen(pkill_cmd)]);
        /* kill all processes based on GDB Server name */
        ret = system(pkill_cmd);
#else
        int pid = get_gdb_server_pid(new_path, port);
        if (pid > 0) {
                sprintf(pkill_cmd, "kill %d", pid);
                ret = system(pkill_cmd);
        }
#endif
        (void) ret;
}

/* check that there is at least one GDB Server instance running */
static bool is_running_gdb_server(const char *new_path, int port)
{
        return get_gdb_server_pid(new_path, port) > 0;
}
/*
 * Before starting gdb server that is expected to open specific port, make sure
 * that this port can be used without problem.
 * When gdb server process is killed, socket that was used for communication with clients
 * can be in temporary state that prevents next instance of gdb server to use this
 * socket. This function tries to bind to gdb server socket for some time, if
 * it can be accomplished socket is closed and gdb server instance will not have
 * problems opening it.
 */
static int verify_local_socket_can_bind(uint16_t port, int timeout_ms)
{
        struct sockaddr_in addr;
        int err = 0;
        time_ms_t time_start_ms;
        time_ms_t time_check_ms;

        int sock = socket(PF_INET, SOCK_STREAM, 0);
        if (sock < 0) {
                return ERR_GDB_SERVER_SOCKET;
        }
        addr.sin_family = PF_INET;
        addr.sin_port = htons(port);
        addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

        time_start_ms = gdb_server_get_current_time_ms();

        /* Try to bind socket to specified port for some time */
        do {
                err = bind(sock, (struct sockaddr *) &addr, sizeof(addr));
                if (err) {
                        err = socket_error();
                }
                time_check_ms = gdb_server_get_current_time_ms();
        } while (err == EADDRINUSE && (time_check_ms - time_start_ms) <= timeout_ms);

        closesocket(sock);
        if (err) {
                err = ERR_GDB_SERVER_SOCKET;
        }

        return err;
}

#ifdef WIN32
/* Callback passed to EnumWindows which will close any window which is owned by given process */
BOOL CALLBACK terminate_app_cb(HWND hwnd, LPARAM lparam)
{
        DWORD pid;

        GetWindowThreadProcessId(hwnd, &pid);

        if (pid == (DWORD) lparam) {
                PostMessage(hwnd, WM_CLOSE, 0, 0);
        }

    return TRUE;
 }
#endif

/* run specified system command in different process */
static void run_command(const char *cmd)
{
#ifdef WIN32
        STARTUPINFOA si = {0};
        PROCESS_INFORMATION pi;
        SECURITY_ATTRIBUTES sa;
        char cmd_line[32768];
        char log_file[MAX_PATH];
        strcpy(cmd_line, cmd);

        /*
         * Standard output will be redirected to file, for this security attributes must have
         * inheritable flag.
         */
        sa.nLength = sizeof(sa);
        sa.lpSecurityDescriptor = NULL;
        sa.bInheritHandle = TRUE;

        /*
         * Try to open gdb server log file in current folder, if not possible try temp folder
         */
        si.hStdOutput = CreateFile("cli_gdb_server.log", GENERIC_READ | GENERIC_WRITE,
                                FILE_SHARE_READ | FILE_SHARE_WRITE, &sa, OPEN_ALWAYS, 0, 0);
        if (si.hStdOutput == INVALID_HANDLE_VALUE)
        {
                GetTempPath(sizeof(log_file) / sizeof(log_file[0]), log_file);
                PathAppend(log_file, "cli_gdb_server.log");
                si.hStdOutput = CreateFile(log_file, GENERIC_READ | GENERIC_WRITE,
                                FILE_SHARE_READ | FILE_SHARE_WRITE, &sa, OPEN_ALWAYS, 0, 0);
        }
        si.hStdError = si.hStdOutput;
        si.hStdInput = (HANDLE) STD_INPUT_HANDLE; /* Both handles to one file */

        si.cb = sizeof(si);
        si.dwFlags = STARTF_USESTDHANDLES;
        if (CreateProcessA(NULL, cmd_line, NULL, NULL, TRUE, 0, NULL, NULL, &si, &pi)) {
                CloseHandle(pi.hThread);
                gdb_server_pid = pi.dwProcessId;
                gdb_server_handle = pi.hProcess;
        }
        if (si.hStdOutput != INVALID_HANDLE_VALUE) {
                CloseHandle(si.hStdOutput);
        }
#else
        pid_t pid = fork();

        /* child process */
        if (pid == 0) {
                int fd;
                char *exec_cmd;

                /* Open log file and redirect (append) stdout and stderr there */
                fd = open("cli_gdb_server.log", O_APPEND | O_CREAT | O_WRONLY, 0666);
                dup2(fd, STDOUT_FILENO);
                dup2(fd, STDERR_FILENO);
                close(fd);

                /*
                 * Launching GDB server via execlp() in a safe manner would require to parse 'cmd'
                 * into separate arguments which is tricky. To make things easier we skip this and
                 * launch 'exec <cmd>' command in a shell. The result is more or less the same as
                 * using system() call but since shell process replaces current one and 'exec <cmd>'
                 * replaces shell process, 'pid' will be actual pid of process running GDB server
                 * and not pid of shell or its parent process.
                 */
                exec_cmd = alloca(5 + strlen(cmd) + 1);
                strcpy(exec_cmd, "exec ");
                strcat(exec_cmd, cmd);
                execlp("sh", "sh", "-c", exec_cmd, NULL);

                /* No more code will be executed here */
        } else if (pid == -1) {
                prog_print_err("Cannot fork GDB Server \n");
                return;
        }
        /* Save GDB Server process PID */
        gdb_server_pid = pid;
#endif
}

/* create socket and connect to GDB Server specified by host_name and port */
static int gdb_server_init_socket(uint16_t port, const char *host_name)
{
        struct sockaddr_in addr;
        time_ms_t time_start_ms;
        time_ms_t time_check_ms;
        const int nodelay = 1;

        if ((gdb_server_sock = socket(PF_INET, SOCK_STREAM, 0)) == -1) {
                return ERR_GDB_SERVER_SOCKET;
        }

        memset(&addr, 0, sizeof(struct sockaddr_in));
        addr.sin_family = PF_INET;

        /* try resolve host_name as address */
        if ((addr.sin_addr.s_addr = inet_addr(host_name)) == INADDR_NONE) {
                /* get address from host_name*/
                struct hostent *host = gethostbyname(host_name);

                /* cannot find host_name */
                if (!host) {
                        closesocket(gdb_server_sock);
                        return ERR_GDB_SERVER_SOCKET;
                }

                addr.sin_addr.s_addr = *(uint32_t *) host->h_addr_list[0];
        }

        addr.sin_port = htons(port);

        time_start_ms = gdb_server_get_current_time_ms();

        /* Setting TCP_NODELAY option increases flashing speed on Linux */
        setsockopt(gdb_server_sock, IPPROTO_TCP, TCP_NODELAY, (void *) &nodelay, sizeof(nodelay));

        /* try connect to created socket */
        do {
                if (connect(gdb_server_sock, (struct sockaddr *) &addr, sizeof(struct sockaddr_in))
                                                                                        == 0) {
                        goto done;
                }

                time_check_ms = gdb_server_get_current_time_ms();
        } while ((time_check_ms - time_start_ms) <= GDB_RECONNECT_MAX_TIME_MS);

        closesocket(gdb_server_sock);
        return ERR_GDB_SERVER_SOCKET;

done:
        return 0;
}

/* check that checksum of data in gdb_server_recv_buf.buf is correct */
static bool gdb_sever_check_checksum(void)
{
        bool status = false;
        uint8_t from_frame = checksum((char *) gdb_server_recv_buf.buf + 1, gdb_server_recv_buf.len
                                                                                        - 4);
        uint8_t correct = chars_to_uint8(gdb_server_recv_buf.buf[gdb_server_recv_buf.len - 2],
                                gdb_server_recv_buf.buf[gdb_server_recv_buf.len - 1], &status);

        return (from_frame == correct);
}

/* check that received frame contains '$', '#' characters and checksum */
static bool gdb_server_check_frame(void)
{
        uint32_t i;
        /* $ character is start of the frame */
        bool dollar_found = false;
        /* # character is end of the data in frame */
        bool hash_found = false;
        uint32_t hash_pos = 0;

        for (i = 0; i < gdb_server_recv_buf.len; i++) {
                if (gdb_server_recv_buf.buf[i] == '$' ) {
                        dollar_found = true;
                } else if (gdb_server_recv_buf.buf[i] == '#') {
                        hash_pos = i;
                        hash_found = true;
                }

                /* response contains start frame and end data characters */
                if (dollar_found && hash_found) {
                        /* check that response contains checksum */
                        return ((hash_pos + 2 <= gdb_server_recv_buf.len));
                }
        }

        return false;
}

/* send data to GDB Server socket */
static int gdb_server_send(const char *buf, uint32_t buf_len)
{
        int i;
#if DBG_GDB_SERVER
        printf("<-- ");

        for (i = 0; i < (int) buf_len; i++) {
                printf("%c", buf[i]);
        }

        printf("\n");
#endif
        while (buf_len > 0) {
                i = send(gdb_server_sock, buf, buf_len, 0);

                if (i < 0) {
                        return ERR_GDB_SERVER_SOCKET;
                }

                buf_len -= i;
                buf += i;
        }

        return 0;
}

/* send acknowledgement to GDB Server socket */
static inline int gdb_server_ack(void)
{
        return gdb_server_send("+", 1);
}

/* send not acknowledgement to GDB Server socket */
static inline int gdb_server_nack(void)
{
        return gdb_server_send("-", 1);
}

/* receive data from GDB Server, check frame and send acknowledgement */
static int gdb_server_recv_with_ack(void)
{
        uint8_t repeats_cnt = 0;
        int status;
#if DBG_GDB_SERVER
        int i;
#endif
start:
        gdb_server_recv_buf.len = 0;

        /* receive until data is incomplete */
        do {
                gdb_server_recv_buf.len += recv(gdb_server_sock, (char *) gdb_server_recv_buf.buf +
                                gdb_server_recv_buf.len, MAX_BUF_LEN - gdb_server_recv_buf.len, 0);

#if DBG_GDB_SERVER
                printf("--> ");

                for (i = 0; i < (int) gdb_server_recv_buf.len; i++) {
                        printf("%c", gdb_server_recv_buf.buf[i]);
                }

                printf("\n");
#endif
        } while (!gdb_server_check_frame());

        if (!gdb_sever_check_checksum()) {
                /* checksum of received data is incorrect */
                if (repeats_cnt >= GDB_SERVER_REPEATS_LIMIT) {
                        /* exceeded repeats limit */
                        return ERR_GDB_SERVER_CRC_MISMATCH;
                }

                if ((status = gdb_server_nack()) != 0) {
                        return status;
                }

                ++repeats_cnt;
                goto start;
        }

        return gdb_server_ack();
}

/*
 * wait for acknowledgement (ack_nack set to true) or not acknowledgement (ack_nack set to false)
 * from GDB Server
 */
static inline int gdb_server_wait_for_ack(bool *ack_nack)
{
        uint8_t tmp_buf[1];
        long int tmp_buf_len;

        while (true) {
                if ((tmp_buf_len = recv(gdb_server_sock, (char *) tmp_buf, 1, 0)) < 0) {
                        return ERR_GDB_SERVER_SOCKET;
                }

                if (tmp_buf_len >= 1 && tmp_buf[0] == ACK_CHAR) {
                        *ack_nack = true;
                        return 0;
                } else if (tmp_buf_len >= 1 && tmp_buf[0] == NACK_CHAR) {
                        *ack_nack = false;
                        return 0;
                }
        }
}

/*
 * send data to GDB Server and wait for acknowledgement, if NACK received more than
 * GDB_SERVER_REPEATS_LIMIT return error else receive data to gdb_server_recv_buf.buf and send
 * acknowledgement
 */
static int gdb_server_send_recv_ack(const char *buf, uint32_t buf_len)
{
        uint8_t repeats_cnt = 0;
        int status;
        bool ack_nack;

        while (repeats_cnt < GDB_SERVER_REPEATS_LIMIT) {
                if ((status = gdb_server_send(buf, buf_len)) != 0) {
                       return status;
                }

                ++repeats_cnt;

                if ((status = gdb_server_wait_for_ack(&ack_nack)) != 0) {
                       return status;
                }

                if (ack_nack) {
                        return gdb_server_recv_with_ack();
                }
        }

        return ERR_GDB_SERVER_CMD_REJECTED;
}

/* send read command to GDB Server, command syntax typical for GDB */
static int gdb_server_send_read_cmd(uint32_t addr, uint32_t len)
{
        /*
         * length calculation: address (8 bytes), length (8 bytes), checksum (2 bytes), frame
         * characters (4 bytes) and NULL terminating (1 byte)
         */
        char cmd[8 + 8 + 2 + 4 + 1];
        uint32_t cmd_len;

        /* frame example: $m00000000,00000002#FF */
        sprintf(cmd, "$m%08X,%08X", addr, len);
        cmd_len = strlen(cmd);
        sprintf(&cmd[cmd_len], "#%02X", checksum(cmd + 1, cmd_len - 1));

        return gdb_server_send_recv_ack(cmd, strlen(cmd));
}

/* send write command to GDB Server, command syntax typical for GDB */
static int gdb_server_send_write_cmd(uint32_t addr, uint32_t data_len, const uint8_t *data)
{
        uint32_t tmp_len;
        uint32_t i;
        char *cmd;
        int ret;

        /*
         * length calculation: address (up to 8 bytes), data length (up to 8 bytes), checksum
         * (2 bytes), frame characters (5 bytes), data (up to data_len * 2 bytes) and NULL
         * terminating (1 byte)
         */
        cmd = malloc(data_len * 2 + 8 + 8 + 2 + 5 + 1);

        if (!cmd) {
                return ERR_ALLOC_FAILED;
        }

        /*
         * frame example: $m10,2:01234#FF, data are not a characters - binary data with some
         * characters escaping
         */
        sprintf(cmd, "$X%x,%x:", addr, data_len);
        tmp_len = strlen(cmd);

        for (i = 0; i < data_len; i++) {
                /* escape special characters */
                if (data[i] == '#' || data[i] == '$' || data[i] == '}') {
                        cmd[tmp_len++] = '}';
                        cmd[tmp_len++] = data[i] - 0x20;
                } else {
                        cmd[tmp_len++] = data[i];
                }
        }

        sprintf(&cmd[tmp_len], "#%02X", checksum(cmd + 1, tmp_len - 1));

        ret = gdb_server_send_recv_ack(cmd, tmp_len + 3);
        free(cmd);

        return ret;
}

/* create loadbin request with specified file path, after using returned pointer must be freed */
static char *gdb_server_create_loadbin_req(const char *file_path, uint32_t addr)
{
        char *req;

        /*
         * length calculation: file path (file path length bytes), loadbin command (7 bytes),
         * address (8 bytes), checksum (2 bytes), request frame characters (5 bytes) and NULL
         * terminating (1 byte)
         */
        req = malloc(strlen(file_path) + 7 + 8 + 5 + 2 + 1);

        if (!req) {
                return NULL;
        }

        /* request example: loadbin /tmp/AbCdfile.bin, 0x00000000 */
        sprintf(req, "%s %s, 0x%08X", "loadbin", file_path, addr);

        return req;
}

/*
 * send local command to GDB Server, command syntax typical for GDB, commands may be different
 * depending of the server application
 */
static int gdb_server_send_local_cmd(const char *req)
{
        uint32_t len;
        uint32_t i;
        char *cmd;
        int ret;

        /*
         * length calculation: execute local command (5 bytes), request (2 * request length bytes),
         * checksum (2 bytes), frame characters (3 bytes), and NULL terminating (1 byte)
         */
        cmd = malloc(strlen(req) * 2 + 5 + 2 + 3 + 1);

        if (!cmd) {
                return ERR_ALLOC_FAILED;
        }

        /*
         * frame example: $qRcmd,012345678#FF where 0123.. is encoded request - 2 characters for
         * each byte of request
         */
        sprintf(cmd,"$%s,", GDB_LOCAL_CMD_EXE);
        len = strlen(cmd);

        for (i = 0; i < strlen(req); i++) {
                sprintf(&cmd[len], "%02X", req[i]);
                len += 2;
        }

        strcat(cmd + len, "#");
        ++len;
        sprintf(cmd + len, "%02X", checksum(cmd + 1, len - 2));

        ret = gdb_server_send_recv_ack(cmd, strlen(cmd));
        free(cmd);

        return ret;
}

/* send loadbin command to GDB Server */
static int gdb_server_send_loadbin_cmd(const char *path, uint32_t addr)
{
        char *req;
        int ret;

        req = gdb_server_create_loadbin_req(path, addr);

        if (!req) {
                return ERR_ALLOC_FAILED;
        }

        ret = gdb_server_send_local_cmd(req);
        free(req);

        return ret;
}

/* set swd_run field on true - this allows swd_loop execution in uartboot */
static int gdb_server_set_run_swd(void)
{
        uint8_t arr[] = {true};

        return gdb_server_send_write_cmd(swd_addr.run_swd_addr, 1, arr);
}

/* increase command number field - this allows new command execution by uartboot */
static int gdb_server_inc_cmd_num(void)
{
        ++cmd_num_cp;

        return gdb_server_send_write_cmd(swd_addr.cmd_num_addr, 4, (uint8_t *) &cmd_num_cp);
}

/*
 * send step and continue commands to GDB Server - after continue command only program cannot skip
 * breakpoint
 */
static int gdb_server_send_continue(void)
{
        int status;

        if ((status = gdb_server_send_recv_ack(GDB_STEP, strlen(GDB_STEP))) != 0) {
                return status;
        }

        return gdb_server_send_recv_ack(GDB_CONTINUE, strlen(GDB_CONTINUE));
}

/*
 * create array of uint8_t from characters buffer, e.g: ABCDEF -> {0xAB, 0xCD, 0xEF}, if conversion
 * cannot be done return false otherwise return true
 */
static bool gdb_server_frame_to_uint8_buf(uint8_t *buf, uint32_t len)
{
        uint32_t i;
        uint32_t start_data = 0;
        bool conversion_status = false;

        /* find start of the data - '$' character */
        for (i = 0; i < gdb_server_recv_buf.len; i++) {
                if (gdb_server_recv_buf.buf[i] == '$') {
                        start_data = i + 1;
                        break;
                }
        }

        /* convert characters to uint8_t values, 2 characters for each value */
        for (i = 0; i < len; i++) {
                buf[i] = chars_to_uint8(gdb_server_recv_buf.buf[start_data + i * 2],
                        gdb_server_recv_buf.buf[start_data + i * 2 + 1], &conversion_status);

                if (!conversion_status) {
                      /* cannot convert characters to uint8_t */
                     return false;
                }
        }

        /* conversion done without problems */
        return true;
}

static int gdb_server_reset_device()
{
        int status;
        uint32_t tmp_32;

        /* remove all breakpoints */
        if ((status = gdb_server_send_local_cmd("clrbp")) != 0) {
                return status;
        }

        /* hardware platform reset */
        if ((status = gdb_server_send_local_cmd("reset 0")) != 0) {
                return status;
        }

        /* Wait for reset */
        if ((status = gdb_server_send_local_cmd("sleep 10")) != 0) {
                return status;
        }

        /* stop program execution on platform */
        if ((status = gdb_server_send_local_cmd("halt")) != 0) {
                return status;
        }

        /* write MAGIC VALUE */
        status  = gdb_server_send_local_cmd("memU32 0x7fd0000 = 0xdeadbeef");
        status |= gdb_server_send_local_cmd("memU32 0x7fd0004 = 0xdeadbeef");
        status |= gdb_server_send_local_cmd("memU32 0x7fd0008 = 0xdeadbeef");
        status |= gdb_server_send_local_cmd("memU32 0x7fd000c = 0xdead10cc");
        if (status  != 0) {
                return status;
        }

        /* set SWD_HW_RESET_REQ bit in SWD_RESET_REG */
        tmp_32 = 0x00000001;
        /* verification of this writing could fail - not readable register */
        if ((status = gdb_server_send_write_cmd(0x400C3050, 4, (uint8_t *)&tmp_32)) != 0) {
                return status;
        }

        /* wait after platform reset */
        if ((status = gdb_server_send_local_cmd("sleep 100")) != 0) {
                return status;
        }
        sleep(1);

        if ((status = gdb_server_send_local_cmd("reset 0")) != 0) {
                return status;
        }

        /* Wait for reset */
        if ((status = gdb_server_send_local_cmd("sleep 1")) != 0) {
                return status;
        }

        /* stop program execution on platform */
        return gdb_server_send_local_cmd("halt");
}

/*
 * perform all necessary action to properly connect to GDB Server and start the platform
 * loading uartboot code must be in other function - when initialization function is called
 * the local copy of uartboot code is not created
 */
static int gdb_server_init(const prog_gdb_server_config_t *gdb_server_conf)
{
        int status = 0;
        bool start_gdb = false;
        bool local_rst = false;
        bool stop_gdb_server;

        stop_gdb_server = (gdb_server_conf->no_kill_gdb_server == NO_KILL_MODE_NONE ||
                                gdb_server_conf->no_kill_gdb_server == NO_KILL_MODE_DISCONNECT);

        /* try to stop previous instances of GDB Server */
        if (stop_gdb_server && gdb_server_conf->gdb_server_path &&
                                                        is_localhost(gdb_server_conf->host_name)) {
                stop_gdb_server_instances(gdb_server_conf->gdb_server_path, gdb_server_conf->port);

                start_gdb = true;
        } else if (is_localhost(gdb_server_conf->host_name) && gdb_server_conf->gdb_server_path &&
                        !is_running_gdb_server(gdb_server_conf->gdb_server_path, gdb_server_conf->port)) {
                start_gdb = true;
        }

        if (start_gdb) {
                time_ms_t time_start_ms;
                time_ms_t time_check_ms;

                /*
                 * Before starting gdb server make sure that it can open specific port.
                 * If port can't be opened there is not point in starting gdb server.
                 */
                status = verify_local_socket_can_bind(gdb_server_conf->port, 5000);
                if (status) {
                        return status;
                }
                if (target_reset_cmd && is_localhost(gdb_server_conf->host_name) &&
                                                                        gdb_server_conf->reset) {
#ifdef WIN32
                        STARTUPINFO si = { .cb=sizeof(STARTUPINFO) };
                        PROCESS_INFORMATION pi;

                        if (CreateProcessA(NULL, target_reset_cmd, NULL, NULL, FALSE, 0, NULL, NULL,
                                                                                        &si, &pi)) {
                                DWORD ret_code;

                                WaitForSingleObject(pi.hProcess, INFINITE);
                                GetExitCodeProcess(pi.hProcess, &ret_code);
                                CloseHandle(pi.hProcess);

                                if (ret_code < 0) {
                                        return ret_code;
                                }

                                local_rst = true;
                        } else {
                                return GetLastError();
                        }
#else
                        status = system(target_reset_cmd);
                        if (status < 0) {
                                return status;
                        }
                        local_rst = true;
#endif
                }
                run_command(gdb_server_conf->gdb_server_path);

                time_start_ms = gdb_server_get_current_time_ms();

                /* check that GDB Server starts listening on given port */
                do {
                        if (get_gdb_server_pid(gdb_server_conf->gdb_server_path,
                                                                gdb_server_conf->port) > 0) {
                                goto gdb_server_started;
                        }

                        time_check_ms = gdb_server_get_current_time_ms();
                } while ((time_check_ms - time_start_ms) <= GDB_RECONNECT_MAX_TIME_MS);

                return ERR_FAILED;
        }

gdb_server_started:

        if (gdb_server_conf->connect_gdb_server) {
                status = gdb_server_connect(gdb_server_conf->host_name, gdb_server_conf->port,
                                                        (gdb_server_conf->reset && !local_rst));
                if (status < 0) {
                        return status;
                }

                if (local_rst) {
                        /* set SYS_CTRL_REG register */
                        uint16_t tmp_16 = 0x00AB;

                        return gdb_server_send_write_cmd(0x50000012, 2, (uint8_t *) &tmp_16);
                }
        }

        return status;
}

static int gdb_server_load_image(void)
{
        char tmp_name[500];
        int status;

        /*
         * these operations can not be performed in initialization function - without uartboot
         * code
         */
        if ((status = get_tmp_file_name(tmp_name)) != 0) {
                return status;
        }

        if ((status = memory_to_file(tmp_name, boot_loader_code, boot_loader_size)) != 0) {
                return status;
        }

        /* write boot loader code from file to platform */
        if ((status = gdb_server_send_loadbin_cmd(tmp_name, 0)) != 0) {
                return status;
        }

        /* hardware platform reset */
        if ((status = gdb_server_send_local_cmd("reset 0")) != 0) {
                return status;
        }

        /* hardware platform reset */
        if ((status = gdb_server_send_local_cmd("go")) != 0) {
                return status;
        }

        /* remove created temporary file */
        remove(tmp_name);

        uartboot_loaded = true;

        return 0;
}

static int gdb_server_load_uartboot(void)
{
        char tmp_name[500];
        int status;

        /*
         * these operations can not be performed in initialization function - without uartboot
         * code
         */
        if ((status = get_tmp_file_name(tmp_name)) != 0) {
                return status;
        }

        if ((status = memory_to_file(tmp_name, boot_loader_code, boot_loader_size)) != 0) {
                return status;
        }

        /* write boot loader code from file to platform */
        if ((status = gdb_server_send_loadbin_cmd(tmp_name, 0)) != 0) {
                return status;
        }

        /* hardware platform reset */
        if ((status = gdb_server_send_local_cmd("reset 0")) != 0) {
                return status;
        }

        /* stop program execution on platform */
        if ((status = gdb_server_send_local_cmd("halt")) != 0) {
                return status;
        }

        /* set run_swd field in boot loader on the platform */
        if ((status = gdb_server_set_run_swd()) != 0) {
                return status;
        }

        /* continue program execution  */
        if ((status = gdb_server_send_continue()) != 0) {
                return status;
        }

        /* remove created temporary file */
        remove(tmp_name);

        uartboot_loaded = true;

        return 0;
}

/*
 * If bootloader is running this function initializes its command counter also. This function
 * returns true if uartboot is running on the platform and false otherwise.
 */
static bool gdb_server_cmd_dummy(void)
{
        uint8_t header_buf[2];
        uint8_t rsp_buf[4];
        int status;
        char tmp[] = UARTBOOT_LIVE_MARKER;

        /* Send dummy command and reset command counter in uartboot */
        header_buf[0] = SOH;
        header_buf[1] = CMD_DUMMY;

        cmd_num_cp = 0xFFFFFFFF;

        if ((status = gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf)) != 0) {
                return false;
        }

        /* receive data */
        if ((status = gdb_server_send_read_cmd(swd_addr.buf_addr, sizeof(rsp_buf))) != 0) {
                return false;
        }

        if (!gdb_server_frame_to_uint8_buf(rsp_buf, sizeof(rsp_buf))) {
             return false;
        }

        if (memcmp(rsp_buf, tmp, sizeof(rsp_buf))) {
                return false;
        }

        return true;
}

/* If bootloader is running this function initializes its command counter also */
static bool gdb_server_uartboot_is_running()
{
        char swd_info_buf[5] = { 0 };
        int status;

        status = gdb_server_send_read_cmd(swd_addr.run_swd_addr - 4, sizeof(swd_info_buf));

        if (status) {
                return false;
        }

        if (!gdb_server_frame_to_uint8_buf((uint8_t *) swd_info_buf, sizeof(swd_info_buf))) {
                return false;
        }

        if (!swd_info_buf[4]) {
                /* SWD loop is not enable or binaries are different */
                return false;
        }

        if (memcmp(swd_info_buf, marker, 4)) {
                /* Marker was not found at proper address */
                return false;
        }

        return gdb_server_cmd_dummy();
}

/* check is the gdb server socket was opened before, if not open it and initialize GDB Server */
static int gdb_server_verify_connection(void)
{
        int status;

        /* initial procedure was done earlier */
        if (gdb_server_sock < 0) {
                /*
                 * standard initialization debugger procedure:
                 * - initialize GDB Server socket
                 * - reset and halt device few time
                 * - write registers values
                 * - start swd loop in uartboot
                 */
                if ((status = gdb_server_init(&configuration)) != 0) {
                        return status;
                }
        } else if (uartboot_loaded) {
                return 0;
        }

        if (!configuration.check_bootloader) {
                /* Reset should be done earlier - load bootloader binary */
                return gdb_server_load_uartboot();
        }

        if (gdb_server_uartboot_is_running()) {
                /* uartboot is running on the platform */
                uartboot_loaded = true;
                return 0;
        }

        /* uartboot is not running - do platform reset and load it */
        if (!configuration.reset) {
                /* Initialization wasn't done earlier */
                uint16_t tmp_16;

                if ((status = gdb_server_reset_device()) != 0) {
                        return status;
                }

                /* set SYS_CTRL_REG register */
                tmp_16 = 0x00AB;

                if ((status = gdb_server_send_write_cmd(0x50000012, 2, (uint8_t *) &tmp_16)) != 0) {
                        return status;
                }
        }

        return gdb_server_load_uartboot();
}

/*
 *  write command header to command buffer in uartboot, increase command number and continue
 *  execution swd loop in uartboot
 */
static int gdb_server_send_swd_cmd_header(uint32_t data_len, const uint8_t *data)
{
        int status;

        if ((status = gdb_server_send_write_cmd(swd_addr.cmd_buf_addr, data_len, data)) != 0) {
                return status;
        }

        if ((status = gdb_server_inc_cmd_num()) != 0) {
                return status;
        }

        return gdb_server_send_continue();
}

static void gdb_server_stop(int pid)
{
        if (pid == INVALID_PID) {
                pid = gdb_server_pid;
        }

        if (pid < 0) {
                return;
        }

#ifndef WIN32
        pid_t tmp_pid;
        time_ms_t time_start_ms;
        time_ms_t time_check_ms;

        /* Terminate GDB server gracefully */
        kill(pid, SIGTERM);

        time_start_ms = gdb_server_get_current_time_ms();

        /* wait until GDB Server is running or timeout is not reached */
        do {
                /* GDB Server exited */
                if ((tmp_pid = waitpid(pid, NULL, WNOHANG)) != 0) {
                        return;
                }

                time_check_ms = gdb_server_get_current_time_ms();
        } while ((time_check_ms - time_start_ms) <= GDB_SERVER_CLOSE_MAX_TIME_MS);

        /* If GDB server process is still running, just force kill it with SIGKILL */
        kill(pid, SIGKILL);
        waitpid(pid, NULL, 0);

#else
        /* Try to stop JLinkGDBServer gracefully */
        if (pid) {
                EnumWindows(terminate_app_cb, (LPARAM) pid);
        }

        /* GDB server was started by CLI wait for graceful end first, then kill */
        if (gdb_server_handle != INVALID_HANDLE_VALUE) {
                if (WaitForSingleObject(gdb_server_handle, GDB_SERVER_CLOSE_MAX_TIME_MS)
                                                                                != WAIT_OBJECT_0) {
                        char kill_cmd[MAX_PATH];

                        sprintf(kill_cmd, "%%WINDIR%%\\system32\\TASKKILL /F /PID %d >nul 2>nul",
                                                                                        (int) pid);
                        system(kill_cmd);
                }
                CloseHandle(gdb_server_handle);
        }

        WSACleanup();
#endif
}

/*
 * read gdb frames, first the buffer len is detected and then the translated data
 * are copied into buf
 */
static int gdb_server_read_dynamic_length(uint8_t **buf, uint32_t *len)
{
        int ret = 0;
        uint16_t size;

        /* receive payload len */
        if ((ret = gdb_server_send_read_cmd(swd_addr.buf_addr, sizeof(uint16_t))) != 0) {
                goto done;
        }

        if (!gdb_server_frame_to_uint8_buf((uint8_t *) &size, sizeof(uint16_t))) {
                ret = ERR_FAILED;
                goto done;
        }

        *len = size;

        if ((*buf = malloc(*len)) == NULL) {
                ret = ERR_ALLOC_FAILED;
                goto done;
        }

        /* receive payload */
        if ((ret = gdb_server_send_read_cmd(swd_addr.buf_addr, size)) != 0) {
                goto done;
        }

        if (!gdb_server_frame_to_uint8_buf(*buf, size)) {
                ret = ERR_FAILED;
                goto done;
        }

done:
        return ret;
}

int gdb_server_initialization(const prog_gdb_server_config_t *gdb_server_conf)
{
#ifdef WIN32
        WSADATA wsaData;

        WSAStartup(MAKEWORD(2, 2), &wsaData);
#endif
        int status;

        /* close socket if opened */
        if (gdb_server_sock != -1) {
                closesocket(gdb_server_sock);
                gdb_server_sock = -1;
        }

        /* make local copy of configuration */
        memset(&configuration, 0 , sizeof(configuration));
        configuration.port = gdb_server_conf->port;
        configuration.no_kill_gdb_server = gdb_server_conf->no_kill_gdb_server;
        configuration.connect_gdb_server = gdb_server_conf->connect_gdb_server;
        configuration.reset = gdb_server_conf->reset;
        configuration.check_bootloader = gdb_server_conf->check_bootloader;

        /* GDB Server path could be empty */
        if (gdb_server_conf->gdb_server_path) {
                configuration.gdb_server_path = strdup(gdb_server_conf->gdb_server_path);
        } else {
                configuration.gdb_server_path = NULL;
        }

        configuration.host_name = strdup(gdb_server_conf->host_name);

        status = gdb_server_init(&configuration);

        if (status) {
                return status;
        }

        if (!configuration.gdb_server_path || !is_localhost(configuration.host_name)) {
                return INVALID_PID;
        }

        return get_gdb_server_pid(configuration.gdb_server_path, configuration.port);
}

int gdb_server_connect(const char *host_name, int port, bool reset)
{
        int status;

        /* close socket if open */
        if (gdb_server_sock != -1) {
                closesocket(gdb_server_sock);
                gdb_server_sock = -1;
        }

        /* open socket to GDB Server */
        if ((status = gdb_server_init_socket(port, host_name)) != 0) {
                prog_print_err("Failed to bind to socket \n");
                return status;
        }

        if (reset) {
                /* set SYS_CTRL_REG register */
                uint16_t tmp_16 = 0x00AB;

                status = gdb_server_reset_device();

                if (status) {
                        return status;
                }

                return gdb_server_send_write_cmd(0x50000012, 2, (uint8_t *) &tmp_16);
        }

        return 0;
}

void gdb_server_set_boot_loader_code(uint8_t *code, size_t size)
{
        boot_loader_code = code;
        boot_loader_size = size;

        /* set initial values */
        set_swd_addresses();
        cmd_num_cp = 0;
}

void gdb_server_get_boot_loader_code(uint8_t **code, size_t *size)
{
        *code = boot_loader_code;
        *size = boot_loader_size;
}

/* write to RAM could be direct - without using uartboot command */
int gdb_server_cmd_write(const uint8_t *buf, size_t size, uint32_t addr)
{
        int status = 0;
        size_t part_size;

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /*
         * if address is equal ADDRESS_TMP then buffer should be write to temporary buffer on the
         * platform - to address specified by swd_addr.buf_addr
         */
        addr = ((addr == ADDRESS_TMP) ? swd_addr.buf_addr : addr);

        for (part_size = 0; part_size < size;) {
                size_t write_size = ((CHUNK_SIZE > (size - part_size)) ? (size - part_size) :
                                                                                        CHUNK_SIZE);

                status = gdb_server_send_write_cmd(addr + part_size, write_size, buf + part_size);

                if (status) {
                        return status;
                }

                part_size += write_size;
        }

        return status;
}

/* read from RAM could be direct - without bootloader */
int gdb_server_cmd_direct_read(uint8_t *buf, size_t size, uint32_t addr)
{
        int status = 0;
        size_t chunk;
        size_t offset = 0;

        /*
         * buffer for reading response from gdb server is limited to 64K.
         * If user requested more data split it to several gdb server requests.
         */
        while (size > 0 && status == 0) {
                chunk = MAX_READ_SIZE < size ? MAX_READ_SIZE : size;
                if ((status = gdb_server_send_read_cmd(addr + offset, chunk)) != 0) {
                        return status;
                }
                if (!(gdb_server_frame_to_uint8_buf(buf + offset, chunk))) {
                        status = ERR_GDB_SERVER_INVALID_RESPONSE;
                } else {
                        size -= chunk;
                        offset += chunk;
                }
        }
        return status;
}

/* read from RAM could be direct - without using uartboot command */
int gdb_server_cmd_read(uint8_t *buf, size_t size, uint32_t addr)
{
        int status;

        if ((status = gdb_server_verify_connection()) != 0) {
                return status;
        }

        return gdb_server_cmd_direct_read(buf, size, addr);
}

/*
 * Some commands will return NAK, this can happen if arguments were wrong or execution is not
 * possible. For example writing to already written OTP address will result in NAK.
 */
static int gdb_server_read_ack(void)
{
        int status;
        uint8_t ack_nak;

        /* read ACK or NAK left by command execution in swd area */
        if ((status = gdb_server_send_read_cmd(swd_addr.ack_nak_addr, 1)) != 0) {
                return status;
        }

        /* Decode ACK or NAK from GDB one byte read */
        if (!gdb_server_frame_to_uint8_buf(&ack_nak, 1)) {
                return ERR_GDB_SERVER_INVALID_RESPONSE;
        }

        return (ack_nak == NAK) ? ERR_PROT_COMMAND_ERROR : 0;
}

int gdb_server_cmd_copy_to_qspi(uint32_t src_address, size_t size, uint32_t dst_address)
{
        uint8_t header_buf[14];
        int status;

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_COPY_QSPI;
        header_buf[2] = (uint8_t) 10;
        header_buf[3] = (uint8_t) (10 >> 8);

        /*
         * if src_address is equal ADDRESS_TMP then buffer should be write to temporary buffer on
         * the platform - to address specified by swd_addr.buf_addr
         */
        src_address = ((src_address == ADDRESS_TMP) ? swd_addr.buf_addr : src_address);

        header_buf[4] = (uint8_t) (src_address);
        header_buf[5] = (uint8_t) (src_address >> 8);
        header_buf[6] = (uint8_t) (src_address >> 16);
        header_buf[7] = (uint8_t) (src_address >> 24);

        header_buf[8] = (uint8_t) size;
        header_buf[9] = (uint8_t) (size >> 8);

        header_buf[10] = (uint8_t) (dst_address);
        header_buf[11] = (uint8_t) (dst_address >> 8);
        header_buf[12] = (uint8_t) (dst_address >> 16);
        header_buf[13] = (uint8_t) (dst_address >> 24);

        /* send header */
        if ((status = gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf)) != 0) {
                return status;
        }

        /* wait for ACK */
        return gdb_server_read_ack();
}

int gdb_server_cmd_erase_qspi(uint32_t address, size_t size)
{
        uint8_t header_buf[12];

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_ERASE_QSPI;
        header_buf[2] = (uint8_t) 8;
        header_buf[3] = (uint8_t) (8 >> 8);

        header_buf[4] = (uint8_t) (address);
        header_buf[5] = (uint8_t) (address >> 8);
        header_buf[6] = (uint8_t) (address >> 16);
        header_buf[7] = (uint8_t) (address >> 24);
        header_buf[8] = (uint8_t) (size);
        header_buf[9] = (uint8_t) (size >> 8);
        header_buf[10] = (uint8_t) (size >> 16);
        header_buf[11] = (uint8_t) (size >> 24);

        /* send header */
        return gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf);
}

int gdb_server_cmd_chip_erase_qspi(void)
{
        uint8_t header_buf[2];

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_CHIP_ERASE_QSPI;

        /* send header */
        return gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf);
}

int gdb_server_cmd_run(uint32_t address)
{
        uint8_t header_buf[8];

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_RUN;
        header_buf[2] = (uint8_t) 4;
        header_buf[3] = (uint8_t) (4 >> 8);

        header_buf[4] = (uint8_t) (address);
        header_buf[5] = (uint8_t) (address >> 8);
        header_buf[6] = (uint8_t) (address >> 16);
        header_buf[7] = (uint8_t) (address >> 24);

        /* send header */
        return gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf);
}

int gdb_server_cmd_write_otp(uint32_t address, const uint32_t *buf, uint32_t len)
{
        uint8_t header_buf[8];
        uint32_t size = len * sizeof(*buf);
        uint32_t part_size;
        int status = 0;

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create constant part of header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_WRITE_OTP;

        for (part_size = 0; part_size < size;) {
                size_t write_size = ((CHUNK_SIZE > (size - part_size)) ? (size - part_size) :
                                                                                        CHUNK_SIZE);
                header_buf[2] = (uint8_t) (4 + write_size);
                header_buf[3] = (uint8_t) ((4 + write_size) >> 8);

                header_buf[4] = (uint8_t) (address);
                header_buf[5] = (uint8_t) (address >> 8);
                header_buf[6] = (uint8_t) (address >> 16);
                header_buf[7] = (uint8_t) (address >> 24);

                /* send data */
                gdb_server_send_write_cmd(swd_addr.buf_addr, write_size, (const uint8_t *) buf +
                                                                                        part_size);

                /* send header */
                if ((status = gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf))
                                                                                        != 0) {
                        return status;
                }

                /* wait for ACK or NACK */
                if ((status = gdb_server_read_ack()) != 0) {
                        return status;
                }

                part_size += write_size;
                /* It is a cell address - should be divided by 8 bytes */
                address += (write_size >> 3);
        }

        return status;
}
int gdb_server_cmd_read_otp(uint32_t address, uint32_t *buf, uint32_t len)
{
        uint8_t header_buf[10];
        uint32_t size = len * sizeof(*buf);
        int status;

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_READ_OTP;
        header_buf[2] = (uint8_t) 6;
        header_buf[3] = (uint8_t) (6 >> 8);

        header_buf[4] = (uint8_t) (address);
        header_buf[5] = (uint8_t) (address >> 8);
        header_buf[6] = (uint8_t) (address >> 16);
        header_buf[7] = (uint8_t) (address >> 24);

        header_buf[8] = (uint8_t) len;
        header_buf[9] = (uint8_t) (len >> 8);

        /* send header */
        if ((status = gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf)) != 0) {
                return status;
        }

        /* Check is command returned NAK */
        if ((status = gdb_server_read_ack()) != 0) {
                return status;
        }

        /* receive data */
        if ((status = gdb_server_send_read_cmd(swd_addr.buf_addr, size)) != 0) {
                return status;
        }

        return (gdb_server_frame_to_uint8_buf((uint8_t *) buf, size) ? 0 :
                                                                ERR_GDB_SERVER_INVALID_RESPONSE);
}

int gdb_server_cmd_read_qspi(uint32_t address, uint8_t *buf, uint32_t len)
{
        uint8_t header_buf[10];
        uint32_t size = len * sizeof(*buf);
        int status = 0;

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_READ_QSPI;
        header_buf[2] = (uint8_t) 6;
        header_buf[3] = (uint8_t) (6 >> 8);

        header_buf[4] = (uint8_t) (address);
        header_buf[5] = (uint8_t) (address >> 8);
        header_buf[6] = (uint8_t) (address >> 16);
        header_buf[7] = (uint8_t) (address >> 24);

        header_buf[8] = (uint8_t) len;
        header_buf[9] = (uint8_t) (len >> 8);

        /* send header */
        if ((status = gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf)) != 0) {
                return status;
        }

        /* receive data */
        if ((status = gdb_server_send_read_cmd(swd_addr.buf_addr, size)) != 0) {
                return status;
        }

        return ((!status && gdb_server_frame_to_uint8_buf((uint8_t *) buf, len)) ? 0 :
                                                                ERR_GDB_SERVER_INVALID_RESPONSE);
}

int gdb_server_cmd_is_empty_qspi(unsigned int size, unsigned int start_address, int *ret_number)
{
        uint8_t header_buf[12];
        int status = 0;

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_IS_EMPTY_QSPI;
        header_buf[2] = (uint8_t) 8;
        header_buf[3] = (uint8_t) (8 >> 8);
        header_buf[4] = (uint8_t) (size);
        header_buf[5] = (uint8_t) (size >> 8);
        header_buf[6] = (uint8_t) (size >> 16);
        header_buf[7] = (uint8_t) (size >> 24);

        header_buf[8] = (uint8_t) (start_address);
        header_buf[9] = (uint8_t) (start_address >> 8);
        header_buf[10] = (uint8_t) (start_address >> 16);
        header_buf[11] = (uint8_t) (start_address >> 24);

        /* send header */
        if ((status = gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf)) != 0) {
                return status;
        }

        /* receive data */
        if ((status = gdb_server_send_read_cmd(swd_addr.buf_addr, sizeof(int))) != 0) {
                return status;
        }

        return (gdb_server_frame_to_uint8_buf((uint8_t *) ret_number, sizeof(uint32_t)) ? 0 :
                                                                ERR_GDB_SERVER_INVALID_RESPONSE);
}

int gdb_server_cmd_read_partition_table(uint8_t **buf, uint32_t *len)
{
        uint8_t header_buf[2];
        int status = 0;

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_READ_PARTITION_TABLE;

        /* send header */
        if ((status = gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf)) != 0) {
                return status;
        }

        return ((!status && gdb_server_read_dynamic_length(buf, len)) ?
                                                                ERR_GDB_SERVER_INVALID_RESPONSE :
                                                                0);
}

int gdb_server_cmd_read_partition(nvms_partition_id_t id, uint32_t address, uint8_t *buf,
                                                                                uint32_t len)
{
        uint8_t header_buf[11];
        uint32_t size = len * sizeof(*buf);
        int status = 0;

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_READ_PARTITION;
        header_buf[2] = (uint8_t) 7;
        header_buf[3] = (uint8_t) (7 >> 8);

        header_buf[4] = (uint8_t) (address);
        header_buf[5] = (uint8_t) (address >> 8);
        header_buf[6] = (uint8_t) (address >> 16);
        header_buf[7] = (uint8_t) (address >> 24);

        header_buf[8] = (uint8_t) len;
        header_buf[9] = (uint8_t) (len >> 8);

        header_buf[10] = (uint8_t) id;

        /* send header */
        if ((status = gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf)) != 0) {
                return status;
        }

        /* receive data */
        if ((status = gdb_server_send_read_cmd(swd_addr.buf_addr, size)) != 0) {
                return status;
        }

        return ((!status && gdb_server_frame_to_uint8_buf((uint8_t *) buf, len)) ? 0 :
                                                                ERR_GDB_SERVER_INVALID_RESPONSE);
}

int gdb_server_cmd_write_partition(nvms_partition_id_t id, uint32_t dst_address,
                                                                uint32_t src_address, size_t size)
{
        uint8_t header_buf[15];

        if (gdb_server_verify_connection()) {
                return ERR_GDB_SERVER_SOCKET;
        }

        /* create header */
        header_buf[0] = SOH;
        header_buf[1] = CMD_WRITE_PARTITION;
        header_buf[2] = (uint8_t) 11;
        header_buf[3] = (uint8_t) (11 >> 8);

        /*
         * if src_address is equal to ADDRESS_TMP then buffer should be written to a temporary
         * buffer on the platform - to the address specified by swd_addr.buf_addr
         */
        src_address = ((src_address == ADDRESS_TMP) ? swd_addr.buf_addr : src_address);

        header_buf[4] = (uint8_t) (src_address);
        header_buf[5] = (uint8_t) (src_address >> 8);
        header_buf[6] = (uint8_t) (src_address >> 16);
        header_buf[7] = (uint8_t) (src_address >> 24);

        header_buf[8] = (uint8_t) size;
        header_buf[9] = (uint8_t) (size >> 8);

        header_buf[10] = (uint8_t) (dst_address);
        header_buf[11] = (uint8_t) (dst_address >> 8);
        header_buf[12] = (uint8_t) (dst_address >> 16);
        header_buf[13] = (uint8_t) (dst_address >> 24);

        header_buf[14] = (uint8_t) (id);

        /* send header */
        return gdb_server_send_swd_cmd_header(sizeof(header_buf), header_buf);
}

int gdb_server_cmd_boot(void)
{
        return gdb_server_load_image();
}

void gdb_server_disconnect()
{
        /* close socket if open */
        if (gdb_server_sock > -1) {
                closesocket(gdb_server_sock);
                gdb_server_sock = -1;
        }
}


void gdb_server_close(int pid)
{
        if (configuration.no_kill_gdb_server == NO_KILL_MODE_NONE ||
                                        configuration.no_kill_gdb_server == NO_KILL_MODE_CONNECT) {
                gdb_server_stop(pid);
        }

        /* Cleanup local configuration structure */
        if (configuration.host_name) {
                free(configuration.host_name);
        }

        if (configuration.gdb_server_path) {
                free(configuration.gdb_server_path);
        }
        if (target_reset_cmd)
                free(target_reset_cmd);
}

void gdb_invalidate_stub(void)
{
	uartboot_loaded = false;
}


#ifndef WIN32
static prog_gdb_server_info_t parse_ps_line(char *line)
{
        char arg[50];
        char *token;
        prog_gdb_server_info_t instance = {
                .pid = -1,
                .port = -1,
                .sn = SERIAL_NUMBER_NA
        };

        token = strtok(line, " ");

        if (!token) {
                return instance;
        }

        instance.pid = atoi(token);

        for (; token; token = strtok(NULL, " ")) {
                str_to_lower(token, arg);

                if (strstr(arg, "usb")) {
                        instance.sn = strtoll(strchr(arg, '=') + 1, NULL, 10);
                } else if (strstr(arg, "port")) {
                        /*
                         * Port number must be given if flag exist - without it GDB Server
                         * doesn't run (command line error will appear).
                         */
                        token = strtok(NULL, " ");
                        instance.port = atoi(token);
                }
        }

        /* Port can be not included in command line - assume default port */
        instance.port = (instance.port > -1) ? instance.port : GDB_SERVER_DEFAULT_PORT;

        return instance;
}

prog_gdb_server_info_t *gdb_server_get_instances(const char *gdb_server_cmd)
{
        prog_gdb_server_info_t *gdb_server_instances;
        char gdb_name[100];
        char cmd[500];
        char line[500];
        int index = 0;
        FILE *fp;

        get_name_from_path(gdb_server_cmd, gdb_name);
        snprintf(cmd, sizeof(cmd), "ps  x 2>/dev/null |awk '$5 ~ \"%s\" {$2=$3=$4=\"\"; print $0}'",
                                                                                        gdb_name);

        fp = popen(cmd, "r");

        if (!fp) {
                return NULL;
        }

        /* Allocate memory for instances array - one element more for invalid marker */
        gdb_server_instances = malloc((GDB_SERVER_INSTANCES_LIMIT + 1) *
                                                                sizeof(prog_gdb_server_info_t));

        if (!gdb_server_instances) {
                /* Allocation failed - do cleanup */
                pclose(fp);
                return NULL;
        }

        while (fgets(line, sizeof(line), fp)) {
                if (feof(fp)) {
                        break;
                }

                gdb_server_instances[index] = parse_ps_line(line);

                if (gdb_server_instances[index].pid > -1) {
                        ++index;
                }

                if (index == GDB_SERVER_INSTANCES_LIMIT) {
                        break;
                }
        }

        /* The end of valid entries */
        gdb_server_instances[index].pid = -1;

        pclose(fp);

        if (index == 0) {
                free(gdb_server_instances);
                gdb_server_instances = NULL;
        }

        return gdb_server_instances;
}
#else
static int get_gdb_server_pids(const char *proc_name, prog_gdb_server_info_t *instances, int max_num)
{
        int index = 0;
        HANDLE snap_shot;
        PROCESSENTRY32 proc_entry;

        proc_entry.dwSize = sizeof(PROCESSENTRY32);

        /* Get process ID array */
        snap_shot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if ((snap_shot !=  INVALID_HANDLE_VALUE) && Process32First(snap_shot, &proc_entry)) {
                do {
                        if (_stricmp(proc_name, proc_entry.szExeFile) == 0) {
                                instances[index].pid = proc_entry.th32ProcessID;
                                instances[index].sn = SERIAL_NUMBER_NA;
                                instances[index].port = -1;
                                ++index;

                                if (index == max_num) {
                                        break;
                                }
                        }
                } while (Process32Next(snap_shot, &proc_entry));
        }

        if (snap_shot !=  INVALID_HANDLE_VALUE) {
                CloseHandle(snap_shot);
        }

        return index;
}

static long long get_serial_number(const char *device, const char *symlink)
{
        int i;
        const char *sn_ptr = NULL;

        if (strstr(device, JLINK_PRO_PREFIX)) {
                /* Motherboard rev. C */
                /* Device name is like USB#VID_1366&PID_0101#SERIAL_NUMBER#{INTERFACE} */
                sn_ptr = device + strlen(JLINK_PRO_PREFIX) + 1;
        } else if (strstr(device, JLINK_LITE_PREFIX)) {
                /* Motherboard rev. B and LiteDK */
                HDEVINFO devs_info;
                SP_DEVINFO_DATA dev_info_data;

                devs_info = SetupDiGetClassDevs(NULL, NULL, NULL, DIGCF_ALLCLASSES | DIGCF_PRESENT);

                if (devs_info == INVALID_HANDLE_VALUE) {
                        return SERIAL_NUMBER_NA;
                }

                dev_info_data.cbSize = sizeof(SP_DEVINFO_DATA);

                i = 0;

                while (SetupDiEnumDeviceInfo(devs_info, i, &dev_info_data)) {
                        TCHAR buffer[1000];
                        DEVINST parent;
                        TCHAR parent_instance_id[1000];

                        ++i;

                        if (!SetupDiGetDeviceRegistryProperty(devs_info, &dev_info_data,
                                SPDRP_PHYSICAL_DEVICE_OBJECT_NAME, NULL, (PBYTE) buffer,
                                                                        sizeof(buffer), NULL)) {
                                continue;
                        }

                        if (strcmp(buffer, symlink)) {
                                continue;
                        }


                        if (CM_Get_Parent(&parent, dev_info_data.DevInst, 0) != CR_SUCCESS) {
                                continue;
                        }

                        if (CM_Get_Device_ID(parent, parent_instance_id, 1000, 0) != CR_SUCCESS) {
                                continue;
                        }

                        if (strstr(parent_instance_id, "VID_" JLINK_VID) &&
                                                strstr(parent_instance_id, "PID_" JLINK_LITE_PID)) {
                                /*
                                 * Parent's instance ID should be like
                                 * USB\VID_1366&PID_0105\SERIAL_NUMBER
                                 */
                                sn_ptr = parent_instance_id + strlen(JLINK_PARENT_PREFIX) + 1;
                        }

                        break;
                }

                SetupDiDestroyDeviceInfoList(devs_info);
        }

        return sn_ptr ? strtoll(sn_ptr, NULL, 10) : SERIAL_NUMBER_NA;
}

static int get_jlink_devices(jlink_dev_t *devices, int max_num)
{
        int index = 0;
        TCHAR* device;
        TCHAR target_path[TARGET_LEN_LIMIT];

        /* Query devices */
        if (QueryDosDevice(NULL, target_path, TARGET_LEN_LIMIT) < 1) {
                return 0;
        }

        device = &target_path[0];

        /* Get JLink devices (by interface) */
        while (device[0] != '\0') {
                /* Check device's interface */
                if (strstr(device, JLINK_INTERFACE)) {
                        TCHAR symlink[100];
                        long long sn;

                        /* Get device's SymLink (like \Device\00000001) */
                        QueryDosDevice(device, symlink, sizeof(symlink));

                        /* Try get device's serial number */
                        sn = get_serial_number(device, symlink);

                        if (sn == SERIAL_NUMBER_NA) {
                                goto no_jlink_dev;
                        }

                        /* Get serial number from name */
                        devices[index].sn = sn;
                        /* Copy device SymLink  */
                        strcpy(devices[index].dev_name, symlink);
                        ++index;

                        if (index == max_num) {
                                return (index - 1);
                        }
                }
no_jlink_dev:
                device += strlen(device) + 1;
        }

        return index;
}

static int get_gdb_server_port(int instance_pid)
{
        FILE *fp;
        char buf[50];
        bool data_started = false;
        int pid;
        int cnt = 0;
        int port = -1;

        fp = _popen("netstat -nao", "r");

        while (fscanf(fp, "%s", buf) == 1) {
                if (!data_started) {
                        if (!strcmp(buf, "PID")) {
                                data_started = true;
                        }

                        continue;
                }

                switch (cnt) {
                case 1:
                        /* local address - get port */
                        port = atoi(strchr(buf, ':') + 1);
                        break;
                case 2:
                        /*
                         * The '*:*' value of foreign address is appearing in case of UDP protocol.
                         * In this protocol the state value doesn't exist - state column should be
                         * skipped.
                         */
                        if (!strcmp(buf, "*:*")) {
                                ++cnt;
                        }
                        break;
                case 4:
                        /* pid */
                        pid = atoi(buf);

                        if (pid == instance_pid) {
                                /* Skip SWO, telnet and RTT ports */
                                if (port != 2332 && port != 2333 && port != 19021 && port != 19030) {
                                        _pclose(fp);
                                        return port;
                                }
                        }
                        break;
                }

                cnt = (cnt + 1) % 5;
        }

        _pclose(fp);

        return -1;
}

static long long get_sn_for_process(int pid, int devices_num, const jlink_dev_t *devices,
                                                        PSYSTEM_HANDLE_INFORMATION handles_info)
{
        unsigned long i;
        HANDLE proc_handle = OpenProcess(PROCESS_DUP_HANDLE, FALSE, pid);

        if (!proc_handle) {
                /* Cannot open the process */
                return SERIAL_NUMBER_NA;
        }

        /* Check all system handles */
        for (i = 0; i < handles_info->Count; ++i) {
                HANDLE own_handle = NULL;
                PVOID name_info = NULL;
                UNICODE_STRING name;
                ULONG length;
                int j;
                char buffer[100];

                if ((handles_info->Handle[i].OwnerPid != pid) ||
                                                (handles_info->Handle[i].ObjectType != 0x1c)) {
                        /* Skip not file handles and not GDB Server process handles */
                        continue;
                }

                /* Duplicate handle (needed for querying)  */
                if (!DuplicateHandle(proc_handle, (HANDLE) (UINT) handles_info->Handle[i].HandleValue,
                                                        GetCurrentProcess(), &own_handle, 0, 0, 0)) {
                        continue;
                }

                /* Get proper buffer's length */
                NtQueryObject(own_handle, ObjectNameInformation, name_info, 0, &length);
                name_info = malloc(length);

                if (!name_info) {
                        CloseHandle(own_handle);
                        continue;
                }

                /* Get object's name */
                if (!NT_SUCCESS(NtQueryObject(own_handle, ObjectNameInformation, name_info, length,
                                                                                        &length))) {
                        free(name_info);
                        CloseHandle(own_handle);
                        continue;
                }

                /* Get string */
                name = *(PUNICODE_STRING) name_info;
                wcstombs(buffer, name.Buffer, sizeof(buffer));
                /* Cleanup */
                free(name_info);
                CloseHandle(own_handle);

                for (j = 0; j < devices_num; ++j) {
                        if (!strcmp(buffer, devices[j].dev_name)) {
                                CloseHandle(proc_handle);
                                return devices[j].sn;
                        }
                }
        }

        CloseHandle(proc_handle);

        return SERIAL_NUMBER_NA;
}

prog_gdb_server_info_t *gdb_server_get_instances(const char *gdb_server_cmd)
{
        jlink_dev_t devices[JLINK_DEVICE_LIMIT];
        int i;
        unsigned proc_num, dev_num;
        char gdb_server_name[MAX_PATH];
        prog_gdb_server_info_t *gdb_server_instances;
        ULONG size = HANDLES_START_NUM * sizeof(SYSTEM_HANDLE_INFORMATION);
        PSYSTEM_HANDLE_INFORMATION handles_info;

        get_name_from_path(gdb_server_cmd, gdb_server_name);

        /* Allocate memory for instances array - one element more for invalid marker */
        gdb_server_instances = malloc((GDB_SERVER_INSTANCES_LIMIT + 1) *
                                                                sizeof(prog_gdb_server_info_t));

        if (!gdb_server_instances) {
                /* Allocation failed - do cleanup */
                return NULL;
        }

        /* Get GDB Server processes ID */
        proc_num = get_gdb_server_pids(gdb_server_name, gdb_server_instances,
                                                                        GDB_SERVER_INSTANCES_LIMIT);

        if (proc_num == 0) {
                /* No GDB Server process was found or error occurred */
                free(gdb_server_instances);
                return NULL;
        }

        /* Mark first invalid instance entry */
        gdb_server_instances[proc_num].pid = -1;

        dev_num = get_jlink_devices(devices, JLINK_DEVICE_LIMIT);

        if (dev_num == 0) {
                /* No device was found - skip checking handles */
                goto get_ports;
        }

        /* Allocate proper size for handles information */
        handles_info = (PSYSTEM_HANDLE_INFORMATION) malloc(size);

        while (NtQuerySystemInformation(SystemHandleInformation, handles_info, size, NULL) ==
                                                                STATUS_INFO_LENGTH_MISMATCH) {
                size *= 2;

                free(handles_info);
                handles_info = malloc(size);

                /* Allocation failed - skip getting serial number */
                if (!handles_info) {
                        goto get_ports;
                }
        }

        /* Get handles informations */
        if (!NT_SUCCESS(NT_SUCCESS(NtQuerySystemInformation(SystemHandleInformation, handles_info,
                                                                                size, NULL)))) {
                /* Function failed - cleanup */
                if (handles_info) {
                        free(handles_info);
                }

                goto get_ports;
        }

        /* Get device's serial number for each GDB Server instance */
        for (i = 0; i < proc_num; ++i) {
                gdb_server_instances[i].sn = get_sn_for_process(gdb_server_instances[i].pid,
                                                                dev_num, devices, handles_info);
        }

        free(handles_info);

get_ports:
        /* Get port number for each instance */
        for (i = 0; i < proc_num; ++i) {
                gdb_server_instances[i].port = get_gdb_server_port(gdb_server_instances[i].pid);
        }

        return gdb_server_instances;
}
#endif
