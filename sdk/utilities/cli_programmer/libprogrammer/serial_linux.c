/**
 ****************************************************************************************
 *
 * @file serial_linux.c
 *
 * @brief Serial port API for Linux
 *
 * Copyright (C) 2015 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#include <stdint.h>
#include <unistd.h>
#include <fcntl.h>
#include <termios.h>
#include <sys/select.h>
#include <time.h>
#include <stdio.h>
#include "crc16.h"
#include "serial.h"
#include "protocol_cmds.h"

static int serial_fd = 0;
static int serial_byte_time_ns; // Time in ns of one byte

int get_baudrate_flag(int baudrate)
{
        int baudrate_flag = B57600;

        switch (baudrate) {
        case 9600:
                baudrate_flag = B9600;
                break;
        case 57600:
                baudrate_flag = B57600;
                break;
        case 19200:
                baudrate_flag = B19200;
                break;
        case 115200:
                baudrate_flag = B115200;
                break;
        case 230400:
                baudrate_flag = B230400;
                break;
        case 500000:
                baudrate_flag = B500000;
                break;
        case 1000000:
                baudrate_flag = B1000000;
                break;
        }

        return baudrate_flag;
}

static void serial_flush(int fd)
{
        uint8_t buf[100];

        while (serial_read(buf, sizeof(buf), 1) > 0) {
        }
}

int serial_open(const char *port, int baudrate)
{
        int baudrate_flag = B57600;
        serial_byte_time_ns = 1000000000 / baudrate * 10;
        struct termios tios;

        serial_fd = open(port, O_RDWR);

        if (serial_fd < 0) {
                return 0;
        }
        serial_flush(serial_fd);

        tcgetattr(serial_fd, &tios);
        cfmakeraw(&tios);

        /*
         * cfmakeraw() clears IXON flag but it's IXOFF which enables flow control in FTDI driver so
         * we need to clear it explicitly here in order to disable XON/XOFF flow control.
         */
        tios.c_iflag &= ~IXOFF;
        /*
         * disable hardware flow control
         */
        tios.c_cflag &= ~CRTSCTS;
        prog_print_log("Using serial port %s at baud rate %d.\n", port, baudrate);
        baudrate_flag = get_baudrate_flag(baudrate);
        cfsetspeed(&tios, baudrate_flag);
        tcsetattr(serial_fd, TCSANOW, &tios);

        return 1;
}

int serial_set_baudrate(int baudrate)
{
        int baudrate_flag = B57600;
        struct termios tios;
        int prev_baudrate = 57600;
        speed_t speed;
        /* Open loop wait here to make sure that last transaction is complete. */
        usleep(200000);
        tcgetattr(serial_fd, &tios);
        speed = cfgetispeed(&tios);
        switch (speed) {
        case B9600:
                prev_baudrate = 9600;
                break;
        case B57600:
                prev_baudrate = 57600;
                break;
        case B19200:
                prev_baudrate = 19200;
                break;
        case B115200:
                prev_baudrate = 115200;
                break;
        case B230400:
                prev_baudrate = 230400;
                break;
        case B500000:
                prev_baudrate = 500000;
                break;
        case B1000000:
                prev_baudrate = 1000000;
                break;
        }
        cfmakeraw(&tios);
        tios.c_iflag &= ~IXOFF;

        prog_print_log("Setting serial port baud rate to %d.\n", baudrate);
        baudrate_flag = get_baudrate_flag(baudrate);
        cfsetspeed(&tios, baudrate_flag);
        tcsetattr(serial_fd, TCSANOW, &tios);
        serial_byte_time_ns = 1000000000 / baudrate * 10;
        return prev_baudrate;
}

int serial_write(const uint8_t *buffer, size_t length)
{
        int written = 0;
        int total = 0;
        struct timespec ts1;
        struct timespec ts2;
        long int expected_time_us = length * (serial_byte_time_ns / 1000);
        long int time_taken_us;
        clock_gettime(CLOCK_REALTIME, &ts1);

        while (length > 0) {
                written = write(serial_fd, buffer + total, length);
                if (written < 0) {
                        return written;
                } else {
                        total += written;
                        length -= written;
                }
        }
        tcdrain(serial_fd);
        clock_gettime(CLOCK_REALTIME, &ts2);
        time_taken_us = (ts2.tv_sec - ts1.tv_sec) * 1000000 + (ts2.tv_nsec - ts1.tv_nsec) / 1000;
        if (time_taken_us + 10000 < expected_time_us) {
                usleep(expected_time_us - time_taken_us);
        }

        return total;
}

int serial_read(uint8_t *buffer, size_t length, uint32_t timeout)
{
        struct timespec ts;
        fd_set rfds;

        ts.tv_sec = timeout / 1000;
        ts.tv_nsec = (timeout % 1000) * 1000000;
        FD_ZERO(&rfds);
        FD_SET(serial_fd, &rfds);

        if (pselect(serial_fd + 1, &rfds, NULL, NULL, &ts, NULL) > 0) {
                return read(serial_fd, buffer, length);
        }

        return 0;
}

void serial_close(void)
{
        if (serial_fd != 0) {
                close(serial_fd);
                serial_fd = 0;
        }
}
