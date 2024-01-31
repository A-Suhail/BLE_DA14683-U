/**
 ****************************************************************************************
 *
 * @file serial.h
 *
 * @brief Serial port API.
 *
 * Copyright (C) 2015-2016 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

/**
 * \addtogroup UTILITIES
 * \{
 * \{
 * \{
 */

#ifndef SERIAL_H_
#define SERIAL_H_

#include <stdint.h>

/**
 * \brief Open serial port
 *
 * \param [in] port Serial port
 * \param [in] baudrate Serial port baudrate
 *
 * \return 1 if port is opened and configured
 *
 */
int serial_open(const char *port, int baudrate);

/**
 * \brief Write to serial port
 *
 * \param [in] buffer Data to send
 * \param [in] length Number of characters to write
 *
 * \return Number of written characters
 *
 */
int serial_write(const uint8_t *buffer, size_t length);

/**
 * \brief Read from serial port
 *
 * \param [out] buffer Received data
 * \param [in] length Number of characters to read
 * \param [in] timeout Time to wait for next character
 *
 * \return Number of read characters
 *
 */
int serial_read(uint8_t *buffer, size_t length, uint32_t timeout);

/**
 * \brief Close serial port
 *
 */
void serial_close(void);

/**
 * \brief Set BAUD rate for an already opened serial.
 *
 * \param [in] baudrate Serial port BAUD rate
 *
 * \return The previously used BAUD rate
 */
int serial_set_baudrate(int baudrate);

#endif /* SERIAL_H_ */

/**
 * \}
 * \}
 * \}
 */
