/**
 ****************************************************************************************
 *
 * @file cmd_handlers.c
 *
 * @brief Handling of CLI commands provided on command line
 *
 * Copyright (C) 2015-2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <programmer.h>
#include "cli_common.h"
#include <assert.h>

#define DEFAULT_SIZE 0x100000

/* Maximum size for an image */
#define MAX_IMAGE_SIZE 0x7F000
/* Maximum size for an OTP image (58kB)*/
#define MAX_OTP_IMAGE_SIZE 0xE800

static int cmdh_write(int argc, char *argv[]);
static int cmdh_read(int argc, char *argv[]);
static int cmdh_write_qspi(int argc, char *argv[]);
static int cmdh_write_qspi_bytes(int argc, char *argv[]);
static int cmdh_write_qspi_exec(int argc, char *argv[]);
static int cmdh_write_suota_image(int argc, char *argv[]);
static int cmdh_read_qspi(int argc, char *argv[]);
static int cmdh_read_partition_table(int argc, char *argv[]);
static int cmdh_read_partition(int argc, char *argv[]);
static int cmdh_write_partition(int argc, char *argv[]);
static int cmdh_write_partition_bytes(int argc, char *argv[]);
static int cmdh_erase_qspi(int argc, char *argv[]);
static int cmdh_chip_erase_qspi(int argc, char *argv[]);
static int cmdh_copy_qspi(int argc, char *argv[]);
static int cmdh_is_empty_qspi(int argc, char *argv[]);
static int cmdh_write_otp(int argc, char *argv[]);
static int cmdh_read_otp(int argc, char *argv[]);
static int cmdh_write_otp_file(int argc, char *argv[]);
static int cmdh_write_otp_raw_file(int argc, char *argv[]);
static int cmdh_read_otp_file(int argc, char *argv[]);
static int cmdh_write_otp_exec(int argc, char *argv[]);
static int cmdh_write_tcs(int argc, char *argv[]);
static int cmdh_boot(int argc, char *argvp[]);
static int cmdh_read_chip_info(int argc, char *argvp[]);
static int cmdh_read_unique_device_id(int argc, char *argvp[]);
static int cmdh_write_key(int argc, char *argv[]);
static int cmdh_read_key(int argc, char *argv[]);


/**
 * \brief CLI command handler description
 *
 */
struct cli_command {
        const char *name;                       /**< name of command */
        int min_num_p;                          /**< minimum number of parameters */
        int (* func) (int argc, char *argv[]);  /**< handler function, return non-zero for success */
};

/**
 * \brief CLI command handlers
 *
 */
static struct cli_command cmds[] = {
        { "write",                 2, cmdh_write, },
        { "read",                  3, cmdh_read, },
        { "write_qspi",            2, cmdh_write_qspi, },
        { "write_qspi_bytes",      2, cmdh_write_qspi_bytes, },
        { "write_qspi_exec",       1, cmdh_write_qspi_exec, },
        { "write_suota_image",     2, cmdh_write_suota_image, },
        { "read_qspi",             3, cmdh_read_qspi, },
        { "erase_qspi",            2, cmdh_erase_qspi, },
        { "chip_erase_qspi",       0, cmdh_chip_erase_qspi, },
        { "read_partition_table",  0, cmdh_read_partition_table, },
        { "read_partition",        4, cmdh_read_partition, },
        { "write_partition",       3, cmdh_write_partition, },
        { "write_partition_bytes", 3, cmdh_write_partition_bytes, },
        { "copy_qspi",             3, cmdh_copy_qspi, },
        { "is_empty_qspi",         0, cmdh_is_empty_qspi, },
        { "write_otp",             2, cmdh_write_otp, },
        { "read_otp",              2, cmdh_read_otp, },
        { "write_otp_file",        1, cmdh_write_otp_file, },
        { "write_otp_raw_file",    2, cmdh_write_otp_raw_file, },
        { "read_otp_file",         1, cmdh_read_otp_file, },
        { "write_otp_exec",        1, cmdh_write_otp_exec, },
        { "write_tcs",             3, cmdh_write_tcs },
        { "boot",                  0, cmdh_boot, },
        { "read_chip_info",        0, cmdh_read_chip_info, },
        { "read_unique_device_id", 0, cmdh_read_unique_device_id, },
        { "write_key",             3, cmdh_write_key, },
        { "read_key",              0, cmdh_read_key, },
        /* end of table */
        { NULL,             0, NULL, }
};

static int get_filesize(const char *fname)
{
        struct stat st;

        if (stat(fname, &st) < 0) {
                return -1;
        }

        return st.st_size;
}

static bool check_otp_cell_address(uint32_t *addr)
{
        uint32_t _addr = *addr;

        /* convert mapped address to cell address, if possible */
        if ((_addr & 0x07F80000) == 0x07F80000) {
                _addr = (_addr & 0xFFFF) >> 3;
        }

        /* there are 0x2000 cells... */
        if (_addr >= 0x2000) {
                return false;
        }

        *addr = _addr;

        return true;
}

static int cmdh_write(int argc, char *argv[])
{
        unsigned int addr;
        const char *fname = argv[1];
        unsigned int size = 0;
        int ret;

        if (!get_number(argv[0], &addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (argc > 2) {
                if (!get_number(argv[2], &size)) {
                        fprintf(stderr, "invalid size\n");
                        return 0;
                }
        } else {
                int file_size = get_filesize(fname);

                if (file_size < 0) {
                        fprintf(stderr, "could not open file\n");
                        return 0;
                }

                size = file_size;
        }

        ret = prog_write_file_to_ram(addr, fname, size);
        if (ret) {
                fprintf(stderr, "write to RAM failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        return 1;
}

static int cmdh_read(int argc, char *argv[])
{
        unsigned int addr;
        const char *fname = argv[1];
        unsigned int size = 0;
        uint8_t *buf = NULL;
        int ret;

        if (!get_number(argv[0], &addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (!get_number(argv[2], &size)) {
                fprintf(stderr, "invalid size\n");
                return 0;
        }

        if (!strcmp(fname, "-") || !strcmp(fname, "--")) {
                buf = malloc(size);
                ret = prog_read_memory(addr, buf, size);
        } else {
                ret = prog_read_memory_to_file(addr, fname, size);
        }
        if (ret) {
                free(buf);
                fprintf(stderr, "read from RAM failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        if (buf) {
                dump_hex(addr, buf, size, !strcmp(fname, "--") ? 32 : 16);
                free(buf);
        }

        return 1;
}

static int cmdh_write_qspi(int argc, char *argv[])
{
        unsigned int addr;
        const char *fname = argv[1];
        unsigned int size = 0;
        int ret;

        if (!get_number(argv[0], &addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (argc > 2) {
                if (!get_number(argv[2], &size)) {
                        fprintf(stderr, "invalid size\n");
                        return 0;
                }
        } else {
                int file_size = get_filesize(fname);

                if (file_size < 0) {
                        fprintf(stderr, "could not open file\n");
                        return 0;
                }

                size = file_size;
        }

        ret = prog_write_file_to_qspi(addr, fname, size);
        if (ret) {
                fprintf(stderr, "write to QSPI failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        return 1;
}

static int cmdh_write_qspi_bytes(int argc, char *argv[])
{
        unsigned int addr;
        int ret;
        int i;
        unsigned int b;
        uint8_t *buf = (uint8_t *) malloc(argc);

        if (buf == NULL) {
                return 0;
        }

        if (!get_number(argv[0], &addr)) {
                fprintf(stderr, "invalid address %s\n", argv[0]);
                ret = 0;
                goto end;
        }

        for (i = 1; i < argc; ++i) {
                if (!get_number(argv[i], &b)) {
                        fprintf(stderr, "invalid byte '%s'\n", argv[i]);
                        ret = 0;
                        goto end;
                }
                buf[i - 1] = (uint8_t) b;
        }

        ret = prog_write_to_qspi(addr, buf, argc - 1);
        if (ret) {
                fprintf(stderr, "write to QSPI failed: %s (%d)\n", prog_get_err_message(ret), ret);
                ret = 0;
                goto end;
        }
end:
        if (buf) {
                free(buf);
        }

        return 1;
}

/*
 *  Write image to address 0, qQ are added after everything else.
 */
static int prog_write_image_to_qspi_safe(uint8_t *buf, uint32_t size)
{
        int err;
        uint8_t head[2] = { buf[0], buf[1] };

        buf[0] = 0xFF;
        buf[1] = 0xFF;

        err = prog_write_to_qspi(0, buf, size);

        if (!err) {
                err = prog_write_to_qspi(0, head, 2);
        }

        return err;
}

static int prog_write_exec(uint8_t *buf, int size, image_mode_t mode, image_type_t type)
{
        int err;
        chip_info_t chip_info;
        uint8_t *buf_with_hdr;
        int size_with_hdr = size + IMAGE_HEADER_SIZE;

        if (buf == NULL) {
                return ERR_PROG_INVALID_ARGUMENT;
        }

        err = prog_read_chip_info(&chip_info);
        if (err) {
                return err;
        }

        /* Chip revision specified, compare with what read from board */
        if (main_opts.chip_rev && *main_opts.chip_rev) {
                if (strcmp(chip_info.chip_rev, main_opts.chip_rev)) {
                        return ERR_PROG_QSPI_IMAGE_FORMAT;
                }
        }

        if (type == IMG_OTP) {
                if (strcmp(chip_info.chip_rev, "680AH") != 0) {
                        /* Header is not needed for newer chip revision */
                        size_with_hdr = size;
                }

                if (size_with_hdr % 4) {
                        /* Align the buffer to multiples of 4 bytes */
                        size_with_hdr += 4 - size_with_hdr % 4;
                }
        }

        /* Buffer must be big enough to contain binary + header */
        buf_with_hdr = (uint8_t *) malloc(size_with_hdr);

        if (!buf_with_hdr) {
                return ERR_PROG_INSUFICIENT_BUFFER;
        }

        if (type == IMG_OTP) {
                /* Make sure that unused by image bytes are zeroed (3, 2 or 1 bytes in the last word */
                memset(buf_with_hdr, 0, size_with_hdr);
        }

        err = prog_make_image(buf, size, chip_info.chip_rev, type, mode, buf_with_hdr,
                                                                        size_with_hdr, NULL);

        if (err >= 0) {
                if (type == IMG_QSPI) {
                        err = prog_write_image_to_qspi_safe(buf_with_hdr, size_with_hdr);
                } else if (type == IMG_OTP) {
                        err = prog_write_image_to_otp(buf_with_hdr, size_with_hdr, mode);
                } else {
                        return ERR_PROG_INVALID_ARGUMENT;
                }
        }

        free(buf_with_hdr);

        return err;
}

int prog_write_executable_file(const char *file_name, image_mode_t mode, image_type_t type)
{
        int err = 0;
        uint8_t *buf = NULL;
        FILE *f = NULL;
        struct stat fstat;
        int size;

        if (stat(file_name, &fstat) < 0 || !S_ISREG(fstat.st_mode)) {
                return ERR_FILE_OPEN;
        }

        size = (int) fstat.st_size;
        f = fopen(file_name, "rb");
        if (f == NULL) {
                err = ERR_FILE_OPEN;
                goto end;
        }

        buf = (uint8_t *) malloc(size);
        if (buf == NULL) {
                err = ERR_ALLOC_FAILED;
                goto end;
        }

        if (fread(buf, 1, size, f) != size) {
                err = ERR_FILE_READ;
                goto end;
        }

        err = prog_write_exec(buf, fstat.st_size, mode, type);
end:
        if (buf) {
                free(buf);
        }

        return err;
}

static int cmdh_write_qspi_exec(int argc, char *argv[])
{
        const char *fname = argv[0];
        struct stat fstat;
        int ret;

        if (stat(fname, &fstat) < 0 || !S_ISREG(fstat.st_mode)) {
                fprintf(stderr, "Invalid file specified %s\n", fname);
                return 0;
        }

        if (fstat.st_size > MAX_IMAGE_SIZE) {
                fprintf(stderr, "File %s is too big\n", fname);
                return 0;
        }

        ret = prog_write_executable_file(fname, IMG_CACHED, IMG_QSPI);
        if (ret) {
                fprintf(stderr, "Write executable failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }
        return 1;
}

int prog_write_qspi_suota_image_file(const char *file_name, const char *version)
{
        int err = 0;
        uint8_t *buf = NULL;
        FILE *f = NULL;
        struct stat fstat;
        int size;

        if (stat(file_name, &fstat) < 0 || !S_ISREG(fstat.st_mode)) {
                return ERR_FILE_OPEN;
        }

        size = (int) fstat.st_size;
        f = fopen(file_name, "rb");
        if (f == NULL) {
                err = ERR_FILE_OPEN;
                goto end;
        }

        buf = (uint8_t *) malloc(size);
        if (buf == NULL) {
                err = ERR_ALLOC_FAILED;
                goto end;
        }

        if (fread(buf, 1, size, f) != size) {
                err = ERR_FILE_READ;
                goto end;
        }

        err = prog_write_qspi_suota_image(buf, fstat.st_size, version, fstat.st_mtime, 0xFFFF);
end:
        if (buf) {
                free(buf);
        }

        return err;
}

static int cmdh_write_suota_image(int argc, char *argv[])
{
        const char *fname = argv[0];
        const char *version = argv[1];
        struct stat fstat;
        int ret;

        if (stat(fname, &fstat) < 0 || !S_ISREG(fstat.st_mode)) {
                fprintf(stderr, "Invalid file specified %s\n", fname);
                return 0;
        }

        if (fstat.st_size > MAX_IMAGE_SIZE) {
                fprintf(stderr, "File %s is too big\n", fname);
                return 0;
        }

        ret = prog_write_qspi_suota_image_file(fname, version);
        if (ret) {
                fprintf(stderr, "Write SUOTA image failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }
        return 1;
}

static int cmdh_read_qspi(int argc, char *argv[])
{
        unsigned int addr;
        const char *fname = argv[1];
        unsigned int size = 0;
        uint8_t *buf = NULL;
        int ret;

        if (!get_number(argv[0], &addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (!get_number(argv[2], &size)) {
                fprintf(stderr, "invalid size\n");
                return 0;
        }

        if (!strcmp(fname, "-") || !strcmp(fname, "--")) {
                buf = malloc(size);
                if (!buf) {
                        ret = ERR_ALLOC_FAILED;
                } else {
                        ret = prog_read_qspi(addr, buf, size);
                }
        } else {
                ret = prog_read_qspi_to_file(addr, fname, size);
        }
        if (ret) {
                free(buf);
                fprintf(stderr, "read from QSPI failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        if (buf) {
                dump_hex(addr, buf, size, !strcmp(fname, "--") ? 32 : 16);
                free(buf);
        }

        return 1;
}

static int cmdh_erase_qspi(int argc, char *argv[])
{
        unsigned int addr;
        unsigned int size;
        int ret;

        if (!get_number(argv[0], &addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (!get_number(argv[1], &size)) {
                fprintf(stderr, "invalid size\n");
                return 0;
        }

        ret = prog_erase_qspi(addr, size);
        if (ret) {
                fprintf(stderr, "erase QSPI failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        return 1;
}

static int cmdh_read_partition_table(int argc, char *argv[])
{
        int ret = 0;
        unsigned int size = 0;
        uint8_t *buf = NULL;

        ret = prog_read_partition_table(&buf, &size);
        if (ret) {
                fprintf(stderr, "read partition table failed: %s (%d)\n", prog_get_err_message(ret), ret);
                goto done;
        }

        ret = dump_partition_table(buf, size);

done:
        free(buf);
        return (ret == 0);
}

static int cmdh_read_partition(int argc, char *argv[])
{
        unsigned int addr;
        const char *fname = argv[2];
        unsigned int size = 0;
        uint8_t *buf = NULL;
        unsigned int id;
        int ret;

        if (!is_valid_partition_name(argv[0], &id)) {
                if (!get_number(argv[0], &id) || !is_valid_partition_id(id)) {
                        fprintf(stderr, "invalid partition name/id or selected partition doesn't "
                                                                                        "exist\n");
                        return 0;
                }
        }

        if (!get_number(argv[1], &addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (!get_number(argv[3], &size)) {
                fprintf(stderr, "invalid size\n");
                return 0;
        }

        if (!strcmp(fname, "-") || !strcmp(fname, "--")) {
                buf = malloc(size);
                if (!buf) {
                        ret = ERR_ALLOC_FAILED;
                } else {
                        ret = prog_read_partition(id, addr, buf, size);
                }
        } else {
                ret = prog_read_patrition_to_file(id, addr, fname, size);
        }

        if (ret) {
                free(buf);
                fprintf(stderr, "read from partition failed (%d)\n", ret);
                return 0;
        }

        if (buf) {
                dump_hex(addr, buf, size, !strcmp(fname, "--") ? 32 : 16);
                free(buf);
        }

        return 1;
}

static int cmdh_write_partition(int argc, char *argv[])
{
        unsigned int addr;
        const char *fname = argv[2];
        unsigned int size = 0;
        unsigned int id;
        int ret;

        if (!is_valid_partition_name(argv[0], &id)) {
                if (!get_number(argv[0], &id) || !is_valid_partition_id(id)) {
                        fprintf(stderr, "invalid partition name/id\n");
                        return 0;
                }
        }

        if (!get_number(argv[1], &addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (argc > 3) {
                if (!get_number(argv[3], &size)) {
                        fprintf(stderr, "invalid size\n");
                        return 0;
                }
        } else {
                int file_size = get_filesize(fname);

                if (file_size < 0) {
                        fprintf(stderr, "could not open file\n");
                        return 0;
                }

                size = file_size;
        }

        ret = prog_write_file_to_partition(id, addr, fname, size);
        if (ret) {
                fprintf(stderr, "write to partition failed: %s (%d)\n", prog_get_err_message(ret),
                                                                                                ret);
                return 0;
        }

        return 1;
}

static int cmdh_write_partition_bytes(int argc, char *argv[])
{
        unsigned int addr;
        unsigned int id;
        int ret = 0;
        int i;
        unsigned int b;
        uint8_t *buf = (uint8_t *) malloc(argc - 2);

        if (buf == NULL) {
                return ERR_ALLOC_FAILED;
        }

        if (!is_valid_partition_name(argv[0], &id)) {
                if (!get_number(argv[0], &id) || !is_valid_partition_id(id)) {
                        fprintf(stderr, "invalid partition name/id\n");
                        goto end;
                }
        }

        if (!get_number(argv[1], &addr)) {
                fprintf(stderr, "invalid address %s\n", argv[0]);
                goto end;
        }

        for (i = 2; i < argc; ++i) {
                if (!get_number(argv[i], &b)) {
                        fprintf(stderr, "invalid byte '%s'\n", argv[i]);
                        goto end;
                }
                buf[i - 2] = (uint8_t) b;
        }

        ret = prog_write_partition(id, addr, buf, argc - 2);
        if (ret) {
                fprintf(stderr, "write to partition failed: %s (%d)\n", prog_get_err_message(ret),
                                                                                                ret);
                ret = 0;
                goto end;
        }
        ret = 1;

end:
        free(buf);

        return ret;
}

static int cmdh_copy_qspi(int argc, char *argv[])
{
        unsigned int addr_ram;
        unsigned int addr_qspi;
        unsigned int size;
        int ret;

        if (!get_number(argv[0], &addr_ram)) {
                fprintf(stderr, "invalid RAM address\n");
                return 0;
        }

        if (!get_number(argv[1], &addr_qspi)) {
                fprintf(stderr, "invalid QSPI address\n");
                return 0;
        }

        if (!get_number(argv[2], &size)) {
                fprintf(stderr, "invalid size\n");
                return 0;
        }

        ret = prog_copy_to_qspi(addr_ram, addr_qspi, size);
        if (ret) {
                fprintf(stderr, "erase QSPI failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        return 1;
}

static int cmdh_is_empty_qspi(int argc, char *argv[])
{
        unsigned int size = DEFAULT_SIZE;
        unsigned int start_address = 0;
        int ret_number;
        int ret = 0;

        if (argc != 0 && argc != 2) {
                fprintf(stderr, "invalid argument - function is_empty_qspi needs zero or two arguments\n");
                return -1;
        }

        if (argc == 2) {
                if (!get_number(argv[0], &start_address)) {
                        fprintf(stderr, "invalid start address\n");
                        return -1;
                }

                if (!get_number(argv[1], &size) || size == 0) {
                        fprintf(stderr, "invalid size\n");
                        return -1;
                }
        }

        ret = prog_is_empty_qspi(size, start_address, &ret_number);

        if (!ret) {
                if (ret_number <= 0) {
                        printf("QSPI flash region is not empty (byte at 0x%08x + 0x%08x is not 0xFF).\n",
                                                                start_address, (-1 * ret_number));
                } else {
                        printf("QSPI flash region is empty (checked %u bytes).\n", ret_number);
                }
        } else {
                fprintf(stderr, "check QSPI emptiness failed: %s (%d)\n", prog_get_err_message(ret),
                                                                                        ret);
        }

        return ret;
}

static int cmdh_chip_erase_qspi(int argc, char *argv[])
{
        int ret;

        ret = prog_chip_erase_qspi();

        if (ret) {
                fprintf(stderr, "chip erase QSPI failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        return 1;
}

static int cmdh_write_otp(int argc, char *argv[])
{
        unsigned int addr;
        unsigned int length;
        uint32_t *buf;
        int i;
        int ret;

        if (!get_number(argv[0], &addr) || !check_otp_cell_address(&addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (!get_number(argv[1], &length) || !length) {
                fprintf(stderr, "invalid length\n");
                return 0;
        }

        argc -= 2;
        argv += 2;

        buf = calloc(length, sizeof(*buf));
        for (i = 0; i < argc; i++) {
                if (!get_number(argv[i], &buf[i])) {
                        fprintf(stderr, "invalid data (#%d)\n", i + 1);
                        ret = 0;
                        goto done;
                }
        }

        ret = prog_write_otp(addr, buf, length);
        if (ret) {
                fprintf(stderr, "write to OTP failed: %s (%d)\n", prog_get_err_message(ret), ret);
                ret = 0;
                goto done;
        }

        ret = 1;

done:
        free(buf);

        return ret;
}

static int cmdh_read_otp(int argc, char *argv[])
{
        unsigned int addr;
        unsigned int length;
        unsigned int size;
        uint32_t *buf;
        int ret;

        if (!get_number(argv[0], &addr) || !check_otp_cell_address(&addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (!get_number(argv[1], &length) || !length) {
                fprintf(stderr, "invalid length\n");
                return 0;
        }
		
        size = length * sizeof(*buf);

        buf = malloc(size);
		assert(buf != NULL);

        ret = prog_read_otp(addr, buf, length);
        if (ret) {
                fprintf(stderr, "read from OTP failed: %s (%d)\n", prog_get_err_message(ret), ret);
                ret = 0;
                goto done;
        }

        dump_otp(addr, buf, length);

        ret = 1;

done:
        free(buf);

        return ret;
}
static bool write_otp_file_value_cb(uint32_t addr, uint32_t size, uint64_t value)
{
        uint8_t *buf;
        unsigned int i;
        int ret;

        buf = calloc(1, size);
        if (!buf) {
                return false;
        }

        memcpy(buf, &value, size < sizeof(value) ? size : sizeof(value));

        printf("write_otp %04x %d ", addr, size);
        for (i = 0; i < size; i++) {
                printf("%02X", buf[i]);
        }

        ret = prog_write_otp(addr, (void *) buf, size / 4);
        if (ret < 0) {
                printf(" (FAILED: %s (%d))\n", prog_get_err_message(ret), ret);
                free(buf);
                return false;
        }

        free(buf);
        printf(" (OK)\n");

        return true;
}

int cmdh_write_otp_file(int argc, char *argv[])
{
        return parse_otp_file(argv[0], write_otp_file_value_cb);
}

static int cmdh_write_otp_raw_file(int argc, char *argv[])
{
        unsigned int addr;
        const char *fname = argv[1];
        unsigned int size = 0;
        int ret;

        if (!get_number(argv[0], &addr) || !check_otp_cell_address(&addr)) {
                fprintf(stderr, "invalid address\n");
                return 0;
        }

        if (argc > 2) {
                if (!get_number(argv[2], &size)) {
                        fprintf(stderr, "invalid size\n");
                        return 0;
                }
        } else {
                int file_size = get_filesize(fname);

                if (file_size < 0) {
                        fprintf(stderr, "could not open file\n");
                        return 0;
                }

                size = file_size;
        }

        ret = prog_write_file_to_otp(addr, fname, size);
        if (ret) {
                fprintf(stderr, "write to OTP failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        return 1;
}

static bool read_otp_file_value_cb(uint32_t addr, uint32_t size, uint64_t value)
{
        uint8_t *buf;
        int ret;

        buf = calloc(1, size);
        if (!buf) {
                return false;
        }

        printf("read_otp %04x %d ", addr, size);

        ret = prog_read_otp(addr, (void *) buf, size / 4);
        if (ret < 0) {
                printf(" (FAILED: %s (%d))\n", prog_get_err_message(ret), ret);
                free(buf);
                return false;
        }

        printf(" (OK)\n");

        dump_otp(addr, (void *) buf, size / 4);

        free(buf);

        return true;
}

int cmdh_read_otp_file(int argc, char *argv[])
{
        return parse_otp_file(argv[0], read_otp_file_value_cb);
}

static int cmdh_write_otp_exec(int argc, char *argv[])
{
        const char *cached = "CACHED";
        const char *fname = argv[0];
        struct stat fstat;
        int ret;
        image_mode_t mode = IMG_MIRRORED;

        if (stat(fname, &fstat) < 0 || !S_ISREG(fstat.st_mode)) {
                fprintf(stderr, "Invalid file specified %s\n", fname);
                return 0;
        }

        if (argc > 1) {
                if (!strcmp(argv[1], cached)) {
                        mode = IMG_CACHED;
                } else {
                        fprintf(stderr, "invalid mode parameter should be %s\n", cached);
                        return 0;
                }
        }

        if (fstat.st_size > MAX_OTP_IMAGE_SIZE) {
                fprintf(stderr, "File %s is too big\n", fname);
                return 0;
        }

        ret = prog_write_executable_file(fname, mode, IMG_OTP);
        if (ret) {
                fprintf(stderr, "Write executable failed: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }
        return 1;
}

static int cmdh_write_tcs(int argc, char *argv[])
{
        unsigned int length;
        uint32_t *buf;
        unsigned int i;
        uint32_t address;
        int ret;

        if (!get_number(argv[0], &length) || !length) {
                fprintf(stderr, "invalid length\n");
                return 0;
        }

        argc -= 1;
        argv += 1;

        if(length & 0x01){
                fprintf(stderr, "invalid length. TCS entries need to be in pairs\n");
                return 0;
        }
        if(length > TCS_WORD_SIZE){
                fprintf(stderr, "invalid length. length is bigger than TCS size\n");
                return 0;
        }

        length<<=1;
        buf = calloc(length, sizeof(*buf));
		assert(buf != NULL);

        /*Create data + complement data for TCS*/
        for (i = 0; i < (unsigned int)argc; i++) {
                if (!get_number(argv[i], &buf[2*i])) {
                        fprintf(stderr, "invalid data (#%d)\n", i + 1);
                        ret = 0;
                        goto done;
                }
                buf[2*i+1]=~buf[2*i];//calculate the complement
        }

        ret = prog_write_tcs(&address, buf, length);
        if (ret) {
                fprintf(stderr, "write to OTP TCS failed: %s (%d)\n", prog_get_err_message(ret), ret);
                ret = 0;
                goto done;
        }
        printf("TCS contents written: \n");
        dump_otp(address, buf, length);
        ret = 1;

done:
        free(buf);

        return ret;
}
int cmdh_boot(int argc, char *argv[])
{
        int ret;

        ret = prog_boot();
        if (ret < 0) {
                fprintf(stderr, "failed to boot: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        return 1;
}
int cmdh_read_chip_info(int argc, char *argv[])
{
        chip_info_t chip_info;
        int ret;

        if (argc >= 1 && !strcmp(argv[0], "simple")) {
                char chip_rev[CHIP_REV_STRLEN];
                int ret;

                ret = prog_gdb_read_chip_rev(chip_rev);

                if (ret < 0) {
                        fprintf(stderr, "failed to read chip revision: %s (%d)\n",
                                                                prog_get_err_message(ret), ret);
                        return 0;
                }

                printf("CHIP REVISION: %s\n", chip_rev);

                return 1;
        }

        ret = prog_read_chip_info(&chip_info);
        if (ret < 0) {
                fprintf(stderr, "failed to read chip info: %s (%d)\n", prog_get_err_message(ret), ret);
                return 0;
        }

        printf("CHIP INFO:\n"
                "chip_revision = %s\n"
                "chip_id (as read from otp) = %s\n"
                "chip_package = %s\n",
                chip_info.chip_rev, chip_info.chip_otp_id, chip_info.chip_package);
        return 1;
}

static int cmdh_read_unique_device_id(int argc, char *argvp[])
{
        uint8_t udi[UNIQUE_DEVICE_ID_SIZE];
        int ret;
        int i;

        ret = prog_read_unique_device_id(udi);

        if (ret) {
                fprintf(stderr, "failed to read unique device identifier: %s (%d)\n",
                                                                prog_get_err_message(ret), ret);
                return 0;
        }

        printf("Unique device identifier: ");

        for (i = 0; i < UNIQUE_DEVICE_ID_SIZE; i++) {
                printf("%02X", udi[i]);
        }

        printf("\n");

        return 1;
}

static int cmdh_write_key(int argc, char *argv[])
{
        int i, ret;
        unsigned int key_strlen = 0;
        unsigned int key_idx = 0;
        unsigned int key_length = 0;
        uint8_t key_buff[ASYMMETRIC_KEY_MAX_LEN] = { 0 };
        key_type_t type;

        if (!strcmp("sym", argv[0])) {
                type = KEY_TYPE_SYMMETRIC;
        } else if (!strcmp("asym", argv[0])) {
                type = KEY_TYPE_ASYMMETRIC;
        } else {
                fprintf(stderr, "key type must be 'sym' (symmetric) or 'asym' (asymmetric)\n");
                return 0;
        }

        if (!get_number(argv[1], &key_idx)) {
                fprintf(stderr, "invalid key index\n");
                return 0;
        }

        if ((type == KEY_TYPE_ASYMMETRIC && key_idx > ASYMMETRIC_KEY_MAX_IDX) ||
                                (type == KEY_TYPE_SYMMETRIC && key_idx > SYMMETRIC_KEY_MAX_IDX)) {
                fprintf(stderr, "invalid key index\n");
                return 0;
        }

        key_strlen = strlen(argv[2]);

        if (key_strlen % 2) {
                fprintf(stderr, "key hex-string has odd length\n");
                return 0;
        }

        key_length = key_strlen / 2;

        if (type == KEY_TYPE_ASYMMETRIC && (key_length < ASYMMETRIC_KEY_MIN_LEN ||
                                                        key_length > ASYMMETRIC_KEY_MAX_LEN)) {
                fprintf(stderr, "invalid asymmetric key length\n");
                return 0;
        } else if (type == KEY_TYPE_SYMMETRIC && key_length != SYMMETRIC_KEY_LEN) {
                fprintf(stderr, "invalid symmetric key length\n");
                return 0;
        }

        for (i = 0; i < key_length; i++) {
                unsigned int tmp;
                char byte_str[5] = "";

                sprintf(byte_str, "0x%.2s", &argv[2][i * 2]);

                if (!get_number(byte_str, &tmp)) {
                        fprintf(stderr, "invalid key\n");
                        return 0;
                }

                key_buff[i] = (uint8_t) tmp;
        }

        ret = prog_write_key(type, key_idx, key_buff, key_length);

        if (ret < 0) {
                fprintf(stderr, "failed to write %s key: %s (%d)\n", (type == KEY_TYPE_SYMMETRIC) ?
                                        "symmetric" : "asymmetric", prog_get_err_message(ret), ret);
                return 0;
        }

        printf("%s key #%u and its bit inversion written properly.\n", (type == KEY_TYPE_SYMMETRIC) ?
                                                                "Symmetric" : "Asymmetric", key_idx);

        return 1;
}

static void print_key_line(unsigned int index, const uint8_t *buff, unsigned int len, bool valid)
{
        int i;

        printf("#%u ", index);

        for (i = 0; i < len; i++) {
                printf("%02X", buff[i]);
        }

        printf(" (%svalid, %u-bytes)\n", valid ? "" : "in", len);
}

static int cmdh_read_key(int argc, char *argv[])
{
        int i, ret;
        unsigned int key_idx = 0xFFFFFFFF;
        unsigned int key_length = 0;
        uint8_t key_buff[ASYMMETRIC_KEY_MAX_LEN] = { 0 };
        uint8_t empty_key[ASYMMETRIC_KEY_MAX_LEN] = { 0 };
        bool valid;
        bool read_sym = true;
        bool read_asym = true;
        int start_idx;
        int end_idx;

        if (argc >= 1 && !strcmp("sym", argv[0])) {
                read_asym = false;
        } else if (argc >= 1 && !strcmp("asym", argv[0])) {
                read_sym = false;
        } else if (argc >= 1) {
                fprintf(stderr, "key type must be 'sym' (symmetric) or 'asym' (asymmetric)\n");
                return 0;
        }

        if (argc >= 2 && !get_number(argv[1], &key_idx)) {
                fprintf(stderr, "invalid key index\n");
                return 0;
        }

        start_idx = key_idx;
        end_idx = key_idx;

        if (read_asym) {
                if (key_idx == 0xFFFFFFFF) {
                        start_idx = 0;
                        end_idx = ASYMMETRIC_KEY_MAX_IDX;
                }

                printf("Reading asymmetric key%s...\n", (key_idx == 0xFFFFFFFF) ? "s" : "");

                for (i = start_idx; i <= end_idx; i++) {
                        ret = prog_read_key(KEY_TYPE_ASYMMETRIC, i, key_buff, &key_length, &valid);

                        if (ret) {
                                fprintf(stderr, "failed to read key #%u: %s (%d)\n", i,
                                                                prog_get_err_message(ret), ret);
                                return 0;
                        }

                        if (!valid && !memcmp(key_buff, empty_key, key_length)) {
                                printf("#%u EMPTY\n", i);
                        } else {
                                print_key_line(i, key_buff, key_length, valid);
                        }
                }
        }

        if (read_sym) {
                if (key_idx == 0xFFFFFFFF) {
                        start_idx = 0;
                        end_idx = SYMMETRIC_KEY_MAX_IDX;
                }

                printf("Reading symmetric key%s...\n", (key_idx == 0xFFFFFFFF) ? "s" : "");

                for (i = start_idx; i <= end_idx; i++) {
                        ret = prog_read_key(KEY_TYPE_SYMMETRIC, i, key_buff, &key_length, &valid);

                        if (ret) {
                                fprintf(stderr, "failed to read key #%u: %s (%d)\n", i,
                                                                prog_get_err_message(ret), ret);
                                return 0;
                        }

                        if (!valid && !memcmp(key_buff, empty_key, key_length)) {
                                printf("#%u EMPTY\n", i);
                        } else {
                                print_key_line(i, key_buff, key_length, valid);
                        }
                }
        }

        return 1;
}

int handle_command(char *cmd, int argc, char *argv[])
{
        struct cli_command *cmdh = cmds;

        /* lookup command handler */
        while (cmdh->name && strcmp(cmdh->name, cmd)) {
                cmdh++;
        }

        /* handlers table is terminated by empty entry, so name == NULL means no handler found */
        if (!cmdh->name) {
                fprintf(stderr, "invalid command\n");
                return 1;
        }

        if (argc < cmdh->min_num_p) {
                fprintf(stderr, "not enough parameters\n");
                return 1;
        }

        /*
         * return value from handler (0=failure) will be used as exit code so need to do change it
         * here to have exit code 0 on success
         */
        return !cmdh->func(argc, argv);
}
