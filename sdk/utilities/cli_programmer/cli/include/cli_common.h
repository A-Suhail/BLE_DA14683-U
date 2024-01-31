/**
 ****************************************************************************************
 *
 * @file cli_common.h
 *
 * @brief Common definitions used across CLI
 *
 * Copyright (C) 2015-2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#ifndef CLI_COMMON_H_
#define CLI_COMMON_H_

#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include "programmer.h"

/* inline keyword is not available when building C code in VC++, but __inline is */
#ifdef _MSC_VER
#define inline __inline
#endif
/**
 * \brief Option values parsed from command line
 *
 */
struct cli_options {
        /**
         * Initial baud rate used for uploading uartboot or a user supplied binary. This depends on
         * the rate used by the OTP boot loader of the device.
         */
        unsigned int initial_baudrate;

        /**
         * UART boot configuration that is patched to the uploaded uartboot binary (in that way
         * passed as a parameter.
         */
        prog_uartboot_config_t uartboot_config;

        unsigned int timeout;           /**< serial port communication timeout */

        char *bootloader_fname;         /**< 2nd stage bootloader file name */

        /**
         * GDB Server configuration
         */
        prog_gdb_server_config_t gdb_server_config;

        /**
         * CLI programmer configuration .ini file path, if NULL - don't save configuration
         */
        char *config_file_path;

        /**
         * Chip revision
         */
        char *chip_rev;

        /**
         * Target reset command
         */
        char *target_reset_cmd;
};

/**
 * \brief Global storage for option values parsed from command line
 *
 */
extern struct cli_options main_opts;

/**
 * \brief Callback for OTP file parser
 *
 * \param [in] addr parsed address
 * \param [in] size parsed size
 * \param [in] value parsed default value
  *
  * \return true if processed successfuly, false otherwise
  *
 */
typedef bool (*otp_file_cb) (uint32_t addr, uint32_t size, uint64_t value);

/**
 * \brief Parse number from string
 *
 * Number will be read in base 10, unless it starts with "0x" (base 16) or "0" (base 8).
 * \p num is modified only when conversion is successful.
 *
 * \param [in] str input string
 * \param [out] num parsed number
 *
 * \return 1 on success, 0 on failure
 *
 */
static inline int get_number(const char *str, unsigned int *num)
{
        char *end;
        unsigned int ret;

        ret = strtoul(str, &end, 0);

        if (end == str || *end != '\0') {
                return 0;
        }

        *num = ret;

        return 1;
}

/**
 * \brief Handle option from command line
 *
 * \param [in] opt option
 * \param [in] param next argument from command line (or NULL if no more arguments)
 *
 * \return < 0 in case of failure,
 *           0 in case of success but \p param was not required for this option
 *           1 in case of success and \p param was required
 *
 */
int handle_option(char opt, const char *param);


/**
 * \brief Handle long option (--) from command line
 *
 * \param [in] opt option
 * \param [in] param next argument from command line (or NULL if no more arguments)
 *
 * \return < 0 in case of failure,
 *           0 in case of success but \p param was not required for this option
 *           1 in case of success and \p param was required
 *
 */
int handle_long_option(const char * opt, const char *param);

/**
 * \brief Handle command from command line
 *
 * \param [in] cmd command
 * \param [in] argc number of arguments
 * \param [in] argv arguments (at least \p argc sould be provided)
 *
 * \return 0 for success, non-zero for failure (can be used as exit code)
 */
int handle_command(char *cmd, int argc, char *argv[]);

/**
 * \brief Pretty-print contents of buffer
 *
 * Prints contents of \p buf using combined hexdump and ASCII format with each row containing \p width
 * bytes from buffer and start/end addressed aligned to width boundary.
 * \p width has to be power of 2 with maximum value 32.
 *
 * \param [in] addr base address of data stored in buffer (for printout)
 * \param [in] buf data buffer
 * \param [in] size size of data buffer
 * \param [in] width width of hexdump row
 *
 */
void dump_hex(uint32_t addr, uint8_t *buf, size_t size, unsigned int width);

/**
 * \brief Pretty-print contents of OTP data buffer
 *
 * This is just special case of dump_hex().
 *
 * \param [in] cell_offset OTP cell
 * \param [in] buf OTP data buffer
 * \param [in] len length ot data buffer (words)
 *
 */
void dump_otp(uint32_t cell_offset, uint32_t *buf, size_t len);

/**
 * \brief Parse OTP description file
 *
 * Parses OTP description file (CSV with tab as delimiter) and fires callback for each valid line.
 * A valid line is where address, size and default value fields have meaningful values.
 *
 * \param [in] fname file name
 * \param [in] value_cb callback
 *
 * \return true when all values were handler properly, false otherwise
 *
 */
bool parse_otp_file(const char *fname, otp_file_cb value_cb);

/**
 * \brief Pretty-print of the partition table contents
 *
 * \param [in] buf buffer the partition table contents are stored in
 * \param [in] total_len the size of buffer in bytes
 *
 * \return 0 partition table found - success, otherwise partition table not found - failed
 *
 */
int dump_partition_table(uint8_t *buf, size_t total_len);

/**
 * \brief Assign string value to pointer
 *
 * Function duplicates string and stores it in user pointer. If opt was
 * already initialized, content is freed before assigning new value.
 *
 * \param [in/out] opt pointer that will have copy of data pointed by val
 * \param [in] val pointer to string value
 *
 */
void set_str_opt(char **opt, const char *val);

/**
 * \brief Check if id matches any partition
 *
 * \param [in] id partition id
 *
 * \return true if id matches at least one partition, false otherwise
 *
 */
bool is_valid_partition_id(nvms_partition_id_t id);

/**
 * \brief Check if name matches any partition
 *
 * \param [in] name string to compare with available partitions names
 * \param [out] id partition id if partition had been found
 *
 * \return true if name matches at least one partition, false otherwise
 *
 */
bool is_valid_partition_name(const char *name, nvms_partition_id_t *id);

#endif /* CLI_COMMON_H_ */
