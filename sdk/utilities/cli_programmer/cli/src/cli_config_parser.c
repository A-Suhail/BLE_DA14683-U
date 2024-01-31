/**
 ****************************************************************************************
 *
 * @file cli_config_parser.c
 *
 * @brief Parser for CLI programmer configuration.
 *
 * Copyright (C) 2015-2016 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <sys/stat.h>
#ifdef WIN32
#include <shlwapi.h>
#define HOMEPATHENV "USERPROFILE"
#else
#define HOMEPATHENV "HOME"
#endif
#include "cli_common.h"
#include "cli_config_parser.h"
#include "ini_parser.h"
#include "queue.h"

/* Section names */
#define SECTION_NAME_UARTBOOT           "uartboot"
#define SECTION_NAME_GDB_SERVER         "gdb server"
#define SECTION_NAME_CLI                "cli"
#define SECTION_NAME_BIN2IMAGE          "bin2image"
#define SECTION_NAME_TARGET_RESET       "target reset"

/* Comment appear at the top of configuration file */
#define HEAD_COMMENT                    "This is a cli_programmer configuration file."

/* Parameter names in 'cli' section */
#define PARAM_NAME_INITIAL_BAUDRATE     "initial_baudrate"
#define PARAM_NAME_TIMEOUT              "timeout"
#define PARAM_NAME_BOOTLOADER_FNAME     "bootloader_fname"

/* Parameter names in 'uartboot' section */
#define PARAM_NAME_BAUDRATE             "baudrate"
#define PARAM_NAME_TX_PORT              "tx_port"
#define PARAM_NAME_TX_PIN               "tx_pin"
#define PARAM_NAME_RX_PORT              "rx_port"
#define PARAM_NAME_RX_PIN               "rx_pin"

/* Parameter names in 'gdb server' section */
#define PARAM_NAME_PORT                 "port"
#define PARAM_NAME_HOST_NAME            "host_name"
#define PARAM_NAME_GDB_SERVER_PATH      "gdb_server_path"
#define PARAM_NAME_NO_KILL_MODE         "no_kill_mode"

/* bin2image parameters */
#define PARAM_NAME_CHIP_REV             "chip_rev"

/* target reset command */
#define PARAM_NAME_TARGET_RESET_CMD     "target_reset_cmd"

#ifdef WIN32
#define strdup _strdup
#endif

static void add_num_value(queue_t *q, const char *section, const char *key, unsigned int value)
{
        char tmp_buf[100];

        sprintf(tmp_buf, "%u", value);

        ini_queue_add(q, section, key, tmp_buf);
}

static void add_num_value_flagged(queue_t *q, const char *section, const char *key,
                                                                unsigned int value, bool flag)
{
        char tmp_buf[100];

        if (flag) {
                sprintf(tmp_buf, "%u", value);
                ini_queue_add(q, section, key, tmp_buf);
        } else {
                ini_queue_add(q, section, key, NULL);
        }
}

bool cli_config_save_to_ini_file(const char *file_path, const struct cli_options *opts)
{
        queue_t sections_queue;

        INI_QUEUE_INIT(&sections_queue);

        /**
         * Below each value of cli_options instance fields is got and added to configuration
         * parameter queue. If some string parameters haven't value (set to NULL) they are added to
         * queue as keys without values, same for some patched parameters of uartboot configuration.
         */

        /* 'cli' section */
        add_num_value(&sections_queue, SECTION_NAME_CLI, PARAM_NAME_INITIAL_BAUDRATE,
                                                                        opts->initial_baudrate);
        add_num_value(&sections_queue, SECTION_NAME_CLI, PARAM_NAME_TIMEOUT, opts->timeout);
        ini_queue_add(&sections_queue, SECTION_NAME_CLI, PARAM_NAME_BOOTLOADER_FNAME,
                                                                        opts->bootloader_fname);

        /* 'uartboot' section */
        add_num_value_flagged(&sections_queue, SECTION_NAME_UARTBOOT, PARAM_NAME_BAUDRATE,
                        opts->uartboot_config.baudrate, opts->uartboot_config.baudrate_patch);
        add_num_value_flagged(&sections_queue, SECTION_NAME_UARTBOOT, PARAM_NAME_TX_PORT,
                        opts->uartboot_config.tx_port, opts->uartboot_config.tx_port_patch);
        add_num_value_flagged(&sections_queue, SECTION_NAME_UARTBOOT, PARAM_NAME_TX_PIN,
                        opts->uartboot_config.tx_pin, opts->uartboot_config.tx_pin_patch);
        add_num_value_flagged(&sections_queue, SECTION_NAME_UARTBOOT, PARAM_NAME_RX_PORT,
                        opts->uartboot_config.rx_port, opts->uartboot_config.rx_port_patch);
        add_num_value_flagged(&sections_queue, SECTION_NAME_UARTBOOT, PARAM_NAME_RX_PIN,
                        opts->uartboot_config.rx_pin, opts->uartboot_config.rx_pin_patch);

        /* 'gdb server' section */
        add_num_value(&sections_queue, SECTION_NAME_GDB_SERVER, PARAM_NAME_PORT,
                                                                opts->gdb_server_config.port);
        ini_queue_add(&sections_queue, SECTION_NAME_GDB_SERVER, PARAM_NAME_HOST_NAME,
                                                                opts->gdb_server_config.host_name);

        ini_queue_add(&sections_queue, SECTION_NAME_GDB_SERVER, PARAM_NAME_GDB_SERVER_PATH,
                                                        opts->gdb_server_config.gdb_server_path);

        add_num_value(&sections_queue, SECTION_NAME_GDB_SERVER, PARAM_NAME_NO_KILL_MODE,
                                                        opts->gdb_server_config.no_kill_gdb_server);

        /* bin2image section */
        ini_queue_add(&sections_queue, SECTION_NAME_BIN2IMAGE, PARAM_NAME_CHIP_REV,
                                                                                opts->chip_rev);

        /* target reset section */
        ini_queue_add(&sections_queue, SECTION_NAME_TARGET_RESET, PARAM_NAME_TARGET_RESET_CMD,
                                                                                opts->target_reset_cmd);
        /* Save configuration parameters queue to file */
        return ini_queue_save_file(file_path, HEAD_COMMENT, &sections_queue);
}

bool cli_config_load_from_ini_file(const char *file_path, struct cli_options *opts)
{
        ini_conf_elem_t elem;
        queue_t sections_queue;
        unsigned int tmp;

        INI_QUEUE_INIT(&sections_queue);

        /* Load configuration parameters from file to queue */
        if (!ini_queue_load_file(file_path, &sections_queue)) {
                return false;
        }

        /* Get all configuration parameters from queue */
        while ((elem = ini_queue_pop(&sections_queue)).section != NULL) {
                if (!elem.value || strlen(elem.value) == 0) {
                        /* Parameter doesn't contain value - free memory and skip it */
                        free(elem.key);
                        free(elem.section);

                        /* Value is a single character ('\0') - free it */
                        if (elem.value) {
                                free(elem.value);
                        }

                        continue;
                }

                /* Find proper section and parameter by name */
                if (!strcmp(elem.section, SECTION_NAME_CLI)) {
                        /* 'cli' section */
                        if (!strcmp(elem.key, PARAM_NAME_INITIAL_BAUDRATE)) {
                                if (get_number(elem.value, &tmp)) {
                                        opts->initial_baudrate = tmp;
                                }
                        } else if (!strcmp(elem.key, PARAM_NAME_TIMEOUT)) {
                                if (get_number(elem.value, &tmp)) {
                                        opts->timeout = tmp;
                                }
                        } else if (!strcmp(elem.key, PARAM_NAME_BOOTLOADER_FNAME)) {
                                if (opts->bootloader_fname) {
                                        /* Free previously allocated memory */
                                        free(opts->bootloader_fname);
                                }

                                opts->bootloader_fname = strdup(elem.value);
                        }
                } else if (!strcmp(elem.section, SECTION_NAME_UARTBOOT)) {
                        /* 'uartboot' section */
                        if (!strcmp(elem.key, PARAM_NAME_BAUDRATE)) {
                                if (get_number(elem.value, &tmp)) {
                                        opts->uartboot_config.baudrate = tmp;
                                        opts->uartboot_config.baudrate_patch = true;
                                }
                        } else if (!strcmp(elem.key, PARAM_NAME_TX_PORT)) {
                                if (get_number(elem.value, &tmp)) {
                                        opts->uartboot_config.tx_port = tmp;
                                        opts->uartboot_config.tx_port_patch = true;
                                }
                        } else if (!strcmp(elem.key, PARAM_NAME_TX_PIN)) {
                                if (get_number(elem.value, &tmp)) {
                                        opts->uartboot_config.tx_pin = tmp;
                                        opts->uartboot_config.tx_pin_patch = true;
                                }
                        } else if (!strcmp(elem.key, PARAM_NAME_RX_PORT)) {
                                if (get_number(elem.value, &tmp)) {
                                        opts->uartboot_config.rx_port = tmp;
                                        opts->uartboot_config.rx_port_patch = true;
                                }
                        } else if (!strcmp(elem.key, PARAM_NAME_RX_PIN)) {
                                if (get_number(elem.value, &tmp)) {
                                        opts->uartboot_config.rx_pin = tmp;
                                        opts->uartboot_config.rx_pin_patch = true;
                                }
                        }
                } else if (!strcmp(elem.section, SECTION_NAME_GDB_SERVER)) {
                        /* 'gdb server' section */
                        if (!strcmp(elem.key, PARAM_NAME_PORT)) {
                               if (get_number(elem.value, &tmp)) {
                                       opts->gdb_server_config.port = tmp;
                               }
                       } else if (!strcmp(elem.key, PARAM_NAME_HOST_NAME)) {
                               if (opts->gdb_server_config.host_name) {
                                       /* Free previously allocated memory */
                                       free(opts->gdb_server_config.host_name);
                               }

                               opts->gdb_server_config.host_name = strdup(elem.value);
                       } else if (!strcmp(elem.key, PARAM_NAME_GDB_SERVER_PATH)) {
                               if (opts->gdb_server_config.gdb_server_path) {
                                       /* Free previously allocated memory */
                                       free(opts->gdb_server_config.gdb_server_path);
                               }

                               opts->gdb_server_config.gdb_server_path = strdup(elem.value);
                       } else if (!strcmp(elem.key, PARAM_NAME_NO_KILL_MODE)) {
                               if (get_number(elem.value, &tmp)) {
                                       opts->gdb_server_config.no_kill_gdb_server = tmp;
                               }
                       }
                } else if (!strcmp(elem.section, SECTION_NAME_BIN2IMAGE)) {
                        /* 'bin2image' section */
                        if (!strcmp(elem.key, PARAM_NAME_CHIP_REV)) {
                                set_str_opt(&opts->chip_rev, elem.value);
                        }
                } else if (!strcmp(elem.section, SECTION_NAME_TARGET_RESET)) {
                        /* 'target_reset_cmd' section */
                        if (!strcmp(elem.key, PARAM_NAME_TARGET_RESET_CMD)) {
                                set_str_opt(&opts->target_reset_cmd, elem.value);
                        }
                }


                /* Free memory */
                free(elem.key);
                free(elem.value);
                free(elem.section);
        }

        return true;
}

#ifndef WIN32
bool PathAppend(char *dst, const char *more)
{
        size_t len = strlen(dst);
        if (dst[len - 1] != '/') {
                strcat(dst, "/");
        }
        strcat(dst, more);

        return true;
}


bool PathCombine(char *dst, const char *path, const char *more)
{
        size_t len = strlen(path);
        strcpy(dst, path);
        if (len > 0 && dst[len - 1] != '/') {
                strcat(dst, "/");
        }
        strcat(dst, more);

        return true;
}

bool PathRemoveFileSpec(char *path)
{
        char *path_end;
        for (path_end = path + strlen(path) - 1; path_end >= path; path_end--) {
                if (*path_end == '/') {
                        break;
                }
        }
        *path_end = '\0';

        return true;
}

#endif

char *get_default_config_file_path(char *path_buf, const char *argv0)
{
        const char *dir;
        struct stat st;

        /* Default configuration file name in current directory */
        if (stat(DEFAULT_CLI_CONFIG_FILE_NAME, &st) == 0) {
                PathCombine(path_buf, "", DEFAULT_CLI_CONFIG_FILE_NAME);

                return path_buf;
        }

        /* Default configuration file name in user directory */
        if ((dir = getenv(HOMEPATHENV)) != NULL) {
                PathCombine(path_buf, dir, DEFAULT_CLI_CONFIG_FILE_NAME);

                if (stat(path_buf, &st) == 0) {
                        return path_buf;
                }
        }

        strcpy(path_buf, argv0);
        PathRemoveFileSpec(path_buf);

        if (strlen(path_buf) == 0) {
                return NULL;
        }

        PathAppend(path_buf, DEFAULT_CLI_CONFIG_FILE_NAME);

        /* Default configuration file name in CLI programmer runtime directory */
        if (stat(path_buf, &st) == 0) {
                return path_buf;
        }

        /* Any configuration file exist */
        return NULL;
}
