/**
 ****************************************************************************************
 *
 * @file main.c
 *
 * @brief cli programmer to programm RAM
 *
 * Copyright (C) 2015-2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <programmer.h>
#include "cli_common.h"
#include "cli_version.h"
#include "cli_config_parser.h"

#define DEFAULT_BOOTLOADER_FNAME_WIN    "uartboot.bin"
#define DEFAULT_GDB_SERVER_HOST_NAME    "localhost"

#if (__GNUC__ && (!__MINGW32__))
/* symbols defined by linker for embedded uartboot.bin */
extern uint8_t _binary_uartboot_bin_start[];
extern uint8_t _binary_uartboot_bin_end[];
#endif

#ifdef WIN32
#include <windows.h>
/* Microsoft deprecated Posix function */
#define strdup _strdup
#endif

static void free_main_opts_dynamic_fields()
{
        if (main_opts.bootloader_fname) {
               free(main_opts.bootloader_fname);
        }

        if (main_opts.gdb_server_config.host_name) {
               free(main_opts.gdb_server_config.host_name);
        }

        if (main_opts.gdb_server_config.gdb_server_path) {
               free(main_opts.gdb_server_config.gdb_server_path);
        }

        if (main_opts.config_file_path) {
               free(main_opts.config_file_path);
        }

        if (main_opts.target_reset_cmd) {
               free(main_opts.target_reset_cmd);
        }

}

static bool set_default_boot_loader()
{
#if (__GNUC__ && (!__MINGW32__))
        size_t size = _binary_uartboot_bin_end - _binary_uartboot_bin_start;

        printf("bootloader file not specified, using internal uartboot.bin\n\n");
        prog_set_uart_boot_loader(_binary_uartboot_bin_start, size);

        return true;
#elif defined(WIN32)
        HGLOBAL glob;
        uint8_t *bin = NULL;
        HRSRC res = FindResource(NULL, "UARTBOOT", "BINARY_DATA");
        if (res) {
                glob = LoadResource(NULL, res);
                if (glob) {
                        bin = (uint8_t *) LockResource(glob);
                        printf("bootloader file not specified, using internal uartboot.bin\n\n");
                        prog_set_uart_boot_loader(bin, SizeofResource(NULL, res));
                }
        }
        if (!bin) {
                fprintf(stderr, "bootloader file not specified");
                return false;
        }
        return true;
#else
        fprintf(stderr, "bootloader file not specified");
        return false;
#endif
}

int main(int argc, char *argv[])
{
        int p_idx = 1; // start from argv[1]
        int ret = 0;
        char file_path[500];
        int close_data = 0;
        bool gdb_server_used = false;

        printf("cli_programmer %d.%02d\n", CLI_VERSION_MAJOR,
                                                                                CLI_VERSION_MINOR);
        printf("Copyright (c) 2015-2017 Dialog Semiconductor\n\n");

        /* Initialize dynamic main_opt's fields */
        if (main_opts.bootloader_fname) {
               free(main_opts.bootloader_fname);
        }

        main_opts.bootloader_fname = NULL;

        if (main_opts.gdb_server_config.host_name) {
               free(main_opts.gdb_server_config.host_name);
        }

        main_opts.gdb_server_config.host_name = strdup(DEFAULT_GDB_SERVER_HOST_NAME);

        /* Try load configuration from ini file */
        if (cli_config_load_from_ini_file(get_default_config_file_path(file_path, argv[0]), &main_opts)) {
                printf("Configuration from %s file loaded.\n", file_path);
        }

        /* check all opts starting with '-' */
        while (p_idx < argc && argv[p_idx][0] == '-') {
                char opt;
                char *param;

                //if (strlen(argv[p_idx]) != 2) {
                //        continue;
                //}

                opt = argv[p_idx][1];
                param = p_idx + 1 < argc ? argv[p_idx + 1] : NULL;
                if (opt == '-') {
                        char * lopt = &(argv[p_idx][2]);
                        ret = handle_long_option(lopt, param);
                } else {
                        ret = handle_option(opt, param);
                }
                if (ret < 0) {
                        free_main_opts_dynamic_fields();
                        return 1;
                }

                /* handle_option() will return 1 in case parameter was 'consumed' or 0 in case it
                 * was not, i.e. parameter is not required for opt
                 */
                p_idx += 1 + ret;

                /*
                 * Options handlers return <0 value on error and >=0 value on success. Just make
                 * sure here that exit code from cli_programmer will be =0 in case of success.
                 */
                ret = 0;
        }

        if (!main_opts.initial_baudrate) {
                main_opts.initial_baudrate = main_opts.uartboot_config.baudrate;
        }

        if (main_opts.target_reset_cmd) {
                prog_set_target_reset_cmd(main_opts.target_reset_cmd);
        }

        if (main_opts.config_file_path) {
                if (cli_config_save_to_ini_file(main_opts.config_file_path, &main_opts)) {
                        printf("Configuration saved to %s file.\n", main_opts.config_file_path);
                } else {
                        printf("Cannot save configuration to %s file.\n", main_opts.config_file_path);
                        ret = -1;
                }
                goto end;
        }

        if (p_idx >= argc) {
                fprintf(stderr, "serial port parameter not found\n");
                free_main_opts_dynamic_fields();
                return 1;
        }

        /*
         * Check if command parameter exist before opening interface - it does not make sense to
         * open interface only to close it due to missing command parameter...
         */
        if (p_idx + 1 >= argc) {
                fprintf(stderr, "command parameter not found\n");
                free_main_opts_dynamic_fields();
                return 1;
        }

        if (strcmp(argv[p_idx], "gdbserver") == 0) {
                /* Get PID if available */
                close_data = prog_gdb_open(&main_opts.gdb_server_config);
                if (close_data < 0) {
                        fprintf(stderr, "cannot open gdb interface\n");
                        free_main_opts_dynamic_fields();
                        return 1;
                }

                gdb_server_used = true;
        }
        /* argv[p_idx] should be serial port name, we can try to open it */
        else if (prog_serial_open(argv[p_idx], main_opts.uartboot_config.baudrate)) {
                fprintf(stderr, "cannot open serial port\n");
                free_main_opts_dynamic_fields();
                return 1;
        }

        /*
         * Go to next argument which is a command parameter - we already verified if exists before
         * opening interface
         */
        p_idx++;

        if (main_opts.bootloader_fname) {
                ret = prog_set_uart_boot_loader_from_file(main_opts.bootloader_fname);
                if (ret == ERR_FILE_TOO_BIG) {
                        if (!set_default_boot_loader()) {
                                goto end;
                        }
                } else if (ret < 0) {
                        fprintf(stderr, "Can't read bootloader file %s\n",
                                                                        main_opts.bootloader_fname);
                        goto end;
                }
        } else if (!set_default_boot_loader()) {
                goto end;
        }
        if (strcmp(argv[p_idx], "boot")) {
                prog_uartboot_patch_config(&main_opts.uartboot_config);
                prog_set_initial_baudrate(main_opts.initial_baudrate);
        }
        prog_set_uart_timeout(main_opts.timeout);
        ret = handle_command(argv[p_idx], argc - p_idx - 1, &argv[p_idx + 1]);
        if (!ret) {
                printf("done.\n");
        }
end:
        if (gdb_server_used) {
                /* Disconnect from GDB Server */
                prog_gdb_disconnect();
        }

        prog_close_interface(close_data);
        free_main_opts_dynamic_fields();

        return ret;
}
