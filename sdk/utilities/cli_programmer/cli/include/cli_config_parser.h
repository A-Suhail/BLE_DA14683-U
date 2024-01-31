/**
 ****************************************************************************************
 *
 * @file cli_config_parser.h
 *
 * @brief Parser for CLI programmer configuration - API.
 *
 * Copyright (C) 2015-2016 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */
#ifndef CLI_CONFIG_PARSER_H
#define CLI_CONFIG_PARSER_H

#include <stdbool.h>
#include "cli_common.h"

#define DEFAULT_CLI_CONFIG_FILE_NAME "cli_programmer.ini"

/**
 * \brief Save CLI programmer configuration to .ini file.
 *
 * \param [in] file_path        path to .ini file
 * \param [in] opts             CLI programmer configuration instance
 *
 * \return true if file was saved properly, false otherwise
 *
 */
bool cli_config_save_to_ini_file(const char *file_path, const struct cli_options *opts);

/**
 * \brief Load CLI programmer configuration from .ini file.
 *
 * \param [in] file_path        path to .ini file
 * \param [in] opts             CLI programmer configuration instance
 *
 * \return true if file was loaded properly, false otherwise
 *
 */
bool cli_config_load_from_ini_file(const char *file_path, struct cli_options *opts);

/**
 * \brief Get default path to CLI programmer configuration file.
 *
 * Default path to configuration file could be: current directory, default user directory or
 * CLI programmer runtime directory - in this order. Function check that file is exist. If file
 * doesnt't exist in any of this three location NULL is returned.
 *
 * \param [in, out] path_buf    allocated buffer for file path
 * \param [in] argv0            CLI programmer argv[0] argument
 *
 * \return default path to CLI programmer configuration file if exist, NULL otherwise
 *
 */
char *get_default_config_file_path(char *path_buf, const char *argv0);

#endif /* CLI_CONFIG_PARSER_H */
