/**
 ****************************************************************************************
 *
 * @file programmer.h
 *
 * @brief Programmer API.
 *
 * Copyright (C) 2015-2018 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#ifndef PROGRAMMER_H_
#define PROGRAMMER_H_

#include <stdint.h>
#include <stdbool.h>
#include <partition_def.h>

#ifdef __cplusplus
#extern "C" {
#endif

#ifdef _MSC_VER
#ifdef LIBPROGRAMMER_EXPORTS
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT __declspec(dllimport)
#endif
#else
#define DLLEXPORT
#endif
#define ERR_FAILED                      -1      /**< failed with no detailed error code */
#define ERR_ALLOC_FAILED                -2      /**< memory allocation failed */
#define ERR_FILE_OPEN                   -3      /**< file cannot be opened */
#define ERR_FILE_READ                   -4      /**< file cannot be read */
#define ERR_FILE_PATCH                  -5      /**< file cannot be patched */
#define ERR_FILE_WRITE                  -6      /**< file cannot be written */
#define ERR_FILE_CLOSE                  -7      /**< file cannot be closed */
#define ERR_FILE_TOO_BIG                -8      /**< file is too big */

#define ERR_PROT_NO_RESPONSE            -100    /**< timeout waiting for response */
#define ERR_PROT_CMD_REJECTED           -101    /**< NAK received when waiting for ACK */
#define ERR_PROT_INVALID_RESPONSE       -102    /**< invalid data received when waiting for ACK */
#define ERR_PROT_CRC_MISMATCH           -103    /**< CRC16 mismatch */
#define ERR_PROT_CHECKSUM_MISMATCH      -104    /**< checksum mismatch while uploading 2nd stage bootloader */
#define ERR_PROT_BOOT_LOADER_REJECTED   -105    /**< 2nd stage bootloader rejected */
#define ERR_PROT_UNKNOWN_RESPONSE       -106    /**< invalid announcement message received */
#define ERR_PROT_TRANSMISSION_ERROR     -107    /**< failed to transmit data */
#define ERR_PROT_COMMAND_ERROR          -108    /**< error executing command */
#define ERR_PROT_UNSUPPORTED_VERSION    -110    /**< unsupported version of bootloader detected */

#define ERR_GDB_SERVER_SOCKET           -200    /**< communication with GDB Server socket failed */
#define ERR_GDB_SERVER_CRC_MISMATCH     -201    /**< received frame has bad checksum */
#define ERR_GDB_SERVER_CMD_REJECTED     -202    /**< NAK received when waiting for ACK */
#define ERR_GDB_SERVER_INVALID_RESPONSE -203    /**< invalid data received */

#define ERR_PROG_QSPI_WRITE             -300    /**< QSPI write error */
#define ERR_PROG_QSPI_VERIFY            -301    /**< QSPI verify error */
#define ERR_PROG_OTP_WRITE              -310    /**< OTP write error */
#define ERR_PROG_OTP_READ               -311    /**< OTP write error */
#define ERR_PROG_OTP_VERIFY             -312    /**< OTP read error */
#define ERR_PROG_OTP_NOT_EMPTY          -313    /**< OTP not empty */
#define ERR_PROG_OTP_SAME               -314    /**< data written to OTP match data to be written */
#define ERR_PROG_TCS_FULL               -320    /**< OTP not enough empty space in TCS */

#define ERR_PROG_QSPI_IMAGE_FORMAT      -340    /**< Executable image not recognized */
#define ERR_PROG_UNKNOW_CHIP            -341    /**< Chip revision was unreadable or unknown */
#define ERR_PROG_INVALID_ARGUMENT       -342    /**< Invalid argument passed to function */
#define ERR_PROG_INSUFICIENT_BUFFER     -343    /**< Buffer passed to function is to small */
#define ERR_PROG_NO_PARTITON            -344    /**< Required partition not present */
#define ERR_PROG_UNKNOWN_PRODUCT_ID     -345    /**< Product id is unknown */

#define MSG_FROM_STDOUT                 -400    /**< Refers to stdout_msg buffer */
#define MSG_FROM_STDERR                 -401    /**< Refers to stderr_msg buffer */

#define GDB_MODE_GUI                    1       /**< Refers to prog_gdb_mode */
#define GDB_MODE_INVALIDATE_STUB        2       /**< Refers to prog_gdb_mode */
#define GDB_MODE_BLOCK_WRITE_OTP        4       /**< Refers to prog_gdb_mode */

#define PROGRAMMER_PATCH_OFFSET_BAUDRATE        0x210 /**< uartboot binary baudrate value offset. */
#define PROGRAMMER_PATCH_OFFSET_TX_PORT         0x200 /**< uartboot binary Tx port value offset. */
#define PROGRAMMER_PATCH_OFFSET_TX_PIN          0x204 /**< uartboot binary Tx pin value offset. */
#define PROGRAMMER_PATCH_OFFSET_RX_PORT         0x208 /**< uartboot binary Rx port value offset. */
#define PROGRAMMER_PATCH_OFFSET_RX_PIN          0x20c /**< uartboot binary Rx pin value offset. */
/** Maximum offset for patch checking. */
#define PROGRAMMER_PATCH_OFFSET_MAX             PROGRAMMER_PATCH_OFFSET_BAUDRATE

#define TCS_WORD_SIZE  (384>>2)       //TCS size in 32 bit words
#define TCS_ADDR       (0x1D4F)       //TCS address (64 bit aligned)

/* Command for basic functions needed by protocol */
#define CMD_WRITE                  0x01
#define CMD_READ                   0x02
#define CMD_COPY_QSPI              0x03
#define CMD_ERASE_QSPI             0x04
#define CMD_RUN                    0x05
#define CMD_WRITE_OTP              0x06
#define CMD_READ_OTP               0x07
#define CMD_READ_QSPI              0x08
#define CMD_CUSTOMER_SPECIFIC      0x09
#define CMD_READ_PARTITION_TABLE   0x0A
#define CMD_GET_VERSION            0x0B
#define CMD_CHIP_ERASE_QSPI        0x0C
#define CMD_IS_EMPTY_QSPI          0x0D
#define CMD_READ_PARTITION         0x0E
#define CMD_WRITE_PARTITION        0x0F
#define CMD_DUMMY                  0xFF

/** Chip info */
#define CHIP_REV_STRLEN         6   /**< the chip revision string length */
#define CHIP_OTP_ID_STRLEN      9   /**< the chip id string length */
#define CHIP_PACKAGE_LEN        7   /**< the chip package string length */

#define INVALID_PID             0
/** Device's serial number not available */
#define SERIAL_NUMBER_NA        -1

/** The image header size expected by the ROM booter. */
#define IMAGE_HEADER_SIZE       8

/** Unique device identifier size in bytes */
#define UNIQUE_DEVICE_ID_SIZE   16

/** Maximum index of the asymmetric key */
#define ASYMMETRIC_KEY_MAX_IDX  3

/** Asymmetric key length range in bytes */
#define ASYMMETRIC_KEY_MIN_LEN  32
#define ASYMMETRIC_KEY_MAX_LEN  64

/** Maximum index of the symmetric key */
#define SYMMETRIC_KEY_MAX_IDX   7

/** Symmetric key length in bytes */
#define SYMMETRIC_KEY_LEN       32

typedef struct {
        char chip_rev[CHIP_REV_STRLEN];
        char chip_otp_id[CHIP_OTP_ID_STRLEN];
        char chip_package[CHIP_PACKAGE_LEN];
} chip_info_t;

/** No killing GDB Server modes */
typedef enum {
        /** Kill GDB Server instance on start and on stop */
        NO_KILL_MODE_NONE       = 0,
        /** Kill GDB Server instance only during close */
        NO_KILL_MODE_CONNECT    = 1,
        /** Kill GDB Server instances only during initialization */
        NO_KILL_MODE_DISCONNECT = 2,
        /** Don't kill GDB Server instances in any case */
        NO_KILL_MODE_ALL        = 3,
} no_kill_mode_t;

/** GDB Server configuration */
typedef struct {
        /* GDB Server port */
        unsigned int port;
        /* GDB Server host name */
        char *host_name;
        /* Path to GDB Server execution file */
        char *gdb_server_path;
        /* No killing GDB Server mode */
        no_kill_mode_t no_kill_gdb_server;
        /* If true libprogrammer should connect to GDB Server instance */
        bool connect_gdb_server;
        /* If true a platform reset will be performed after connection establishment */
        bool reset;
        /* If true a bootloader could be not loaded if it is running on platform already */
        bool check_bootloader;
} prog_gdb_server_config_t;

/** UART boot configuration that is patched to the uploaded binary. */
typedef struct
{
        /** Baud rate.*/
        unsigned int baudrate;

        /** True when baud rate is to be patched. */
        int baudrate_patch;

        /** Tx GPIO port. */
        unsigned int tx_port;

        /** True when Tx GPIO port is to be patched. */
        int tx_port_patch;

        /** Tx GPIO pin. */
        unsigned int tx_pin;

        /** True when Tx GPIO pin is to be patched. */
        int tx_pin_patch;

        /** Rx GPIO port. */
        unsigned int rx_port;

        /** True when Rx GPIO port  is to be patched. */
        int rx_port_patch;

        /** Rx GPIO pin. */
        unsigned int rx_pin;

        /** True when Rx GPIO pin is to be patched. */
        int rx_pin_patch;
} prog_uartboot_config_t;

/** GDB Server instance info */
typedef struct {
        /** Process ID */
        int pid;
        /** Port used by instance */
        int port;
        /** Connected device's serial number - could be not available (SERIAL_NUMBER_NA) */
        long long sn;
} prog_gdb_server_info_t;

/** Key type */
typedef enum {
        /** Symmetric key */
        KEY_TYPE_SYMMETRIC,
        /** Asymmetric key */
        KEY_TYPE_ASYMMETRIC,
} key_type_t;

/**
 * \brief Set initial baud rate to be used when no uartboot is detected on the device.
 *
 * \param [in] Boot loader baud rate.
 */
void DLLEXPORT prog_set_initial_baudrate(unsigned int initial_baudrate);

/**
 * \brief Get configured boot loader baud rate.
 *
 * \return Boot loader baud rate.
 */
unsigned int DLLEXPORT prog_get_initial_baudrate(void);

/**
 * \brief Open serial port for programmer
 *
 * \param [in] port Serial port
 * \param [in] baudrate Serial port baudrate
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_serial_open(const char *port, int baudrate);

/**
 * \brief Open connection to gdb server
 *
 * \param [in] gdb_server_conf gdb server configuration
 *
 * \return PID of used GDB Server instance on success, error code on failure (negative value)
 *
 */
int DLLEXPORT prog_gdb_open(const prog_gdb_server_config_t *gdb_server_conf);

/**
 * \brief Set mode variables for gdb usage of the dll
 *
 * \param [in] 0 = switch to command line mode(default)
 *             1 = switch to GUI mode
 *             2 = Invalidates a previous downloaded stub into the target
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_gdb_mode(int mode);

/**
 * \brief Close target interface
 *
 * \param [in] data interface dependent data
 *
 * Function will close serial interface or gdb server port, depending on what was opened
 *
 * \note In the case of GDB Server interface the \p data should be a GDB Server instance's PID.
 * GDB Server instance with this PID will be stopped. If INVALID_VALUE is passed in the case of
 * that interface then internally stored PID number is used (if it exists). In the case of serial
 * interface this parameter is currently not used and may be any number.
 *
 * \sa prog_serial_open
 * \sa prog_gdb_open
 *
 */
void DLLEXPORT prog_close_interface(int data);

/**
 * \brief Close serial port
 *
 * \param [in] data currently not used argument
 *
 */
void DLLEXPORT prog_serial_close(int data);

/**
 * \brief Close GDB Server interface
 *
 * \param [in] pid selected process ID
 *
 */
void DLLEXPORT prog_gdb_close(int pid);

/**
 * \brief Write to RAM memory
 *
 * \param [in] ram_address RAM address, where file will be written
 * \param [in] buf Buffer with data to write
 * \param [in] size Number of bytes to write
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_to_ram(uint32_t ram_address, const uint8_t *buf, uint32_t size);

/**
 * \brief Write file to RAM memory
 *
 * \param [in] ram_address RAM address, where file will be written
 * \param [in] file_name Name of the file to written
 * \param [in] size Number of bytes to write
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_file_to_ram(uint32_t ram_address, const char *file_name, uint32_t size);

/**
 * \brief Write buffer to QSPI flash memory
 *
 * \param [in] flash_address QSPI flash address, where file will be written
 * \param [in] buf Buffer to written to device flash
 * \param [in] size Number of bytes to write
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_to_qspi(uint32_t flash_address, const uint8_t *buf, uint32_t size);

/**
 * \brief Write file to QSPI flash memory
 *
 * \param [in] flash_address QSPI flash address, where file will be written
 * \param [in] file_name Name of the file to written
 * \param [in] size Number of bytes to write
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_file_to_qspi(uint32_t flash_address, const char *file_name, uint32_t size);

/**
 * \brief Erase part of QSPI flash memory
 *
 * \param [in] flash_address QPSI flash address
 * \param [in] size Number of bytes of the flash memory to erase
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_erase_qspi(uint32_t flash_address, uint32_t size);

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
int DLLEXPORT prog_is_empty_qspi(unsigned int size, unsigned int start_address, int *ret_number);

/**
 * \brief Read from device memory (RAM, QSPI, OTP)
 *
 * \param [in] mem_address Memory address
 * \param [in] buf buffer to store device memory
 * \param [in] size Number of bytes to read
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_memory(uint32_t mem_address, uint8_t *buf, uint32_t size);

/**
 * \brief Save contents of device memory to file
 *
 * \param [in] mem_address Memory address
 * \param [in] file_name Name of the file to write data from memory
 * \param [in] size Number of bytes to read
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_memory_to_file(uint32_t mem_address, const char *file_name, uint32_t size);

/**
 * \brief Run arbitrary code
 *
 * \param [in] mem_address Memory address in device address space to execute
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_run(uint32_t mem_address);

/**
 * \brief Copy from RAM to QSPI flash memory
 *
 * \param [in] mem_address RAM address memory (source)
 * \param [in] flash_address QSPI flash address memory (destination)
 * \param [in] size Number of bytes to copy
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_copy_to_qspi(uint32_t mem_address, uint32_t flash_address, uint32_t size);

/**
 * \brief Erase whole QSPI flash memory
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_chip_erase_qspi(void);

/**
 * \brief Set uart bootloader code that will be transferred to device
 *
 * This function will store uart bootloader code that will be sent to device when
 * necessary.
 *
 * \param [in] buf Address of memory buffer containing boot loader code
 * \param [in] size NUmber of bytes pointed by buf
 *
 */
void DLLEXPORT prog_set_uart_boot_loader(uint8_t *buf, uint32_t size);

/**
 * \brief Read uart bootloader from file system
 *
 * This function will read uart bootloader from file system and call set_uart_boot_loader()
 * to setup code that must be sent to device before other programming commands can work.
 *
 * \param [in] file_name File name to use for bootloader
 *
 * \return 0 on success, error code on failure
 *
 * \sa prog_set_uart_boot_loader
 *
 */
int DLLEXPORT prog_set_uart_boot_loader_from_file(const char *file_name);

/**
 * \brief Print log message
 *
 * This function prints message to standard output or
 * to message output buffer - depends on GDB GUI mode.
 *
 * \param [in] msg message, includes formatting string
 * \param [in] ... arguments list
 *
 * \sa prog_gdb_mode
 *
 */
void DLLEXPORT prog_print_log(const char *msg, ...);

/**
 * \brief Print log message
 *
 * This function prints message to standard error or
 * to message error buffer - depends on GDB GUI mode.
 *
 * \param [in] msg message, includes formatting string
 * \param [in] ... arguments list
 *
 * \sa prog_gdb_mode
 *
 */
void DLLEXPORT prog_print_err(const char *msg, ...);

/**
 * \brief Write file to OTP memory
 *
 * \note If \p size is indivisible by 4, then proper number of zero bytes will be added to the
 * write buffer.
 *
 * \param [in] otp_address OTP address, where file will be written
 * \param [in] file_name Name of the file to be written
 * \param [in] size Number of bytes to write
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_file_to_otp(uint32_t otp_address, const char *file_name, uint32_t size);

/**
 * \brief Write data to OTP
 *
 * \param [in] address cell address in OTP
 * \param [in] buf words to be written
 * \param [in] len number of words in buffer
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_otp(uint32_t address, const uint32_t *buf, uint32_t len);

/**
 * \brief Read data from OTP
 *
 * \param [in] address cell address in OTP
 * \param [out] buf buffer for read words
 * \param [in] len number of words to be read
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_otp(uint32_t address, uint32_t *buf, uint32_t len);

/**
 * \brief Write data to OTP TCS section
 *
 * \param [out] address cell address in OTP
 * \param [in] buf words to be written in <register_address, register_data> pairs
 * \param [in] len number of words in buffer
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_tcs(uint32_t *address, const uint32_t *buf, uint32_t len);

/**
 * \brief Read data from QSPI
 *
 * \param [in] address address in QSPI
 * \param [out] buf buffer for data
 * \param [in] len number of bytes to be read
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_qspi(uint32_t address, uint8_t *buf, uint32_t len);

/**
 * \brief Save contents of device memory to file
 *
 * \param [in] address address in QSPI
 * \param [in] fname name of output file
 * \param [in] len number of bytes to read
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_qspi_to_file(uint32_t address, const char *fname, uint32_t len);

/**
 * \brief Read partition table
 *
 * \param [out] buf buffer to store the contents of the partition table
 * \param [out] len the size of buffer in bytes
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_partition_table(uint8_t **buf, uint32_t *len);

/**
 * \brief Read data from partition
 *
 * \param [in] id partition id
 * \param [in] address address in partition
 * \param [out] buf buffer for data
 * \param [in] len length of buffer
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_partition(nvms_partition_id_t id, uint32_t address, uint8_t *buf,
                                                                                uint32_t len);

/**
 * \brief Write buffer to NVMS partition memory
 *
 * \param [in] id partition id
 * \param [in] part_address NVMS partition address, where file will be written
 * \param [in] buf buffer to written to device flash
 * \param [in] size number of bytes to write
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_partition(nvms_partition_id_t id, uint32_t part_address,
                                                                const uint8_t *buf, uint32_t size);

/**
 * \brief Write file to NVMS partition memory
 *
 * \param [in] id partition id
 * \param [in] part_address NVMS partition address, where file will be written
 * \param [in] file_name name of the file to write
 * \param [in] size number of bytes to write
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_file_to_partition(nvms_partition_id_t id, uint32_t part_address,
                                                        const char *file_name, uint32_t size);

/**
 * \brief Save contents of partition memory to file
 *
 * \param [in] id partition id
 * \param [in] address address in partition
 * \param [in] fname name of output file
 * \param [in] len number of bytes to read
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_patrition_to_file(nvms_partition_id_t id, uint32_t address,
                                                                const char *fname, uint32_t len);

/**
 * \brief Boot arbitrary application binary
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_boot(void);

/**
 * \brief Translate errors from numbers designations to string equivalent
 *
 * Gives the meaning of the error code in the verbal form.
 *
 * \param [in] err error code
 *
 * \return the error code message
 *
 */
DLLEXPORT const char *prog_get_err_message(int err);

/**
 * \brief Patch secondary boot loader binary with configuration data.
 *
 * \param [in] Boot loader configuration.
 */
int DLLEXPORT prog_uartboot_patch_config(const prog_uartboot_config_t * uartboot_config);

/**
 * \brief Define the timeout value waiting for the UART signal from device
 *
 * \param [in] Timeout time in ms
 *
 */
void DLLEXPORT prog_set_uart_timeout(unsigned int timeoutInMs);

/**
 * \brief Get waiting time for the UART signal.
 *
 * \return Uart time out in ms.
 */
unsigned int DLLEXPORT get_uart_timeout(void);

/**
 * \brief Read chip info.
 *
 * Reads chip revision, chip_id (as stored in otp) and chip package info in ASCII format.
 * In case of error, user provided buffer is not touched.
 *
 * \param [out] chip_info pointer to buffer that receives the chip info
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_chip_info(chip_info_t *chip_info);

/**
 * \brief Read device memory without bootloader
 *
 * This function reads device memory as seen by device CPU. It doesn't require to have bootloader
 * running.
 *
 * \param [in] mem_address RAM address to read from
 * \param [out] buf buffer for data
 * \param [in] size size of buf in bytes
 * \returns 0 on success, negative value with error code on failure
 *
 */
int DLLEXPORT prog_gdb_direct_read(uint32_t mem_address, uint8_t *buf, uint32_t size);

/**
 * \brief Read chip revision.
 *
 * Reads chip revision from device's registers. It doesn't require to have bootloader running.
 *
 * \param [out] chip_rev pointer to buffer that receives the chip revision
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_gdb_read_chip_rev(char *chip_rev);

/**
 * \brief Read unique device identifier
 *
 * Reads unique device identifier from OTP memory.
 *
 * \note \p udi must point to the buffer which has at least UNIQUE_DEVICE_ID_SIZE bytes in length.
 *
 * \param [out] udi buffer for unique device id
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_read_unique_device_id(uint8_t *udi);

/**
 * \brief Write asymmetric/symmetric key to OTP
 *
 * Function writes asymmetric or symmetric key to the asymmetric/symmetric keys area in OTP. It
 * writes inverse asymmetric/symmetric key for given key also. If OTP memory for this key is not
 * empty then no write operation will be performed.
 *
 * \note \p key_idx valid range is from 0 to SYMMETRIC_KEY_MAX_IDX for symmetric keys and from 0 to
 * ASYMMETRIC_KEY_MAX_IDX for asymmetric keys. Symmetric key should have SYMMETRIC_KEY_LEN bytes
 * length and asymmetric key should have from ASYMMETRIC_KEY_MIN_LEN to ASYMMETRIC_KEY_MAX_LEN bytes
 * length. Default addresses (in OTP) for these areas:
 * - Inverse asymmetric keys:    0x7F8E5C0 - 0x7F8E6C0
 * - Asymmetric keys area (AKA): 0x7F8E6C0 - 0x7F8E7C0
 * - Inverse symmetric keys:     0x7F8E7C0 - 0x7F8E8C0
 * - Symmetric keys area (SKA):  0x7F8E8C0 - 0x7F8E9C0
 *
 * \param [in] type key type (symmetric/asymmetric)
 * \param [in] key_idx index of the key
 * \param [in] key buffer with key
 * \param [in] key_len buffer length in bytes
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_key(key_type_t type, int key_idx, const uint8_t *key, unsigned int key_len);


/**
 * \brief Read asymmetric/symmetric key from OTP
 *
 * Function reads an asymmetric or a symmetric key from the asymmetric/symmetric keys area in OTP.
 * It reads inverse asymmetric/symmetric key for given key also for validation key.
 *
 * \note \p key_idx valid range is from 0 to SYMMETRIC_KEY_MAX_IDX for the symmetric keys and
 * from 0 to ASYMMETRIC_KEY_MAX_IDX for the asymmetric keys. \p key must point to the buffer with
 * proper size: ASYMMETRIC_KEY_MAX_LEN for the asymmetric keys and SYMMETRIC_KEY_LEN for the
 * symmetric keys. The key is invalid when its inversion is incompatible or when its length is
 * shorter than ASYMMETRIC_KEY_MAX_LEN (this condition is only for the asymmetric keys).
 *
 * \param [in] type key type (symmetric/asymmetric)
 * \param [in] key_idx index of the key
 * \param [out] key buffer for read key
 * \param [out] key_len buffer length in bytes
 * \param [out] valid flag indicates that the key is valid or not
 *
 * \return 0 on success, error code on failure
 *
 * \sa prog_write_key
 *
 */
int DLLEXPORT prog_read_key(key_type_t type, int key_idx, uint8_t *key, unsigned int *key_len,
                                                                                       bool *valid);

/**
 * \brief Maps product_id to chip_rev in ASCII format.
 *
 * Product_id must contain null terminated strings in the form of 'DA1468x-yy'.
 * Chip_rev contains null terminated strings in the form of '680xx'.
 * In case of error, user provided buffer will not be touched.
 *
 * \param [in] product_id pointer to buffer that holds product_id
 * \param [out] chip_rev pointer to buffer that receives chip revision info, must be at least CHIP_REV_STRLEN char long.
 * If null pointer is passed, the function checks the validity of product_id and returns.
 *
 * \return 0 if product_id is valid, error otherwise
 *
 */
int DLLEXPORT prog_map_product_id_to_chip_rev(const char *product_id, char *chip_rev);

typedef enum {
        IMG_QSPI,
        IMG_QSPI_S,
        IMG_OTP
} image_type_t;

typedef enum {
        IMG_MIRRORED,
        IMG_CACHED
} image_mode_t;

struct qspi_image_header {
        uint8_t magic[4];       /* qQ or pP */
        uint8_t length[4];      /* counts bytes, MSB set to 1 for cached mode */
};

/**
 * \brief Prepare image header
 *
 * Function fills user buffer with header that can be used to build image for QSPI flash or OTP.
 *
 * \param [out] buf pointer to buffer that will be filled with header data (it must be at least
 *              8 bytes)
 * \param [in] image_size size of bin file
 * \param [in] chip_rev string representing chip revision
 * \param [in] type specifies one of QSPI or OTP images
 * \param [in] mode specifies mirrored or cached mode
 *
 * \return positive/zero value represent size of image header, negative is an error code
 *
 */
int DLLEXPORT prog_fill_image_header(uint8_t *buf, int image_size, const char *chip_rev,
                                                        image_type_t type, image_mode_t mode);

/**
 * \brief Prepare image for FLASH or OTP memory
 *
 * Function prog_make_image() takes a binary image, and converts it to an image that can be
 * stored in FLASH or OTP.
 * This function can convert the image in place if binary and buf point to same memory.
 * \Note function can be called first with buf set to NULL or bus_size 0 to calculate how
 * big the output buffer should be. When function returns ERR_PROG_INSUFICIENT_BUFFER variable
 * pointed by reuired_size can be used to allocate buffer that can hold output image.
 *
 * \param [in] binary pointer to binary image data
 * \param [in] binary_size size of binary data
 * \param [in] chip_rev string representing chip revision
 * \param [in] type specifies one of QSPI or OTP images
 * \param [in] mode specifies mirrored or cached mode
 * \param [out] buf pointer to buffer used for saving image (can be NULL)
 * \param [in] buf_size size of memory pointed by buf (must be 0 if buf is NULL)
 * \param [out] required_size pointer to variable that will receive required image size if
 *              buffer provided by caller is too small to fit image (can be NULL)
 *
 * \return positive values represent size of the image that was prepared
 *         negative is an error code, if function returns ERR_PROG_INSUFICIENT_BUFFER
 *         required_buffer size can be used to determine image size.
 *
 */
int DLLEXPORT prog_make_image(uint8_t *binary, int binary_size, const char *chip_rev,
        image_type_t type, image_mode_t mode, uint8_t *buf, int buf_size, int *required_size);

/**
 * \brief Write application image to the OTP memory
 *
 * Function writes given image (raw binary must be converted using e.g. \sa prog_make_image()) to
 * the OTP memory, from which it could be executed. Image is written at 0x7F80000 address. Function
 * fills 'Mirrored/Cached At startup', 'Non-Volatile Memory', 'Mirror image length' and 'Image CRC'
 * fields in the OTP header with proper values.
 *
 * \note \buf and \len must be aligned to 4-bytes (size of OTP word)
 *
 * \param [in] buf buffer application image to be written
 * \param [in] len buffer's length (in bytes)
 * \param [in] mode image's mode (mirrored/cached)
 *
 * \return 0 on success, error code on failure
 */
int DLLEXPORT prog_write_image_to_otp(const uint8_t *buf, uint32_t len, image_mode_t mode);

/**
 * \brief Write binary file to executable partition
 *
 * This function takes a binary image (compiled for address other than 0), and writes it
 * to the partition with id NVMS_FW_EXEC_PART. It also fills the image header with version info and CRC,
 * and writes it to the partition with id NVMS_IMAGE_HEADER_PART.
 *
 * \param [in] buf pointer to binary image data
 * \param [in] size size of binary data
 * \param [in] version version string for image header
 * \param [in] time_stamp image creation time
 * \param [in] flags suota image flags (see suota.h)
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_write_qspi_suota_image(uint8_t *buf, int size, const char *version,
                                                                time_t time_stamp, uint16_t flags);

/**
 * \brief Define the command for resetting the target
 *
 * \param [in] The string of reset command
 *
 */
void DLLEXPORT prog_set_target_reset_cmd(const char *trc);

/**
 * \brief Connect to GDB Server
 *
 * \note After usage of this function the prog_gdb_disconnect function should be used for cleanup.
 *
 * \param [in] host_name host name
 * \param [in] port port number
 * \param [in] reset perform platform reset flag
 *
 * \return 0 on success, error code on failure
 *
 */
int DLLEXPORT prog_gdb_connect(const char *host_name, int port, bool reset);

/**
 * \brief Disconnect from GDB Server instance
 *
 * Function closes socket which is used for communication with GDB Server.
 *
 * \note If socket was not opened earlier, then function will do nothing.
 *
 */
void DLLEXPORT prog_gdb_disconnect();

/**
 * \brief Get GDB Server instances array
 *
 * \note Each valid element has PID value > 0. First element with PID < 0 means end of array.
 * \note Array is dynamic allocated - must be freed after use.
 *
 * \param [in] gdb_server_cmd GDB Server run command
 *
 * \return array with GDB Server instances on success, NULL otherwise
 *
 */
prog_gdb_server_info_t * DLLEXPORT prog_get_gdb_instances(const char *gdb_server_cmd);

#ifdef __cplusplus
}
#endif

#endif /* PROGRAMMER_H_ */
