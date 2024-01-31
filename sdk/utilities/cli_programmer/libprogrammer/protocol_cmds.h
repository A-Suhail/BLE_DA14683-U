/**
 ****************************************************************************************
 *
 * @file protocol_cmds.h
 *
 * @brief UART bootloader protocol header file
 *
 * Copyright (C) 2015-2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

/**
 * \addtogroup UTILITIES
 * \{
 * \addtogroup PROGRAMMER
 * \{
 * \addtogroup LIBRARY
 * \{
 */

#ifndef PROTOCOL_CMDS_H_
#define PROTOCOL_CMDS_H_

#include "programmer.h"

/**
 * \brief Set uart bootloader code for firmware update
 *
 * Binary data specified in this command will be send to device in case only first stage boot
 * loader is present. It this function is not called and second stage bootloader is not on device
 * all other protocol commands will not work.
 *
 * \param [in] code binary data to send to first stage boot loader
 * \param [in] size code size
 *
 */
void set_boot_loader_code(uint8_t *code, size_t size);

/**
 * \brief Get uart bootloader code for firmware update
 *
 * \param [out] code binary data that will be sent to first stage boot loader
 * \param [out] size code size
 *
 */
void get_boot_loader_code(uint8_t **code, size_t * size);

/**
 * \brief Write device RAM memory
 *
 * This function writes device RAM memory with specified data.
 *
 * \param [in] buf binary data to send to device
 * \param [in] size size of buf
 * \param [in] addr device CPU address at device to write data to
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int protocol_cmd_write(const uint8_t *buf, size_t size, uint32_t addr);

/**
 * \brief Read device RAM memory
 *
 * This function reads device RAM memory as seen by device CPU.
 *
 * \param [out] buf buffer for data
 * \param [in] size size of buf in bytes
 * \param [in] addr device CPU address to read from
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int protocol_cmd_read(uint8_t *buf, size_t size, uint32_t addr);

/**
 * \brief Copy memory to QSPI flash
 *
 * This function write flash memory on device with data already present in device RAM memory.
 *
 * \param [in] src_address address in device RAM memory
 * \param [in] size size of memory to copy
 * \param [in] dst_address address in flash to write to (not CPU address)
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int protocol_cmd_copy_to_qspi(uint32_t src_address, size_t size, uint32_t dst_address);

/**
 * \brief Execute code on device
 *
 * This function start execution of code on device.
 *
 * \param [in] address address in device RAM memory to execute
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int protocol_cmd_run(uint32_t address);

/**
 * \brief Erase QSPI flash region
 *
 * This function erases flash memory at specified address.
 *
 * \param [in] address address in flash to start erase
 * \param [in] size size of memory to erase
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int protocol_cmd_erase_qspi(uint32_t address, size_t size);

/**
 * \brief Chip erase QSPI flash
 *
 * This function erases whole flash memory.
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int protocol_cmd_chip_erase_qspi(void);

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
int protocol_cmd_write_otp(uint32_t address, const uint32_t *buf, uint32_t len);

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
int protocol_cmd_read_otp(uint32_t address, uint32_t *buf, uint32_t len);

/**
 * \brief Read data from QSPI
 *
 * \param [in] address address in QSPI
 * \param [out] buf buffer for data
 * \param [in] len length of buffer
 *
 * \return 0 on success, error code on failure
 *
 */
int protocol_cmd_read_qspi(uint32_t address, uint8_t *buf, uint32_t len);

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
int protocol_cmd_is_empty_qspi(unsigned int size, unsigned int start_address, int *ret_number);

/**
 * \brief Read partition table
 *
 * \param [out] buf buffer to store the contents of the partition table
 * \param [out] len the size of buffer in bytes
 *
 * \return 0 on success, error code on failure
 *
 */
int protocol_cmd_read_partition_table(uint8_t **buf, uint32_t *len);

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
int protocol_cmd_read_partition(nvms_partition_id_t id, uint32_t address, uint8_t *buf,
                                                                                uint32_t len);

/**
 * \brief Write NVMS partition with device RAM memory
 *
 * This function writes NVMS partition with specified data.
 *
 * \param [in] id partition id
 * \param [in] dst_address destination address to write data to
 * \param [in] src_address RAM memory source address
 * \param [in] size number of bytes to write
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int protocol_cmd_write_partition(nvms_partition_id_t id, uint32_t dst_address, uint32_t src_address,
                                                                                        size_t size);

/**
 * \brief Boot arbitrary binary.
 *
 * This function boots the device with a provided application binary.
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int protocol_cmd_boot(void);

#endif /* PROTOCOL_CMDS_H_ */

/**
 * \}
 * \}
 * \}
 */
