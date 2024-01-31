/**
 ****************************************************************************************
 *
 * @file ini_parser.c
 *
 * @brief Parser for .ini files.
 *
 * Copyright (C) 2015-2016 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include "ini_parser.h"
#include "queue.h"

#ifdef WIN32
#define strdup _strdup
#endif

#define MAX_KEY_LENGTH 100
#define MAX_VALUE_LENGTH 500
#define MAX_SECTION_LENGTH 100

/** Line type */
typedef enum {
        /** Invalid line */
        INI_LINE_INVALID = 0,
        /** Comment line */
        INI_LINE_COMMENT = 1,
        /** Section line */
        INI_LINE_SECTION = 2,
        /** Parameter line */
        INI_LINE_PARAMETER = 3
} ini_line_t;

typedef struct {
        void *next;
        char *key;
        char *value;
} ini_queue_param_t;

typedef struct {
        void *next;
        queue_t param_queue;
        char *section_name;
} ini_queue_section_t;

/* Write line like: ;comment */
static void write_comment_line(FILE *file, const char *comment)
{
        fprintf(file, ";%s\n", comment);
}

/* Write line like: [section] */
static void write_section_line(FILE *file, const char *section)
{
        fprintf(file, "[%s]\n", section);
}

/* Write line like: key = value */
static void write_parameter_line(FILE *file, const char *key, const char *value)
{
        fprintf(file, "%s = %s\n", key, (value ? value : ""));
}

/* Write line with only new line sign */
static void write_empty_line(FILE *file)
{
        fprintf(file, "\n");
}

static const char *skip_whitespaces(const char *ptr, const char *ptr_end)
{
        for (; ptr < ptr_end; ++ptr) {
                /* Skip whitespaces */
                if (!isspace(*ptr)) {
                        return ptr;
                }
        }

        return ptr_end;
}

static ini_line_t parse_line(const char *line, char *key, char *value)
{
        const char *ptr = line;
        const char *ptr_end = line + strlen(ptr);
        const char *last_char;
        const char *tmp;

        /* Skip whitespaces on the beginning of line */
        if ((ptr = skip_whitespaces(ptr, ptr_end)) == ptr_end) {
                return INI_LINE_INVALID;
        }

        /* Clean value and key strings */
        value[0] = '\0';
        key[0] = '\0';

        /* ptr points on first character, that isn't a whitespace */
        switch (*ptr) {
        case ';':
                /* Line is a comment */
                return INI_LINE_COMMENT;
        case '[':
                /* Line could be a section line */
                if ((ptr = skip_whitespaces(ptr + 1, ptr_end)) == ptr_end) {
                        /* Line with only '[' character and whitespaces */
                        return INI_LINE_INVALID;
                }

                tmp = ptr;

                for (last_char = tmp; tmp < ptr_end; ++tmp ) {
                        if (!isspace(*tmp)) {
                                last_char = tmp;
                        }

                        if (*tmp == ']') {
                                break;
                        }
                 }

                if (*tmp != ']') {
                        /* Invalid section line - without ']' character */
                        return INI_LINE_INVALID;
                }

                /* Copy section name to key and value */
                memcpy(value, ptr, last_char - ptr);
                value[last_char - ptr] = '\0';
                strcpy(key, value);

                return INI_LINE_SECTION;
        default:
                tmp = ptr;

                /* Rewind to '=' character */
                for (last_char = tmp; tmp < ptr_end; ++tmp) {
                        if (*tmp == '=') {
                                break;
                        }

                        if (!isspace(*tmp)) {
                                last_char = tmp;
                        }
                 }

                if (*tmp != '=') {
                        /* Invalid parameter line - without '=' character */
                        return INI_LINE_INVALID;
                }

                /* Copy key name to key */
                memcpy(key, ptr, last_char - ptr + 1);
                key[last_char - ptr + 1] = '\0';

                /* Key without value - correct possibility */
                if ((tmp = skip_whitespaces(tmp + 1, ptr_end)) == ptr_end) {
                        value[0] = '\0';
                        return INI_LINE_PARAMETER;
                }

                ptr = tmp;

                /* Rewind ptr_end to the last character in value - not whitespace */
                for (; ptr_end > ptr; --ptr_end) {
                        if (!isspace(*ptr_end)) {
                                break;
                        }
                 }

                /* Copy value */
                memcpy(value, ptr, ptr_end - ptr - 1);
                value[ptr_end - ptr - 1] = '\0';

                return INI_LINE_PARAMETER;
        }

        return INI_LINE_INVALID;
}

static bool section_match_by_section_name(const void *data, const void *match_data)
{
        const ini_queue_section_t *section = (ini_queue_section_t *) data;
        const char *section_name = (char *) match_data;

        return !strcmp(section->section_name, section_name);
}

static bool param_match_by_key(const void *data, const void *match_data)
{
        const ini_queue_param_t *param = (ini_queue_param_t *) data;
        const char *key = (char *) match_data;

        return !strcmp(param->key, key);
}

void ini_queue_add(queue_t *ini_queue, const char *section, const char *key, const char *value)
{
        ini_queue_section_t *sec;
        ini_queue_param_t *param;

        if ((sec = queue_find(ini_queue, section_match_by_section_name, section)) == NULL) {
                /* Queue doesn't contain specified section - add it */
                sec = malloc(sizeof(ini_queue_section_t));
                queue_init(&(sec->param_queue));
                sec->section_name = strdup(section);

                queue_push_back(ini_queue, sec);
        }

        /* Copy key name */
        param = malloc(sizeof(ini_queue_param_t));
        param->key = strdup(key);

        /* Copy value if exist, assign NULL to value otherwise */
        if (value && (strlen(value) > 0)) {
                param->value = strdup(value);
        } else {
                param->value = NULL;
        }

        /* Add element to proper section */
        queue_push_back(&sec->param_queue, param);
}

const char *ini_queue_get_value(const queue_t *ini_queue, const char *section_name, const char *key)
{
        ini_queue_section_t *section;
        ini_queue_param_t *param;

        if (((section = queue_find(ini_queue, section_match_by_section_name, section_name))
                != NULL) && ((param = queue_find(&section->param_queue, param_match_by_key, key))
                                                                                        != NULL)) {
                /* Parameter with specified key and section exists in the queue - return value of it */
                return param->value;

        }

        /* Parameter doesn't found */
        return NULL;
}

/* Section, key and value fields are dynamic allocated - should be freed after used */
ini_conf_elem_t ini_queue_pop(queue_t *ini_queue)
{
        ini_conf_elem_t elem;
        ini_queue_section_t *section;
        ini_queue_param_t *param;

        elem.key = NULL;
        elem.value = NULL;
        elem.section = NULL;

        while ((section = (ini_queue_section_t *) queue_peek_front(ini_queue)) != NULL) {
                if ((param = queue_pop_front(&section->param_queue)) != NULL) {
                        /* Copy common for few elements section name */
                        elem.section = strdup(section->section_name);
                        elem.key = param->key;
                        elem.value = param->value;

                        /* Section hasn't more parameters - remove it */
                        if (queue_length(&section->param_queue) == 0) {
                                section = queue_pop_front(ini_queue);
                                free(section->section_name);
                        }

                        break;
                } else {
                        /* Section hasn't more parameters - remove it */
                        section = queue_pop_front(ini_queue);
                        free(section->section_name);
                }
        }

        return elem;
}

bool ini_queue_load_file(const char *file_path, queue_t *ini_queue)
{
        FILE *ini_file;
        char line_buf[1024];
        char *current_section;
        char *key;
        char *value;

        if (!file_path) {
                /* Path to file is a pointer to NULL - do not try open it */
                return false;
        }

        /* Open file specified by file path */
        if ((ini_file = fopen(file_path, "r")) == NULL) {
                /* Cannot open specified file */
                return false;
        }

        /* Allocate memory */
        key = malloc(MAX_KEY_LENGTH);
        value = malloc(MAX_VALUE_LENGTH);
        current_section = malloc(MAX_SECTION_LENGTH);
        current_section[0] = '\0';

        while (fgets(line_buf, sizeof(line_buf), ini_file) != NULL) {
                /* Get and parse each line */
                switch(parse_line(line_buf, key, value)) {
                case INI_LINE_SECTION:
                        /* Line is a section line */
                        strcpy(current_section, value);
                        break;
                case INI_LINE_PARAMETER:
                        /* Line is a parameter line */
                        ini_queue_add(ini_queue, current_section, key, value);
                        break;
                default:
                        /* Invalid or comment line */
                        break;
                }
        }

        /* Free memory */
        free(key);
        free(value);
        free(current_section);

        /* Close file */
        fclose(ini_file);

        return true;
}

/* Queue will be empty */
bool ini_queue_save_file(const char *file_path, const char *hdr_comment, queue_t *ini_queue)
{
        FILE *ini_file;
        char current_section[MAX_SECTION_LENGTH];
        ini_conf_elem_t elem;

        if (!file_path) {
                /* Path to file is a pointer to NULL - do not try open it */
                return false;
        }

        /* Open file specified by file path */
        if ((ini_file = fopen(file_path, "w")) == NULL) {
                /* Cannot open specified file */
                return false;
        }

        /* Clean current section name */
        current_section[0] = '\0';

        /* Write comment at the top of file if exist */
        if (hdr_comment != NULL) {
                write_comment_line(ini_file, hdr_comment);
        }

        while (true) {
                /* Get parameter from queue */
                elem = ini_queue_pop(ini_queue);

                if (!elem.section) {
                        /* No more sections in queue */
                        break;
                }

                if (strcmp(current_section, elem.section)) {
                        /* Element is from new section - write section line to file */
                        write_empty_line(ini_file);
                        write_section_line(ini_file, elem.section);
                        strcpy(current_section, elem.section);
                }

                if (!elem.key) {
                        /* No more parameters in queue */
                        break;
                }

                if (elem.value) {
                        /* Write key and value to file */
                        write_parameter_line(ini_file, elem.key, elem.value);
                } else {
                        /* Write key without value to file */
                        write_parameter_line(ini_file, elem.key, "");
                }

                if (elem.key) {
                        /* Free memory */
                        free(elem.key);
                }

                if (elem.value) {
                        /* Free memory */
                        free(elem.value);
                }

                if (elem.section) {
                        /* Free memory */
                        free(elem.section);
                }
        }

        /* Close file */
        fclose(ini_file);

        return true;
}
