/**
 ****************************************************************************************
 *
 * @file gdb_server_cmds.h
 *
 * @brief GDB Server interface header file
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

#ifndef GDB_SERVER_CMDS_H_
#define GDB_SERVER_CMDS_H_

/**
 * \brief Initialize GDB Server
 *
 * \note 0 is returned if initialization was done properly, but GDB Server's PID is unavailable
 *
 * \param [in] gdb_server_conf GDB Server configuration
 *
 * \returns PID of used GDB Server instance or 0 on success, negative value with error code on failure
 *
 */
int gdb_server_initialization(const prog_gdb_server_config_t *gdb_server_conf);

/**
 * \brief Set GDB Server bootloader code for firmware update
 *
 *
 * Binary data specified in this command will be sent to device.
 *
 * \param [in] code binary bootloader data
 * \param [in] size code size
 *
 */
void gdb_server_set_boot_loader_code(uint8_t *code, size_t size);

/**
 * \brief Get GDB Server bootloader code for firmware update
 *
 * \param [out] code binary bootloader data
 * \param [out] size code size
 *
 */
void gdb_server_get_boot_loader_code(uint8_t **code, size_t *size);

/**
 * \brief Write device memory
 *
 * This function writes device RAM with specified data.
 *
 * \param [in] buf binary data to send to device
 * \param [in] size size of buf
 * \param [in] addr RAM address to write data to
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int gdb_server_cmd_write(const uint8_t *buf, size_t size, uint32_t addr);

/**
 * \brief Read device memory without bootloader
 *
 * This function reads device memory as seen by device CPU. It doesn't require to have bootloader
 * running.
 *
 * \param [out] buf buffer for data
 * \param [in] size size of buf in bytes
 * \param [in] addr RAM address to read from
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int gdb_server_cmd_direct_read(uint8_t *buf, size_t size, uint32_t addr);

/**
 * \brief Read device memory
 *
 * This function reads device memory as seen by device CPU.
 *
 * \param [out] buf buffer for data
 * \param [in] size size of buf in bytes
 * \param [in] addr RAM address to read from
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int gdb_server_cmd_read(uint8_t *buf, size_t size, uint32_t addr);

/**
 * \brief Copy memory to QSPI flash
 *
 * This function programs QSPI flash memory with data already present in device RAM.
 *
 * \param [in] src_address address in device RAM
 * \param [in] size size of memory to copy
 * \param [in] dst_address offset in flash to write to
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int gdb_server_cmd_copy_to_qspi(uint32_t src_address, size_t size, uint32_t dst_address);

/**
 * \brief Boot arbitrary binary.
 *
 * This function boots the device with a provided application binary.
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int gdb_server_cmd_run(uint32_t address);

/**
 * \brief Erase QSPI flash region
 *
 * This function erases flash at specified offset.
 *
 * \param [in] address address in flash to start erase
 * \param [in] size size of memory to erase
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int gdb_server_cmd_erase_qspi(uint32_t address, size_t size);

/**
 * \brief Chip erase QSPI flash
 *
 * This function erases whole flash memory.
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int gdb_server_cmd_chip_erase_qspi(void);

/**
 * \brief Write data to OTP
 *
 * \param [in] address address of 64-bit cell in OTP
 * \param [in] buf words to be written
 * \param [in] len number of words in buffer
 *
 * \return 0 on success, error code on failure
 *
 */
int gdb_server_cmd_write_otp(uint32_t address, const uint32_t *buf, uint32_t len);

/**
 * \brief Read data from OTP
 *
 * \param [in] address address of 64-bit cell in OTP
 * \param [out] buf buffer for read words
 * \param [in] len number of words to be read
 *
 * \return 0 on success, error code on failure
 *
 */
int gdb_server_cmd_read_otp(uint32_t address, uint32_t *buf, uint32_t len);

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
int gdb_server_cmd_read_qspi(uint32_t address, uint8_t *buf, uint32_t len);

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
int gdb_server_cmd_is_empty_qspi(unsigned int size, unsigned int start_address, int *ret_number);

/**
 * \brief Read partition table
 *
 * \param [out] buf buffer to store the contents of the partition table
 * \param [out] len the size of buffer in bytes
 *
 * \return 0 on success, error code on failure
 *
 */
int gdb_server_cmd_read_partition_table(uint8_t **buf, uint32_t *len);

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
int gdb_server_cmd_read_partition(nvms_partition_id_t id, uint32_t address, uint8_t *buf,
                                                                                uint32_t len);

/**
 * \brief Write NVMS partition with device memory
 *
 * This function writes NVMS partition with specified data.
 *
 * \param [in] id partition id
 * \param [in] dst_address destination address to write data to
 * \param [in] src_address RAM source address
 * \param [in] size number of bytes to write
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int gdb_server_cmd_write_partition(nvms_partition_id_t id, uint32_t dst_address,
                                                                uint32_t src_address, size_t size);

/**
 * \brief Boot arbitrary binary.
 *
 * This function boots the device with a provided application binary.
 *
 * \returns 0 on success, negative value with error code on failure
 *
 */
int gdb_server_cmd_boot(void);

/**
 * \brief Close GDB Server interface
 *
 * Function stops GDB Server instance with given pid.
 *
 * \note This function doesn't close opened socket, gdb_server_disconnect() function should be used
 * before calling this function.
 * \note If no_kill_mode was set to NO_KILL_ALL or NO_KILL_DISCONNECT during interface
 * initialization then GDB Server process will not be killed.
 *
 * \param [in] pid PID of the selected GDB Server
 *
 * \sa gdb_server_disconnect
 *
 */
void gdb_server_close(int pid);

/**
* \brief Invalidate stub
*
* This function ensures that the stub will be reloaded next time.
*
*/
void gdb_invalidate_stub(void);

/**
 * \brief Connect to GDB Server
 *
 * \note After usage of this function the gdb_server_disconnect function should be used for cleanup.
 *
 * \param [in] host_name host name
 * \param [in] port port number
 * \param [in] reset perform platform reset flag
 *
 * \return 0 on success, error code on failure
 *
 */
int gdb_server_connect(const char *host_name, int port, bool reset);

/**
 * \brief Disconnect with GDB Server instance
 *
 * Function closes socket which is used for communication with GDB Server.
 *
 * \note If socket was not opened earlier, then function will do nothing.
 *
 */
void gdb_server_disconnect();

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
prog_gdb_server_info_t *gdb_server_get_instances(const char *gdb_server_cmd);

#endif /* GDB_SERVER_CMDS_H_ */

/**
 * \}
 * \}
 * \}
 */
