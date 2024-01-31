/**
 ****************************************************************************************
 *
 * @file programmer.c
 *
 * @brief Bootloader API.
 *
 * Copyright (C) 2015-2018 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
#include <sys/stat.h>
#include <uartboot_types.h>
#include <suota.h>

#include <programmer.h>

#include "gdb_server_cmds.h"
#include "protocol_cmds.h"
#include "serial.h"
#include "crc16.h"

/*
 * this is 'magic' address which can be used in some commands to indicate some kind of temporary
 * storage, i.e. command needs to store some data but does not care where as long as it can be
 * accessed later
 */
#define ADDRESS_TMP             (0xFFFFFFFF)
#define VIRTUAL_BUF_ADDRESS     (0x80000000)
#define OTP_START_ADDRESS       0x7F80000
#define OTP_SIZE                0x10000

/*
 * Address of chip revision register.
 */
#define CHIP_ID1_REG            0x50003200
#define CHIP_ID2_REG            0x50003201
#define CHIP_ID3_REG            0x50003202
#define CHIP_REVISION_REG       0x50003204
#define CHIP_TEST1_REG          0x5000320A

/*
 * Address of chip id in OTP header.
 */
#define OTP_HEADER_CHIP_ID      0x7F8EA20
#define OTP_HEADER_CHIP_ID_LEN  0x8

/*
 * Address of position/package in OTP header.
 */
#define OTP_HEADER_POS_PACK_INFO        0x7F8EA00
#define OTP_HEADER_POS_PACK_INFO_LEN    0x8

/*
 * Address of tester/timestamp in OTP header.
 */
#define OTP_HEADER_TESTER_TIME_INFO     0x7F8EA08
#define OTP_HEADER_TESTER_TIME_INFO_LEN 0x8

/*
 * Address of inverse asymmetric keys in OTP.
 */
#define OTP_INVERSE_ASYM_KEYS           0x7F8E5C0
#define OTP_INVERSE_ASYM_KEYS_LEN       0x100

/*
 * Address of asymmetric keys area in OTP.
 */
#define OTP_ASYM_KEYS_AREA              0x7F8E6C0
#define OTP_ASYM_KEYS_AREA_LEN          0x100

/*
 * Address of inverse symmetric keys in OTP.
 */
#define OTP_INVERSE_SYM_KEYS            0x7F8E7C0
#define OTP_INVERSE_SYM_KEYS_LEN        0x100

/*
 * Address of symmetric keys area in OTP.
 */
#define OTP_SYM_KEYS_AREA               0x7F8E8C0
#define OTP_SYM_KEYS_AREA_LEN           0x100

/*
 * Address of mirrored/cached at startup in OTP header.
 */
#define OTP_HEADER_MIRRORED_CACHED      0x7F8E9C0
#define OTP_HEADER_MIRRORED_CACHED_LEN  0x8

/*
 * Address of non-volatile memory in OTP header.
 */
#define OTP_HEADER_NON_VOLATILE_MEM     0x7F8E9C8
#define OTP_HEADER_NON_VOLATILE_MEM_LEN 0x8

/*
 * Address of mirror image length in OTP header.
 */
#define OTP_HEADER_IMAGE_LENGTH         0x7F8EA10
#define OTP_HEADER_IMAGE_LENGTH_LEN     0x8

/*
 * Address of image CRC in OTP header.
 */
#define OTP_HEADER_IMAGE_CRC            0x7F8EA38
#define OTP_HEADER_IMAGE_CRC_LEN        0x8

/*
 *
 * Max chunk size that can be transfered in one protocol command.
 */
#define MAX_CHUNK_SIZE  (0x2000)
#define FLASH_ERASE_MASK (MAX_CHUNK_SIZE - 1)

/*
 * Max bootloader size which can be just send to RAM (at 0 address)
 */
#define MAX_BOOTLOADER_SIZE             0x10000 // 64 KB

/*
 * Pointer will hold memory for bootloader code
 *
 */
static uint8_t *boot_loader = NULL;
static size_t boot_loader_size;

/*
 * Variables will hold the mode in which the dll operates
 *
 */
static bool gdb_gui_mode = false;
static bool block_otp_write = false;

/*
 *
 * buffers for gui mode
 */
#define STDOUT_BUF_SIZE	128
#define STDERR_BUF_SIZE	128
static char stdout_msg[STDOUT_BUF_SIZE];
static char stderr_msg[STDERR_BUF_SIZE];
static char copy_stdout_msg[STDOUT_BUF_SIZE];
static char copy_stderr_msg[STDERR_BUF_SIZE];

static unsigned int prog_intial_baudrate;
static unsigned int uartTimeoutInMs = 5000;
char *target_reset_cmd;

typedef struct {
        /**
         * \brief Close the target interface
         *
         * \note In the GDB Server interface case this is a selected process ID. In the serial
         * interface case this could be anything (currently not used).
         *
         * \param [in] data interface dependent data
         *
         */
        void (*close)(int data);

        /**
         * \brief Set the bootloader code which updates the firmware
         *
         * Binary data specified in this command will be sent to the device.
         *
         * \param [in] code binary data to send to first stage boot loader
         * \param [in] size code size
         *
         */
        void (*set_boot_loader_code)(uint8_t *code, size_t size);

        /**
         * \brief Get the bootloader code which updates the firmware
         *
         * \param [out] code binary data that will be sent to first stage boot loader
         * \param [out] size code size
         *
         */
        void (*get_boot_loader_code)(uint8_t **code, size_t * size);

        /**
         * \brief Read the device memory
         *
         * This function reads the device memory as seen by the device CPU.
         *
         * \param [out] buf buffer for data
         * \param [in]  size size of buf in bytes
         * \param [in]  addr device CPU address to read from
         *
         * \returns 0 on success, negative value with error code on failure
         *
         */
        int (*cmd_read)(uint8_t *buf, size_t size, uint32_t addr);

        /**
         * \brief Write the device memory
         *
         * This function writes the specified data to the device RAM.
         *
         * \param [in] buf binary data to send to device
         * \param [in] size size of buf
         * \param [in] addr device CPU address at device to write data to
         *
         * \returns 0 on success, negative value with error code on failure
         *
         */
        int (*cmd_write)(const uint8_t *buf, size_t size, uint32_t addr);

        /**
         * \brief Erase the QSPI flash region
         *
         * This function erases the flash at a specified offset.
         *
         * \param [in] address address in flash to start erase
         * \param [in] size size of memory to erase
         *
         * \returns 0 on success, negative value with error code on failure
         *
         */
        int (*cmd_erase_qspi)(uint32_t address, size_t size);

        /**
         * \brief Apply chip erase on QSPI
         *
         * This function erases the whole flash memory.
         *
         * \returns 0 on success, negative value with error code on failure
         *
         */
        int (*cmd_chip_erase_qspi)(void);

        /**
         * \brief Read data from QSPI
         *
         * \param [in] address offset in flash
         * \param [out] buf buffer for data
         * \param [in] len length of buffer
         *
         * \return 0 on success, error code on failure
         *
         */
        int (*cmd_read_qspi)(uint32_t address, uint8_t *buf, uint32_t len);

        /**
         * \brief Check emptiness of QSPI flash
         *
         * If specified flash region is empty, parameter \p ret_number is a number of checked bytes
         * (positive value). Otherwise if specified flash region contains values different than 0xFF,
         * parameter \p ret_number is a nonpositive value. This value is a number of first non 0xFF byte in
         * checked region multiplied by -1.
         *
         * \param [in]  size number of bytes to check
         * \param [in]  start_address start address in QSPI flash
         * \param [out] ret_number number of checked bytes, or number of first non 0xFF byte multiplied by -1
         *
         * \return 0 on success, error code on failure
         *
         */
        int (*cmd_is_empty_qspi)(unsigned int size, unsigned int start_address, int *ret_number);

        /**
         * \brief Read the partition table
         *
         * \param [out] buf buffer to store the contents of the partition table
         * \param [out] len the size of buffer in bytes
         *
         * \return 0 on success, error code on failure
         *
         */
        int (*cmd_read_partition_table)(uint8_t **buf, uint32_t *len);

        /**
         * \brief Read data from a specific partition
         *
         * \param [in] id partition id
         * \param [in] address offset in flash
         * \param [out] buf buffer for data
         * \param [in] len length of buffer
         *
         * \return 0 on success, error code on failure
         *
         */
        int (*cmd_read_partition)(nvms_partition_id_t id, uint32_t address, uint8_t *buf,
                                                                                uint32_t len);

        /**
         * \brief Write memory to NVMS partition
         *
         * This function programs NVMS partition memory with data already present in the device RAM.
         *
         * \param [in] id partition id
         * \param [in] dst_address offset in partition to write to
         * \param [in] src_address address in the device RAM
         * \param [in] size size of memory to copy
         *
         * \returns 0 on success, negative value with error code on failure
         *
         */
        int (*cmd_write_partition)(nvms_partition_id_t id, uint32_t dst_address,
                                                                uint32_t src_address, size_t size);

        /**
         * \brief Copy memory to QSPI flash
         *
         * This function programs QSPI flash memory with data already present in the device RAM.
         *
         * \param [in] src_address address in the device RAM
         * \param [in] size size of memory to copy
         * \param [in] dst_address offset in flash to write to
         *
         * \returns 0 on success, negative value with error code on failure
         *
         */
        int (*cmd_copy_to_qspi)(uint32_t src_address, size_t size, uint32_t dst_address);

        /**
         * \brief Read data from OTP
         *
         * \param [in] address address of 64-bit cell in the OTP
         * \param [out] buf buffer for read words
         * \param [in] len number of words to be read
         *
         * \return 0 on success, error code on failure
         *
         */
        int (*cmd_read_otp)(uint32_t address, uint32_t *buf, uint32_t len);

        /**
         * \brief Write data to OTP
         *
         * \param [in] address address of 64-bit cell in the OTP
         * \param [in] buf words to be written
         * \param [in] len number of words in buffer
         *
         * \return 0 on success, error code on failure
         *
         */
        int (*cmd_write_otp)(uint32_t address, const uint32_t *buf, uint32_t len);

        /**
         * \brief Execute code on the device
         *
         * This function starts execution of the code on the device.
         *
         * \param [in] address address in device RAM to execute
         *
         * \returns 0 on success, negative value with error code on failure
         *
         */
        int (*cmd_run)(uint32_t address);

        /**
         * \brief Boot arbitrary binary.
         *
         * This function boots the device with a provided application binary.
         *
         * \returns 0 on success, negative value with error code on failure
         *
         */
        int (*cmd_boot) (void);
} target_interface_t;

static const target_interface_t target_serial = {
        /* .close_interface = */                prog_serial_close,
        /* .set_boot_loader_code = */           set_boot_loader_code,
        /* .get_boot_loader_code = */           get_boot_loader_code,
        /* .cmd_read = */                       protocol_cmd_read,
        /* .cmd_write = */                      protocol_cmd_write,
        /* .cmd_erase_qspi = */                 protocol_cmd_erase_qspi,
        /* .cmd_chip_erase_qspi = */            protocol_cmd_chip_erase_qspi,
        /* .cmd_read_qspi = */                  protocol_cmd_read_qspi,
        /* .cmd_is_empty_qspi = */              protocol_cmd_is_empty_qspi,
        /* .cmd_read_partition_table = */       protocol_cmd_read_partition_table,
        /* .cmd_read_partition = */             protocol_cmd_read_partition,
        /* .cmd_write_partition = */            protocol_cmd_write_partition,
        /* .cmd_copy_to_qspi = */               protocol_cmd_copy_to_qspi,
        /* .cmd_read_otp = */                   protocol_cmd_read_otp,
        /* .cmd_write_otp = */                  protocol_cmd_write_otp,
        /* .cmd_run = */                        protocol_cmd_run,
        /* .cmd_boot = */                       protocol_cmd_boot,
};

static const target_interface_t target_gdb_server = {
        /* .close_interface = */                gdb_server_close,
        /* .set_boot_loader_code = */           gdb_server_set_boot_loader_code,
        /* .get_boot_loader_code = */           gdb_server_get_boot_loader_code,
        /* .cmd_read = */                       gdb_server_cmd_read,
        /* .cmd_write = */                      gdb_server_cmd_write,
        /* .cmd_erase_qspi = */                 gdb_server_cmd_erase_qspi,
        /* .cmd_chip_erase_qspi = */            gdb_server_cmd_chip_erase_qspi,
        /* .cmd_read_qspi = */                  gdb_server_cmd_read_qspi,
        /* .cmd_is_empty_qspi = */              gdb_server_cmd_is_empty_qspi,
        /* .cmd_read_partition_table = */       gdb_server_cmd_read_partition_table,
        /* .cmd_read_partition = */             gdb_server_cmd_read_partition,
        /* .cmd_write_partition = */            gdb_server_cmd_write_partition,
        /* .cmd_copy_to_qspi = */               gdb_server_cmd_copy_to_qspi,
        /* .cmd_read_otp = */                   gdb_server_cmd_read_otp,
        /* .cmd_write_otp = */                  gdb_server_cmd_write_otp,
        /* .cmd_run = */                        gdb_server_cmd_run,
        /* .cmd_boot = */                       gdb_server_cmd_boot,
};

/* Selected target interface is now serial port protocol */
static const target_interface_t *target = &target_serial;

void prog_set_initial_baudrate(unsigned int initial_baudrate)
{
        prog_intial_baudrate = initial_baudrate;
}

unsigned int prog_get_initial_baudrate(void)
{
        return prog_intial_baudrate;
}

int prog_serial_open(const char *port, int baudrate)
{
        int ret;

        ret = serial_open(port, baudrate);
        if (!ret) {
                return ERR_FILE_OPEN;
        }
        target = &target_serial;

        return 0;
}

void prog_serial_close(int data)
{
        (void) data;

        serial_close();
}

void prog_gdb_close(int pid)
{
        gdb_server_close(pid);
}

void prog_set_uart_boot_loader(uint8_t *buf, uint32_t size)
{
        target->set_boot_loader_code(buf, size);
}

int prog_set_uart_boot_loader_from_file(const char *file_name)
{
        FILE *f;
        struct stat st;
        int err = 0;

        if (file_name == NULL || stat(file_name, &st) < 0) {
                return ERR_FILE_OPEN;
        }

        f = fopen(file_name, "rb");
        if (f == NULL) {
                return ERR_FILE_OPEN;
        }

        boot_loader = realloc(boot_loader, st.st_size);
        if (boot_loader == NULL) {
                err = ERR_ALLOC_FAILED;
                goto end;
        }

        if (st.st_size != fread(boot_loader, 1, st.st_size, f)) {
                err = ERR_FILE_READ;
                goto end;
        }

        if (st.st_size >= MAX_BOOTLOADER_SIZE) {
                boot_loader_size = st.st_size;

                err = ERR_FILE_TOO_BIG;
                goto end;
        }

        target->set_boot_loader_code(boot_loader, st.st_size);
end:
        if (f != NULL) {
                fclose(f);
        }

        return err;
}

static void print_log(char buf_msg[], const char *msg, va_list *args)
{
        if (gdb_gui_mode) {
                vsprintf(buf_msg, msg, *args);
        } else {
                FILE *to = (buf_msg == stderr_msg) ? stderr : stdout;

                vfprintf(to, msg, *args);
                fflush(to);
        }
}

void prog_print_log(const char *msg, ...)
{
        va_list args;
        va_start(args, msg);

        print_log(stdout_msg, msg, &args);
        va_end(args);
}

void prog_print_err(const char *msg, ...)
{
        va_list args;
        va_start(args, msg);

        print_log(stderr_msg, msg, &args);
        va_end(args);
}

int prog_write_to_ram(uint32_t ram_address, const uint8_t *buf, uint32_t size)
{
        const uint8_t MAX_RETRY_COUNT = 10;
        int err = 0;
        uint32_t offset = 0;
        uint8_t retry_cnt = 0;

        while (offset < size) {
                uint32_t chunk_size = size - offset;

                if (retry_cnt > MAX_RETRY_COUNT) {
                        prog_print_err("Write to RAM failed. Abort.\r\n");
                        return err;
                }

                if (chunk_size > MAX_CHUNK_SIZE) {
                        chunk_size = MAX_CHUNK_SIZE;
                }

                prog_print_log("Writing to address: 0x%08x offset: 0x%08x chunk size: 0x%08x\n",
                                                                ram_address, offset, chunk_size);

                err = target->cmd_write(buf + offset, chunk_size, ram_address + offset);
                if (err != 0) {
                        prog_print_log("Verify writing to RAM address 0x%x failed (%d). "
                                                "Retrying ...\n", ram_address + offset, err);
                        retry_cnt++;
                        continue;
                }

                retry_cnt = 0;
                offset += chunk_size;
        }

        return err;
}

int prog_write_file_to_ram(uint32_t ram_address, const char *file_name, uint32_t size)
{
        int err = 0;
        uint8_t *buf = NULL;
        FILE *f = NULL;

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
        err = prog_write_to_ram(ram_address, buf, size);
end:
        if (f) {
                fclose(f);
        }
        if (buf != NULL) {
                free(buf);
        }
        return err;
}

int prog_write_to_qspi(uint32_t flash_address, const uint8_t *buf, uint32_t size)
{
        int err = 0;
        uint32_t offset = 0;
        uint8_t retry_cnt = 0;

        while (offset < size) {
                uint32_t chunk_size = size - offset;

                if (retry_cnt > 10) {
                        err = ERR_PROG_QSPI_WRITE;
                        prog_print_err("Write to qspi failed. Abort. \n");
                        goto done;
                }

                if (chunk_size > MAX_CHUNK_SIZE) {
                        chunk_size = MAX_CHUNK_SIZE;
                }
                /*
                 * Modify chunk size if write would not start at the beginning of sector.
                 */
                if (((flash_address + offset) & FLASH_ERASE_MASK) + chunk_size > MAX_CHUNK_SIZE) {
                        chunk_size = MAX_CHUNK_SIZE - ((flash_address + offset) & FLASH_ERASE_MASK);
                }
                err = target->cmd_write(buf + offset, chunk_size, ADDRESS_TMP);
                if (err != 0) {
                        goto done;
                }

                prog_print_log("Writing to address: 0x%08x offset: 0x%08x chunk size: 0x%08x\n",
                                                                flash_address, offset, chunk_size);

                err = target->cmd_copy_to_qspi(ADDRESS_TMP, chunk_size, flash_address + offset);

                if (err != 0) {
                        prog_print_log("Verify writing to qspi address 0x%x failed. Retrying ...\n",
                                                                        flash_address + offset);
                        retry_cnt++;
                        continue;
                }
                retry_cnt = 0;
                offset += chunk_size;
        }

done:
        return err;
}

int prog_write_file_to_qspi(uint32_t flash_address, const char *file_name, uint32_t size)
{
        int err = 0;
        uint8_t *buf = NULL;
        FILE *f = NULL;
        bool flash_binary = false;

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

        if (flash_address == 0 && !memcmp(buf, "qQ", 2)) {
                memset(buf, 0xFF, 2);
                flash_binary = true;
        }

        err = prog_write_to_qspi(flash_address, buf, size);
end:
        if (f) {
                fclose(f);
        }

        if (buf != NULL) {
                free(buf);
        }

        if (!err && flash_binary) {
                /*
                 * Writing "qQ" on old 0xFF values does not trigger flash erasing in uartboot, so
                 * the rest of bytes in this sector will not be erased.
                 */
                err = prog_write_to_qspi(0, (const uint8_t *) "qQ", 2);
        }

        return err;
}

int prog_erase_qspi(uint32_t flashAddress, uint32_t size)
{
        return target->cmd_erase_qspi(flashAddress, size);
}

int prog_read_memory(uint32_t mem_address, uint8_t *buf, uint32_t size)
{
        const uint8_t MAX_RETRY_COUNT = 10;
        int err = 0;
        uint32_t offset = 0;
        uint8_t retry_cnt = 0;

        while (offset < size) {
                uint32_t chunk_size = size - offset;

                if (retry_cnt > MAX_RETRY_COUNT) {
                        prog_print_err("Read from RAM failed. Abort.\r\n");
                        return err;
                }

                if (chunk_size > MAX_CHUNK_SIZE) {
                        chunk_size = MAX_CHUNK_SIZE;
                }

                prog_print_log("Reading from address: 0x%08x offset: 0x%08x chunk size: 0x%08x\n",
                                                                mem_address, offset, chunk_size);

                err = target->cmd_read(buf + offset, chunk_size, mem_address + offset);
                if (err != 0) {
                        prog_print_log("Verify reading from RAM address 0x%x failed (%d). "
                                                "Retrying ...\n", mem_address + offset, err);
                        retry_cnt++;
                        continue;
                }

                retry_cnt = 0;
                offset += chunk_size;
        }

        return err;
}

int prog_read_memory_to_file(uint32_t mem_address, const char *file_name, uint32_t size)
{
        int err = 0;
        uint8_t *buf = NULL;
        FILE *f = NULL;

        f = fopen(file_name, "wb");
        if (f == NULL) {
                err = ERR_FILE_OPEN;
                goto end;
        }

        buf = (uint8_t*) malloc(size);
        if (buf == NULL) {
                err = ERR_ALLOC_FAILED;
                goto end;
        }
        err = prog_read_memory(mem_address, buf, size);
        if (err < 0) {
                goto end;
        }
        fwrite(buf, 1, size, f);
end:
        if (f) {
                fclose(f);
        }
        if (buf != NULL) {
                free(buf);
        }
        return err;
}

int prog_run(uint32_t mem_address)
{
        return target->cmd_run(mem_address);
}

int prog_copy_to_qspi(uint32_t mem_address, uint32_t flash_address, uint32_t size)
{
        return target->cmd_copy_to_qspi(mem_address, size, flash_address);
}

int prog_chip_erase_qspi(void)
{
        return target->cmd_chip_erase_qspi();
}

int prog_write_file_to_otp(uint32_t otp_address, const char *file_name, uint32_t size)
{
        int err = 0;
        uint8_t *buf = NULL;
        FILE *f = NULL;
        uint32_t write_size;
        int i;

        if (size > OTP_SIZE) {
                return ERR_PROG_INVALID_ARGUMENT;
        }

        f = fopen(file_name, "rb");
        if (!f) {
                return ERR_FILE_OPEN;
        }

        write_size = (size % 4) ? (size + 4 - (size % 4)) : size;

        buf = (uint8_t *) malloc(write_size);
        if (buf == NULL) {
                return ERR_ALLOC_FAILED;
        }

        /* Set last bytes to zero (if exists) - this is faster than memset on large block of memory */
        for (i = size; i < write_size; i++) {
                buf[i] = 0;
        }

        if (fread(buf, 1, size, f) != size) {
                free(buf);
                return ERR_FILE_READ;
        }

        fclose(f);

        /* Length of data is a number of 32-bits words, so it must be divided by 4 */
        err = prog_write_otp(otp_address, (const uint32_t *) buf, (write_size >> 2));

        free(buf);

        return err;
}

int prog_write_otp(uint32_t address, const uint32_t *buf, uint32_t len)
{
        int err = 0;
        unsigned int i;
        uint32_t *read_buf = NULL;
        bool otp_same = true;
        bool otp_addr_not_empty = false;

        /*Check if OTP address is empty*/
        read_buf = (uint32_t*) malloc(len * sizeof(uint32_t));
        if (read_buf == NULL) {
                err = ERR_ALLOC_FAILED;
                goto done;
        }

        err = target->cmd_read_otp(address, read_buf, len);
        if (err != 0) {
                goto done;
        }

        if (block_otp_write) {
                for (i = 0; i < len; i += 2) {
                        if (buf[i] || buf[i + 1]) {
                                if (buf[i] != read_buf[i] ||
                                        buf[i + 1] != read_buf[i + 1]) {
                                        otp_same = false;

                                        if (read_buf[i] || read_buf[i + 1]) {
                                                otp_addr_not_empty = true;
                                                break;
                                        }
                                }
                        }
                }

                if (otp_same) {
                        err = ERR_PROG_OTP_SAME;
                        goto done;
                }

                if (otp_addr_not_empty) {
                        err = ERR_PROG_OTP_NOT_EMPTY;
                        prog_print_err("Otp address 0x%x not empty...\n",
                                                (OTP_START_ADDRESS + (address * 8 + i * 4)));
                        goto done;
                }

                /*Write to OTP address*/
                err = target->cmd_write_otp(address, buf, len);
                if (err != 0) {
                        goto done;
                }

                /*Read back and verify*/
                err = target->cmd_read_otp(address, read_buf, len);
                if (err != 0) {
                        goto done;
                }

                /* Now make 64 bit entries in read_buf zero, where buf also contains zero's */
                for (i = 0; i < len; i += 2) {
                        if ((buf[i] == 0) && (buf[i + 1]) == 0) {// corresponding places in buf not zero
                                read_buf[i] = 0;
                                read_buf[i + 1] = 0;
                        }
                }

                err = memcmp(read_buf, buf, len * sizeof(*buf));

                if (err != 0) {
                        err = ERR_PROG_OTP_VERIFY;
                        prog_print_err("Verify writing to otp address 0x%x failed ...\n",
                                                (OTP_START_ADDRESS + (address * 8 + i * 4)));
                        goto done;
                }
        } else {
                for (i = 0; i < len; i++) {
                        if (buf[i] != read_buf[i]) {
                                otp_same = false;

                                if (read_buf[i]) {
                                        otp_addr_not_empty = true;
                                        break;
                                }
                        }
                }

                if (otp_same) {
                        err = ERR_PROG_OTP_SAME;
                        goto done;
                }

                if (otp_addr_not_empty) {
                        err = ERR_PROG_OTP_NOT_EMPTY;
                        prog_print_err("Otp address 0x%x not empty...\n",
                                                (OTP_START_ADDRESS + (address * 8 + i * 4)));
                        goto done;
                }

                /*Write to OTP address*/
                err = target->cmd_write_otp(address, buf, len);
                if (err != 0) {
                        goto done;
                }

                /*Read back and verify*/
                err = target->cmd_read_otp(address, read_buf, len);
                if (err != 0) {
                        goto done;
                }

                err = memcmp(read_buf, buf, len * sizeof(*buf));
                if (err != 0) {
                        err = ERR_PROG_OTP_VERIFY;
                        prog_print_err("Verify writing to otp address 0x%x failed ...\n",
                                                (OTP_START_ADDRESS + (address * 8 + i * 4)));
                        goto done;
                }
        }

done:
        if (read_buf) {
                free(read_buf);
        }
        return err;
}

int prog_read_otp(uint32_t address, uint32_t *buf, uint32_t len)
{
        return target->cmd_read_otp(address, buf, len);
}

int prog_write_image_to_otp(const uint8_t *buf, uint32_t len, image_mode_t mode)
{
        const uint32_t mirrored_cached = (mode == IMG_MIRRORED ? 0 : 1);
        const uint32_t non_volatile_otp = 1;
        uint32_t word_length = (len >> 2);
        uint32_t crc;
        int err;

        if (len % 4) {
                /* Buffer must be aligned to 4-bytes */
                return ERR_PROG_INSUFICIENT_BUFFER;
        }

        /* Calculate CRC-16 for given image */
        crc = crc16_calculate(buf, len);

        err = target->cmd_write_otp(0, (uint32_t *) buf, word_length);

        if (err != 0) {
                return err;
        }

        if (mirrored_cached != 0) {
                /* Write only low word to the OTP header fields */
                err = target->cmd_write_otp((OTP_HEADER_MIRRORED_CACHED & ~OTP_START_ADDRESS) >> 3,
                                                                                &mirrored_cached, 1);

                if (err != 0) {
                        return err;
                }
        }

        err = target->cmd_write_otp((OTP_HEADER_NON_VOLATILE_MEM & ~OTP_START_ADDRESS) >> 3,
                                                                        &non_volatile_otp, 1);

        if (err != 0) {
                return err;
        }

        err = target->cmd_write_otp((OTP_HEADER_IMAGE_LENGTH & ~OTP_START_ADDRESS) >> 3,
                                                                                &word_length, 1);

        if (err != 0) {
                return err;
        }

        return target->cmd_write_otp((OTP_HEADER_IMAGE_CRC & ~OTP_START_ADDRESS) >> 3, &crc, 1);
}

int prog_write_tcs(uint32_t *address, const uint32_t *buf, uint32_t len)
{
        int err = 0;
        unsigned int i;
        uint32_t *read_buf;

        *address = 0;		//addr of 64bit words
        /*Find empty section in OTP*/
        //Allocate buffer
        read_buf = calloc(TCS_WORD_SIZE, sizeof(*read_buf));
        if (read_buf == NULL) {
                err = ERR_ALLOC_FAILED;
                goto done;
        }
        //Read TCS
        err = target->cmd_read_otp(TCS_ADDR, read_buf, TCS_WORD_SIZE);
        if (err != 0) {
                err = ERR_PROG_OTP_READ;
                prog_print_err("Read from OTP failed...\n");
                goto done_and_free;
        }

        //Check for empty TCS section
        while (*address <= ( TCS_WORD_SIZE - len) >> 1) {
                i = 0;
                while (i < len >> 1 && !((uint64_t*) read_buf)[*address + i]) {
                        i++;
                }
                if (i < len >> 1) {
                        *address += i + 1;
                } else {
                        break;
                }
        }

        if (*address > ( TCS_WORD_SIZE - len) >> 1) {
                err = ERR_PROG_OTP_NOT_EMPTY;
                prog_print_err("not enough empty space in TCS\n");
                return 0;
        }
        *address += TCS_ADDR;

        /*Write OTP*/
        err = target->cmd_write_otp(*address, buf, len);

done_and_free:
        free(read_buf);

done:
        return err;
}

int prog_read_qspi(uint32_t address, uint8_t *buf, uint32_t len)
{
        uint32_t offset = 0;
        int err = 0;

        while (err == 0 && offset < len) {
                uint32_t chunk_size = len - offset;
                if (chunk_size > MAX_CHUNK_SIZE) {
                        chunk_size = MAX_CHUNK_SIZE;
                }
                err = target->cmd_read_qspi(address + offset, buf + offset, chunk_size);
                offset += chunk_size;
        }
        return err;
}

int prog_read_qspi_to_file(uint32_t address, const char *fname, uint32_t len)
{
        int err = 0;
        uint8_t *buf = NULL;
        FILE *f = NULL;

        f = fopen(fname, "wb");
        if (f == NULL) {
                err = ERR_FILE_OPEN;
                goto end;
        }

        buf = (uint8_t*) malloc(len);
        if (buf == NULL) {
                err = ERR_ALLOC_FAILED;
                goto end;
        }

        err = prog_read_qspi(address, buf, len);
        if (err < 0) {
                goto end;
        }

        fwrite(buf, 1, len, f);

end:
        if (f) {
                fclose(f);
        }

        free(buf);

        return err;
}

int prog_is_empty_qspi(unsigned int size, unsigned int start_address, int *ret_number)
{
        return target->cmd_is_empty_qspi(size, start_address, ret_number);
}

int prog_read_partition_table(uint8_t **buf, uint32_t *len)
{
        return target->cmd_read_partition_table(buf, len);
}

int prog_read_partition(nvms_partition_id_t id, uint32_t address, uint8_t *buf, uint32_t len)
{
        uint32_t offset = 0;
        int err = 0;

        while (err == 0 && offset < len) {
                uint32_t chunk_size = len - offset;
                if (chunk_size > MAX_CHUNK_SIZE) {
                        chunk_size = MAX_CHUNK_SIZE;
                }
                err = target->cmd_read_partition(id, address + offset, buf + offset, chunk_size);
                offset += chunk_size;
        }

        return err;
}

int prog_read_patrition_to_file(nvms_partition_id_t id, uint32_t address, const char *fname,
                                                                                uint32_t len)
{
        int err = 0;
        uint8_t *buf = NULL;
        FILE *f = NULL;

        f = fopen(fname, "wb");
        if (f == NULL) {
                err = ERR_FILE_OPEN;
                goto end;
        }

        buf = (uint8_t*) malloc(len);
        if (buf == NULL) {
                err = ERR_ALLOC_FAILED;
                goto end;
        }

        err = prog_read_partition(id, address, buf, len);
        if (err < 0) {
                goto end;
        }

        if (fwrite(buf, 1, len, f) != len) {
                err = ERR_FILE_WRITE;
        }

end:
        if (f) {
                fclose(f);
        }

        free(buf);

        return err;
}

int prog_write_partition(nvms_partition_id_t id, uint32_t part_address, const uint8_t *buf,
                                                                                uint32_t size)
{
        int err = 0;
        uint32_t offset = 0;
        uint8_t retry_cnt = 0;

        while (offset < size) {
                uint32_t chunk_size = size - offset;
                uint8_t read_buf[MAX_CHUNK_SIZE];

                if (retry_cnt > 10) {
                        err = ERR_PROG_QSPI_WRITE;
                        prog_print_err("Write to partition failed. Abort.\n");
                        break;
                }

                if (chunk_size > MAX_CHUNK_SIZE) {
                        chunk_size = MAX_CHUNK_SIZE;
                }
                /*
                 * Modify chunk size if write would not start at the beginning of sector.
                 */
                if (((part_address + offset) & FLASH_ERASE_MASK) + chunk_size > MAX_CHUNK_SIZE) {
                        chunk_size = MAX_CHUNK_SIZE - ((part_address + offset) & FLASH_ERASE_MASK);
                }

                err = target->cmd_write(buf + offset, chunk_size, ADDRESS_TMP);
                if (err != 0) {
                        break;
                }

                prog_print_log("Writing to address: 0x%08x offset: 0x%08x "
                                        "chunk size: 0x%08x\n", part_address, offset, chunk_size);

                err = target->cmd_write_partition(id, part_address + offset, ADDRESS_TMP,
                                                                                chunk_size);
                if (err != 0) {
                        break;
                }

                /*Verify write*/
                err = prog_read_partition(id, part_address + offset, read_buf, chunk_size);
                if (err != 0) {
                        break;
                }

                err = memcmp(read_buf, buf + offset, chunk_size);
                if (err != 0) {
                        prog_print_log("Verify writing to qspi address 0x%x failed."
                                                        "Retrying ...\n", part_address + offset);
                        retry_cnt++;
                        continue;
                }
                retry_cnt = 0;
                offset += chunk_size;
        }

        return err;
}

int prog_write_file_to_partition(nvms_partition_id_t id, uint32_t part_address,
                                                        const char *file_name, uint32_t size)
{
        int err = 0;
        uint8_t *buf = NULL;
        FILE *f = NULL;

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

        err = prog_write_partition(id, part_address, buf, size);
end:
        if (f) {
                fclose(f);
        }

        if (buf != NULL) {
                free(buf);
        }

        return err;
}

int prog_boot(void)
{
        int err;
        err = target->cmd_boot();
        if (err < 0) {
                return err;
        }

        if (!boot_loader_size) {
                return 0;
        }

        err = prog_write_to_ram(VIRTUAL_BUF_ADDRESS, boot_loader, boot_loader_size);
        if (err < 0) {
                return err;
        }

        return prog_run(VIRTUAL_BUF_ADDRESS);
}

const char* prog_get_err_message(int err_int)
{
        switch (err_int) {
        case ERR_FAILED:
                return "general error";
        case ERR_ALLOC_FAILED:
                return "memory allocation failed";
        case ERR_FILE_OPEN:
                return "file cannot be opened";
        case ERR_FILE_READ:
                return "file cannot be read";
        case ERR_FILE_PATCH:
                return "secondary boot loader cannot be patched";
        case ERR_FILE_WRITE:
                return "file cannot be written";
        case ERR_FILE_CLOSE:
                return "file cannot be closed";
        case ERR_PROT_NO_RESPONSE:
                return "timeout waiting for response";
        case ERR_PROT_CMD_REJECTED:
                return "NAK received when waiting for ACK";
        case ERR_PROT_INVALID_RESPONSE:
                return "invalid data received when waiting for ACK";
        case ERR_PROT_CRC_MISMATCH:
                return "CRC16 mismatch";
        case ERR_PROT_CHECKSUM_MISMATCH:
                return "checksum mismatch while uploading 2nd stage bootloader";
        case ERR_PROT_BOOT_LOADER_REJECTED:
                return "2nd stage bootloader rejected";
        case ERR_PROT_UNKNOWN_RESPONSE:
                return "invalid announcement message received";
        case ERR_PROT_TRANSMISSION_ERROR:
                return "failed to transmit data";
        case ERR_PROT_COMMAND_ERROR:
                return "error executing command";
        case ERR_PROT_UNSUPPORTED_VERSION:
                return "unsupported bootloader version";
        case ERR_GDB_SERVER_SOCKET:
                return "communication with GDB Server socket failed";
        case ERR_GDB_SERVER_CRC_MISMATCH:
                return "checksum mismatch";
        case ERR_GDB_SERVER_CMD_REJECTED:
                return "NAK received when waiting for ACK";
        case ERR_GDB_SERVER_INVALID_RESPONSE:
                return "invalid data received from GDB Server";
        case ERR_PROG_OTP_SAME:
                return "Data written to OTP match data to be written";
        case ERR_PROG_QSPI_IMAGE_FORMAT:
                return "invalid image format";
        case ERR_PROG_UNKNOW_CHIP:
                return "can't read chip revision";
        case ERR_PROG_NO_PARTITON:
                return "required partition not found";
        case ERR_PROG_UNKNOWN_PRODUCT_ID:
                return "Unknown product id";
        case ERR_PROG_INSUFICIENT_BUFFER:
                return "Insufficient memory buffer";
        case ERR_PROG_INVALID_ARGUMENT:
                return "Invalid argument";

        case MSG_FROM_STDOUT:
                strcpy(copy_stdout_msg, stdout_msg);
                stdout_msg[0] = 0;
                return (const char*) copy_stdout_msg;
        case MSG_FROM_STDERR:
                strcpy(copy_stderr_msg, stderr_msg);
                stderr_msg[0] = 0;
                return (const char*) copy_stderr_msg;

        default:
                return "unknown error";

        }

}

static void prog_uartboot_patch_write_value(uint8_t * code, int offset, unsigned int value)
{
        uint8_t * pos;
        int i;
        pos = code + offset;
        /* Write value ensuring little-endianess. */
        for (i = 0; i < 4; i++) {
                *pos++ = (uint8_t) value & 0xff;
                value >>= 8;
        }
}

int prog_uartboot_patch_config(const prog_uartboot_config_t * uartboot_config)
{
        uint8_t * code;
        size_t size;
        get_boot_loader_code(&code, &size);
        if (code == NULL) {
                return ERR_FILE_PATCH;
        }
        /* Check size. */
        if (size < PROGRAMMER_PATCH_OFFSET_MAX + 4) {
                return ERR_FILE_PATCH;
        }
        if (uartboot_config->baudrate_patch) {
                prog_uartboot_patch_write_value(code, PROGRAMMER_PATCH_OFFSET_BAUDRATE,
                        uartboot_config->baudrate);
        }
        if (uartboot_config->tx_port_patch) {
                prog_uartboot_patch_write_value(code, PROGRAMMER_PATCH_OFFSET_TX_PORT,
                        uartboot_config->tx_port);
        }
        if (uartboot_config->tx_pin_patch) {
                prog_uartboot_patch_write_value(code, PROGRAMMER_PATCH_OFFSET_TX_PIN,
                        uartboot_config->tx_pin);
        }
        if (uartboot_config->rx_port_patch) {
                prog_uartboot_patch_write_value(code, PROGRAMMER_PATCH_OFFSET_RX_PORT,
                        uartboot_config->rx_port);
        }
        if (uartboot_config->rx_pin_patch) {
                prog_uartboot_patch_write_value(code, PROGRAMMER_PATCH_OFFSET_RX_PIN,
                        uartboot_config->rx_pin);
        }
        return 0;
}

void prog_close_interface(int data)
{
        if (target) {
                target->close(data);
        }
}

int DLLEXPORT prog_gdb_open(const prog_gdb_server_config_t *gdb_server_conf)
{
        target = &target_gdb_server;

        return gdb_server_initialization(gdb_server_conf);
}

int DLLEXPORT prog_gdb_mode(int mode)
{
        int rw = 0;
        if (mode & 0xfffffff8) { // no valid bits adressed
                rw = ERR_FAILED;
        } else {
                if (mode & GDB_MODE_GUI) {
                        gdb_gui_mode = true;
                        stdout_msg[0] = 0;	// empty last known stdout msg buffer
                        stderr_msg[0] = 0;	// empty last known stderr msg buffer
                        if (mode & GDB_MODE_INVALIDATE_STUB) {	// Invalidate downloaded stub
                                gdb_invalidate_stub();
                        }
                } else {
                        gdb_gui_mode = false;
                }
                if (mode & GDB_MODE_BLOCK_WRITE_OTP) {
                        block_otp_write = true;
                } else {
                        block_otp_write = false;
                }
        }
        return rw;
}

void prog_set_uart_timeout(unsigned int timeoutInMs)
{
        uartTimeoutInMs = timeoutInMs;
}

unsigned int get_uart_timeout(void)
{
        return uartTimeoutInMs;
}

int prog_read_chip_info(chip_info_t *chip_info)
{
        const uint32_t id_regs[5] = {
                CHIP_ID1_REG, CHIP_ID2_REG, CHIP_ID3_REG, CHIP_REVISION_REG, CHIP_TEST1_REG
        };
        uint8_t id[5] = { 0 };
        uint32_t chip_otp_id[OTP_HEADER_CHIP_ID_LEN >> 2] = { 0 };
        uint32_t chip_package[OTP_HEADER_POS_PACK_INFO_LEN >> 2] = { 0 };
        int i;
        int err = 0;

        /* Read chip revision */
        for (i = 0; err == 0 && i < sizeof(id); ++i) {
                err = prog_read_memory(id_regs[i], &id[i], 1);
        }
        if (err) {
                return err;
        }

        /* Read chip id as stored in otp */
        err = target->cmd_read_otp(((OTP_HEADER_CHIP_ID & ~OTP_START_ADDRESS) >> 3), chip_otp_id,
        OTP_HEADER_CHIP_ID_LEN >> 2);
        if (err) {
                return err;
        }

        /* Read package info*/
        err = target->cmd_read_otp(((OTP_HEADER_POS_PACK_INFO & ~OTP_START_ADDRESS) >> 3),
                chip_package, OTP_HEADER_POS_PACK_INFO_LEN >> 2);
        if (err) {
                return err;
        }

        /* Copy info to output buffer*/
        /* Chip revision */
        chip_info->chip_rev[0] = id[0];
        chip_info->chip_rev[1] = id[1];
        chip_info->chip_rev[2] = id[2];
        chip_info->chip_rev[3] = id[3];
        chip_info->chip_rev[4] = id[4] + 'A';
        chip_info->chip_rev[5] = '\0';

        /* Chip otp id*/
        for (i = 0; i < OTP_HEADER_CHIP_ID_LEN; i++) {
                chip_info->chip_otp_id[i] = *(((char*) chip_otp_id) + i);
        }
        chip_info->chip_otp_id[i] = '\0';

        /* Chip package info */
        if (*(((char*) chip_package) + 3) == 0x00) {
                strncpy(chip_info->chip_package, "WLCSP ", CHIP_PACKAGE_LEN);
        }
        else if (*(((char*) chip_package) + 3) == 0x55) {
                strncpy(chip_info->chip_package, "aQFN60", CHIP_PACKAGE_LEN);
        }

        return err;

}

int prog_read_unique_device_id(uint8_t *udi)
{
        int err = 0;
        uint32_t cell_address;
        uint32_t length;
        uint32_t *udi_32 = (uint32_t *) udi;

        memset(udi, 0, UNIQUE_DEVICE_ID_SIZE);
        cell_address = (OTP_HEADER_POS_PACK_INFO & ~OTP_START_ADDRESS) >> 3;
        length = OTP_HEADER_POS_PACK_INFO_LEN >> 2;

        err = target->cmd_read_otp(cell_address, udi_32, length);

        if (err) {
                return err;
        }

        cell_address = (OTP_HEADER_TESTER_TIME_INFO & ~OTP_START_ADDRESS) >> 3;
        length = OTP_HEADER_TESTER_TIME_INFO_LEN >> 2;

        err = target->cmd_read_otp(cell_address, udi_32 + (OTP_HEADER_POS_PACK_INFO_LEN >> 2), length);

        return err;
}

/* Key type basic informations */
typedef struct {
        /* Maximum index */
        int max_idx;
        /* Minimal length */
        int min_len;
        /* Maximal length */
        int max_len;
        /* Start address in OTP of keys area */
        uint32_t keys_area_base_address;
        /* Start address in OTP of inverse keys area */
        uint32_t inverse_keys_area_base_address;
} key_info_t;

/* Basic information for symmetric keys */
static const key_info_t symmetric_key = {
        SYMMETRIC_KEY_MAX_IDX,
        SYMMETRIC_KEY_LEN,
        SYMMETRIC_KEY_LEN,
        OTP_SYM_KEYS_AREA,
        OTP_INVERSE_SYM_KEYS,
};

/* Basic information for asymmetric keys */
static const key_info_t asymmetric_key = {
        ASYMMETRIC_KEY_MAX_IDX,
        ASYMMETRIC_KEY_MIN_LEN,
        ASYMMETRIC_KEY_MAX_LEN,
        OTP_ASYM_KEYS_AREA,
        OTP_INVERSE_ASYM_KEYS,
};

int prog_write_key(key_type_t type, int key_idx, const uint8_t *key, unsigned int key_len)
{
        const key_info_t info = (type == KEY_TYPE_SYMMETRIC) ? symmetric_key : asymmetric_key;
        int i;
        int err = 0;
        uint8_t inverse_key[ASYMMETRIC_KEY_MAX_LEN];
        uint32_t key_address;
        uint32_t inverse_key_address = { 0 };

        if (!key) {
                return ERR_PROG_INVALID_ARGUMENT;
        }

        if (key_idx < 0 || key_idx > info.max_idx) {
                return ERR_PROG_INVALID_ARGUMENT;
        }

        if (key_len < info.min_len || key_len > info.max_len) {
                return ERR_PROG_INVALID_ARGUMENT;
        }

        key_address = info.keys_area_base_address + info.max_len * key_idx;
        /* Translate to the 64-bit cell address */
        key_address = (key_address & ~OTP_START_ADDRESS) >> 3;
        inverse_key_address = info.inverse_keys_area_base_address + info.max_len * key_idx;
        inverse_key_address = (inverse_key_address & ~OTP_START_ADDRESS) >> 3;

        for (i = 0; i < key_len; i++) {
                inverse_key[i] = ~key[i];
        }

        err = prog_write_otp(key_address, (uint32_t *) key, (key_len >> 2));

        if (err) {
                return err;
        }

        err = prog_write_otp(inverse_key_address, (uint32_t *) inverse_key, (key_len >> 2));

        return err;
}

int prog_read_key(key_type_t type, int key_idx, uint8_t *key, unsigned int *key_len, bool *valid)
{
        const key_info_t info = (type == KEY_TYPE_SYMMETRIC) ? symmetric_key : asymmetric_key;
        int i;
        int err = 0;
        uint8_t key_cp[ASYMMETRIC_KEY_MAX_LEN] = { 0 };
        uint8_t inverse_key[ASYMMETRIC_KEY_MAX_LEN] = { 0 };
        uint32_t key_address;
        uint32_t inverse_key_address;

        if (!key) {
                return ERR_PROG_INVALID_ARGUMENT;
        }

        if (key_idx < 0 || key_idx > info.max_idx) {
                return ERR_PROG_INVALID_ARGUMENT;
        }

        key_address = info.keys_area_base_address + info.max_len * key_idx;
        /* Translate to the 64-bit cell address */
        key_address = (key_address & ~OTP_START_ADDRESS) >> 3;
        inverse_key_address = info.inverse_keys_area_base_address + info.max_len * key_idx;
        inverse_key_address = (inverse_key_address & ~OTP_START_ADDRESS) >> 3;

        /* Read key */
        err = prog_read_otp(key_address, (uint32_t *) key_cp, (info.max_len >> 2));

        if (err) {
                return err;
        }

        /* Read inverted key */
        err = prog_read_otp(inverse_key_address, (uint32_t *) inverse_key, (info.max_len >> 2));

        if (err) {
                return err;
        }

        *valid = true;
        *key_len = info.max_len;

        for (i = info.max_len - 1; i >= 0; i--) {
                if ((inverse_key[i] ^ key_cp[i]) != 0xFF) {
                        if (type == KEY_TYPE_ASYMMETRIC && inverse_key[i] == 0x00 && key_cp[i] == 0x00) {
                                /* Asymmetric key could be shorter than maximum length */
                                *key_len = i;
                        } else {
                                /* Key was revoked or written improperly */
                                *valid = false;
                                break;
                        }
                }
        }

        if (type == KEY_TYPE_ASYMMETRIC && *key_len < info.min_len) {
                /* Asymmetric key is too short */
                *valid = false;
        }

        memcpy(key, key_cp, *key_len);

        return err;
}

int prog_gdb_direct_read(uint32_t mem_address, uint8_t *buf, uint32_t size)
{
        if (target != &target_gdb_server) {
                return ERR_FAILED;
        }

        return gdb_server_cmd_direct_read(buf, size, mem_address);
}

int prog_gdb_read_chip_rev(char *chip_rev)
{
        const uint32_t id_regs[5] = {
                CHIP_ID1_REG, CHIP_ID2_REG, CHIP_ID3_REG, CHIP_REVISION_REG, CHIP_TEST1_REG
        };
        uint8_t id[5] = { 0 };
        int i;
        int err = 0;

        if (target != &target_gdb_server) {
                return ERR_FAILED;
        }

        /* Read chip revision */
        for (i = 0; err == 0 && i < sizeof(id); ++i) {
                err = prog_gdb_direct_read(id_regs[i], &id[i], 1);
        }

        if (err) {
                return err;
        }

        /* Copy info to output buffer*/
        /* Chip revision */
        chip_rev[0] = id[0];
        chip_rev[1] = id[1];
        chip_rev[2] = id[2];
        chip_rev[3] = id[3];
        chip_rev[4] = id[4] + 'A';
        chip_rev[5] = '\0';

        return err;
}

int prog_map_product_id_to_chip_rev(const char *product_id, char *chip_rev)
{
        if ((strcmp(product_id, "DA14681-01") == 0) || (strcmp(product_id, "DA14680-01") == 0)) {
                if (chip_rev) {
                        strncpy(chip_rev, "680AH", CHIP_REV_STRLEN);
                }
                return 0;
        }
        if ( (strcmp(product_id, "DA14682-00") == 0) || (strcmp(product_id, "DA14683-00") == 0) ||
             (strcmp(product_id, "DA15000-00") == 0) || (strcmp(product_id, "DA15001-00") == 0) ||
             (strcmp(product_id, "DA15100-00") == 0) || (strcmp(product_id, "DA15101-00") == 0) ){
                if (chip_rev) {
                        strncpy(chip_rev, "680BB", CHIP_REV_STRLEN);
                }
                return 0;
        }
        return ERR_PROG_UNKNOWN_PRODUCT_ID;
}

enum endianess {
        USE_LITTLE_ENDIANESS,
        USE_BIG_ENDIANESS
};

static inline void store32(void *buf, uint32_t val, enum endianess e)
{
        uint8_t *b = buf;

        if (USE_LITTLE_ENDIANESS == e) {
                b[0] = val & 0xff;
                val >>= 8;
                b[1] = val & 0xff;
                val >>= 8;
                b[2] = val & 0xff;
                val >>= 8;
                b[3] = val & 0xff;
        } else {
                b[3] = val & 0xff;
                val >>= 8;
                b[2] = val & 0xff;
                val >>= 8;
                b[1] = val & 0xff;
                val >>= 8;
                b[0] = val & 0xff;
        }
}

int prog_fill_image_header(uint8_t *buf, int image_size, const char *chip_rev,
                                                        image_type_t type, image_mode_t mode)
{
        struct qspi_image_header image_header = {
                .magic = { 0 },
                .length = { 0 }
        };
        int header_size = -1;

        image_header.magic[2] = 0x00;

        if (IMG_QSPI == type) {
                image_header.magic[0] = 'q';
                image_header.magic[1] = 'Q';
                if (IMG_CACHED == mode) {
                        store32(&image_header.length, 0x80000000UL | (image_size - 8),
                                                                                USE_BIG_ENDIANESS);
                } else {
                        store32(&image_header.length, image_size, USE_BIG_ENDIANESS);
                }
                header_size = IMAGE_HEADER_SIZE;
                memcpy(buf, &image_header, header_size);
        } else if (IMG_QSPI_S == type) {
                image_header.magic[0] = 'p';
                image_header.magic[1] = 'P';
                store32(&image_header.length, image_size, USE_BIG_ENDIANESS);
                header_size = IMAGE_HEADER_SIZE;
                memcpy(buf, &image_header, header_size);
        } else if (IMG_OTP == type) {
                uint32_t len;

                if (strcmp(chip_rev, "680AH") != 0) {
                        /* Newer chip revisions don't require any header in OTP case */
                        return 0;
                }

                /* convert to 8-byte multiple */
                len = (image_size + 7) & ~7;
                /* convert to counting 32-bit words */
                len >>= 2;

                if (IMG_CACHED == mode) {
                        store32(buf, 0x80000000UL | len, USE_LITTLE_ENDIANESS);
                } else {
                        store32(buf, len, USE_LITTLE_ENDIANESS);
                }
                header_size = IMAGE_HEADER_SIZE >> 1;
        }

        return header_size;
}

int prog_make_image(uint8_t *binary, int binary_size, const char *chip_rev,
                                                image_type_t type, image_mode_t mode,
                                                uint8_t *buf, int buf_size, int *required_size)
{
        int header_size;
        int size;
        uint32_t stack_pointer;
        uint32_t reset_handler;
        uint32_t *int_buf = (uint32_t *) binary;
        /* Size of memory block that is in RAM even when FLASH is mapped at address 0 */
        int ram_at_0_size = 0x200;
        if (strcmp(chip_rev, "680AH") == 0) {
                ram_at_0_size = 0x100;
        }
        uint8_t header_buffer[IMAGE_HEADER_SIZE];

        if (NULL == binary || (NULL == buf && buf_size > 0)) {
                return ERR_PROG_INVALID_ARGUMENT;
        }

        header_size = prog_fill_image_header(header_buffer, binary_size, chip_rev,
                type, mode);

        if (header_size < 0) {
                return header_size;
        }

        stack_pointer = int_buf[0];
        reset_handler = int_buf[1];
        /*
         * Sanity check for image
         *
         * Stack pointer has to be in range of (0x100, 0x24000) or (0x7FC0000, 0x7FE4000)
         * and reset handler has to be in range of (0x100, 0x24000) or (0x7F80000, 0xA0000000)
         * Otherwise the image is invalid.
         */
        if (!((stack_pointer > 0x100 && stack_pointer < 0x24000) ||
                                (stack_pointer > 0x7FC0000 && stack_pointer < 0x7FE4000) ||
                                (reset_handler > 0x100 && reset_handler < 0x24000) ||
                                (reset_handler > 0x7F80000 && reset_handler < 0xA0000000))) {
                return ERR_PROG_QSPI_IMAGE_FORMAT;
        }

        /* Compute required output buffer size */
        if (IMG_QSPI == type && IMG_CACHED == mode) {
                /* For cached images size does not change */
                size = binary_size;
        } else {
                /* For other images, header is added extra, add some padding for OTP */
                size = header_size + binary_size;
                if (IMG_OTP == type) {
                        size += ((binary_size + 7) & ~7) - binary_size;
                }
        }

        if (required_size) {
                *required_size = size;
        }

        if (size > buf_size) {
                return ERR_PROG_INSUFICIENT_BUFFER;
        }

        /* Image can be made in place, make sure that memory is moved correctly */
        if (IMG_QSPI == type && IMG_CACHED == mode) {
                /* Buffer must contain at least RAM block */
                if (buf_size < ram_at_0_size) {
                        return ERR_PROG_INSUFICIENT_BUFFER;
                }

                /*
                 * Cached binary, most of the image does not need to be moved if input
                 * and output buffer is same.
                 */
                if (binary != buf) {
                        memcpy(buf + ram_at_0_size, binary + ram_at_0_size,
                                                                binary_size - ram_at_0_size);
                }
                /* Move vector table a bit, 8  bytes are lost */
                memmove(buf + header_size, binary, ram_at_0_size - header_size);
        } else {
                /* Fill padding with 0 for OTP images */
                memset(buf + binary_size, 0, size - binary_size);
                /* Copy/move binary to make space for header */
                memmove(buf + header_size, binary, binary_size);
        }

        /* Add header at the beginning */
        memcpy(buf, header_buffer, header_size);

        return size;
}

static const uint32_t crc32_tab[] = {
        0x00000000, 0x77073096, 0xee0e612c, 0x990951ba, 0x076dc419, 0x706af48f,
        0xe963a535, 0x9e6495a3, 0x0edb8832, 0x79dcb8a4, 0xe0d5e91e, 0x97d2d988,
        0x09b64c2b, 0x7eb17cbd, 0xe7b82d07, 0x90bf1d91, 0x1db71064, 0x6ab020f2,
        0xf3b97148, 0x84be41de, 0x1adad47d, 0x6ddde4eb, 0xf4d4b551, 0x83d385c7,
        0x136c9856, 0x646ba8c0, 0xfd62f97a, 0x8a65c9ec, 0x14015c4f, 0x63066cd9,
        0xfa0f3d63, 0x8d080df5, 0x3b6e20c8, 0x4c69105e, 0xd56041e4, 0xa2677172,
        0x3c03e4d1, 0x4b04d447, 0xd20d85fd, 0xa50ab56b, 0x35b5a8fa, 0x42b2986c,
        0xdbbbc9d6, 0xacbcf940, 0x32d86ce3, 0x45df5c75, 0xdcd60dcf, 0xabd13d59,
        0x26d930ac, 0x51de003a, 0xc8d75180, 0xbfd06116, 0x21b4f4b5, 0x56b3c423,
        0xcfba9599, 0xb8bda50f, 0x2802b89e, 0x5f058808, 0xc60cd9b2, 0xb10be924,
        0x2f6f7c87, 0x58684c11, 0xc1611dab, 0xb6662d3d, 0x76dc4190, 0x01db7106,
        0x98d220bc, 0xefd5102a, 0x71b18589, 0x06b6b51f, 0x9fbfe4a5, 0xe8b8d433,
        0x7807c9a2, 0x0f00f934, 0x9609a88e, 0xe10e9818, 0x7f6a0dbb, 0x086d3d2d,
        0x91646c97, 0xe6635c01, 0x6b6b51f4, 0x1c6c6162, 0x856530d8, 0xf262004e,
        0x6c0695ed, 0x1b01a57b, 0x8208f4c1, 0xf50fc457, 0x65b0d9c6, 0x12b7e950,
        0x8bbeb8ea, 0xfcb9887c, 0x62dd1ddf, 0x15da2d49, 0x8cd37cf3, 0xfbd44c65,
        0x4db26158, 0x3ab551ce, 0xa3bc0074, 0xd4bb30e2, 0x4adfa541, 0x3dd895d7,
        0xa4d1c46d, 0xd3d6f4fb, 0x4369e96a, 0x346ed9fc, 0xad678846, 0xda60b8d0,
        0x44042d73, 0x33031de5, 0xaa0a4c5f, 0xdd0d7cc9, 0x5005713c, 0x270241aa,
        0xbe0b1010, 0xc90c2086, 0x5768b525, 0x206f85b3, 0xb966d409, 0xce61e49f,
        0x5edef90e, 0x29d9c998, 0xb0d09822, 0xc7d7a8b4, 0x59b33d17, 0x2eb40d81,
        0xb7bd5c3b, 0xc0ba6cad, 0xedb88320, 0x9abfb3b6, 0x03b6e20c, 0x74b1d29a,
        0xead54739, 0x9dd277af, 0x04db2615, 0x73dc1683, 0xe3630b12, 0x94643b84,
        0x0d6d6a3e, 0x7a6a5aa8, 0xe40ecf0b, 0x9309ff9d, 0x0a00ae27, 0x7d079eb1,
        0xf00f9344, 0x8708a3d2, 0x1e01f268, 0x6906c2fe, 0xf762575d, 0x806567cb,
        0x196c3671, 0x6e6b06e7, 0xfed41b76, 0x89d32be0, 0x10da7a5a, 0x67dd4acc,
        0xf9b9df6f, 0x8ebeeff9, 0x17b7be43, 0x60b08ed5, 0xd6d6a3e8, 0xa1d1937e,
        0x38d8c2c4, 0x4fdff252, 0xd1bb67f1, 0xa6bc5767, 0x3fb506dd, 0x48b2364b,
        0xd80d2bda, 0xaf0a1b4c, 0x36034af6, 0x41047a60, 0xdf60efc3, 0xa867df55,
        0x316e8eef, 0x4669be79, 0xcb61b38c, 0xbc66831a, 0x256fd2a0, 0x5268e236,
        0xcc0c7795, 0xbb0b4703, 0x220216b9, 0x5505262f, 0xc5ba3bbe, 0xb2bd0b28,
        0x2bb45a92, 0x5cb36a04, 0xc2d7ffa7, 0xb5d0cf31, 0x2cd99e8b, 0x5bdeae1d,
        0x9b64c2b0, 0xec63f226, 0x756aa39c, 0x026d930a, 0x9c0906a9, 0xeb0e363f,
        0x72076785, 0x05005713, 0x95bf4a82, 0xe2b87a14, 0x7bb12bae, 0x0cb61b38,
        0x92d28e9b, 0xe5d5be0d, 0x7cdcefb7, 0x0bdbdf21, 0x86d3d2d4, 0xf1d4e242,
        0x68ddb3f8, 0x1fda836e, 0x81be16cd, 0xf6b9265b, 0x6fb077e1, 0x18b74777,
        0x88085ae6, 0xff0f6a70, 0x66063bca, 0x11010b5c, 0x8f659eff, 0xf862ae69,
        0x616bffd3, 0x166ccf45, 0xa00ae278, 0xd70dd2ee, 0x4e048354, 0x3903b3c2,
        0xa7672661, 0xd06016f7, 0x4969474d, 0x3e6e77db, 0xaed16a4a, 0xd9d65adc,
        0x40df0b66, 0x37d83bf0, 0xa9bcae53, 0xdebb9ec5, 0x47b2cf7f, 0x30b5ffe9,
        0xbdbdf21c, 0xcabac28a, 0x53b39330, 0x24b4a3a6, 0xbad03605, 0xcdd70693,
        0x54de5729, 0x23d967bf, 0xb3667a2e, 0xc4614ab8, 0x5d681b02, 0x2a6f2b94,
        0xb40bbe37, 0xc30c8ea1, 0x5a05df1b, 0x2d02ef8d
};

uint32_t crc32_update(uint32_t crc, const uint8_t *data, size_t len)
{
        while (len--) {
                crc = crc32_tab[(crc ^ *data++) & 0xff] ^ (crc >> 8);
        }
        return crc;
}

static void fill_suota_header(suota_1_1_image_header_t *img_header, const uint8_t *buf, int size,
                                        const char *version, time_t time_stamp, uint16_t flags)
{
        img_header->signature[0] = SUOTA_1_1_IMAGE_HEADER_SIGNATURE_B1;
        img_header->signature[1] = SUOTA_1_1_IMAGE_HEADER_SIGNATURE_B2;
        img_header->flags = flags;
        img_header->code_size = size;
        img_header->timestamp = time_stamp;
        img_header->exec_location = sizeof(img_header);
        strncpy((char *) img_header->version, version, sizeof(img_header->version));
        img_header->crc = crc32_update(~0, buf, size) ^ ~0;
}

int prog_write_qspi_suota_image(uint8_t *buf, int size, const char *version,
                                                                time_t time_stamp, uint16_t flags)
{
        cmd_partition_table_t *part_table;
        cmd_partition_entry_t *entry;
        cmd_partition_entry_t *part_table_end;
        uint32_t part_table_len;
        suota_1_1_image_header_t img_header;
        int exec_partition_start = -1;
        int image_header_start = -1;
        int ret;

        /*
         * Read partition table to see if NVMS_IMAGE_HEADER_PART and NVMS_FW_EXEC_PART
         * partitions are present.
         */
        ret = prog_read_partition_table((uint8_t **) &part_table, &part_table_len);
        if (ret) {
                goto end;
        }

        /*
         * Find start of those two partitions.
         */
        part_table_end = (cmd_partition_entry_t *) (((uint8_t *) part_table) + part_table_len);
        entry = &part_table->entry;

        while (entry < part_table_end) {
                if (entry->type == NVMS_FW_EXEC_PART) {
                        exec_partition_start = entry->start_sector * part_table->sector_size;
                } else if (entry->type == NVMS_IMAGE_HEADER_PART) {
                        image_header_start = entry->start_sector * part_table->sector_size;
                }
                entry = (cmd_partition_entry_t *) (((uint8_t *) entry) + sizeof(*entry)
                                                                        + entry->name.len);
        }
        free(part_table);

        if (image_header_start < 0 || exec_partition_start < 0) {
                ret = ERR_PROG_NO_PARTITON;
                goto end;
        }

        /*
         * Prepare SUOTA image header with user supplied data.
         */
        fill_suota_header(&img_header, buf, size, version, time_stamp, flags);

        /*
         * Write image header to NVMS_IMAGE_HEADER_PART partition then binary
         * data to NVMS_FW_EXEC_PART
         */
        ret = prog_write_to_qspi(image_header_start, (uint8_t *) &img_header, sizeof(img_header));
        if (ret) {
                goto end;
        }

        ret = prog_write_to_qspi(exec_partition_start, buf, size);

end:
        return ret;
}

void prog_set_target_reset_cmd(const char *trc)
{
        target_reset_cmd = strdup(trc);
}

int prog_gdb_connect(const char *host_name, int port, bool reset)
{
        target = &target_gdb_server;

        return gdb_server_connect(host_name, port, reset);
}

void prog_gdb_disconnect()
{
        gdb_server_disconnect();
}

prog_gdb_server_info_t *prog_get_gdb_instances(const char *gdb_server_cmd)
{
        return gdb_server_get_instances(gdb_server_cmd);
}
