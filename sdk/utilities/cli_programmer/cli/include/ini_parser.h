/**
 ****************************************************************************************
 *
 * @file ini_parser.h
 *
 * @brief Parser for .ini files - API.
 *
 * Copyright (C) 2015-2016 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */
#ifndef INI_PARSER_H
#define INI_PARSER_H

#include "queue.h"

/* Initialize ini queue */
#define INI_QUEUE_INIT(q) queue_init(q)

/**
 * Representation of one parameter
 */
typedef struct {
        /** Section */
        char *section;
        /** Key */
        char *key;
        /** Value */
        char *value;
} ini_conf_elem_t;

/**
 * \brief Load configuration from .ini file .
 *
 * Read file for configuration parameters. Each parameter is added
 * to queue.
 *
 * \param [in] file_path        path to .ini file
 * \param [in] ini_queue        initialized queue instance
 *
 * \return true if file was loaded properly, false otherwise
 *
 */
bool ini_queue_load_file(const char *file_path, queue_t *ini_queue);

/**
 * \brief Save configuration to .ini file.
 *
 * \param [in] file_path        path to .ini file
 * \param [in] ini_queue        queue instance with configuration parameters
 *
 * \return true if file was saved properly, false otherwise
 *
 */
bool ini_queue_save_file(const char *file_path, const char *hdr_comment, queue_t *ini_queue);

/**
 * \brief Add configuration parameter to parameter queue
 *
 * \param [in] ini_queue        queue instance with configuration parameters
 * \param [in] section          section name
 * \param [in] key              parameter key
 * \param [in] value            parameter value
 */
void ini_queue_add(queue_t *ini_queue, const char *section, const char *key, const char *value);

/**
 *  \brief Get parameter value for specified section and key
 *
 * \param [in] ini_queue        queue instance with configuration parameters
 * \param [in] section_name     section name
 * \param [in] key              parameter key
 *
 * \return value for specified section and key if exist, NULL otherwise
 */
const char *ini_queue_get_value(const queue_t *ini_queue, const char *section_name, const char *key);

/**
 *  \brief Take first parameter from parameters queue
 *
 * Returned parameter's key, value and section fields were dynamic allocated - they should be freed
 * after use.
 *
 * \param [in] ini_queue        queue instance with configuration parameters
 *
 * \return parameter instance with key, section and value fields set if queue not empty, parameter
 * instance with set fields to NULL otherwise
 */
ini_conf_elem_t ini_queue_pop(queue_t *ini_queue);

#endif /* INI_PARSER_H */
