/**
 ****************************************************************************************
 *
 * @file serial_win.c
 *
 * @brief Serial port API for Windows.
 *
 * Copyright (C) 2015 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#include <windows.h>
#include <stdio.h>
#include <stdint.h>
#include "serial.h"
#include "protocol_cmds.h"

static HANDLE h_serial_port = NULL;
static int serial_byte_time_ns; // Time in ns of one byte

static void serial_flush(HANDLE h)
{
        uint8_t buf[100];

        while (serial_read(buf, sizeof(buf), 1)) {
        }
}

int serial_open(const char *port, int baudrate)
{
        char serial_port[20];
        DCB dcb_port;
        serial_byte_time_ns = 1000000000 / baudrate * 10;

        if (!strncmp("\\\\.\\", port, 7)) {
                strcpy(serial_port, port);
        } else {
                sprintf(serial_port, "\\\\.\\%s", port);
        }

        prog_print_log("Using serial port %s at baud rate %d.\n", port, baudrate);

        h_serial_port = CreateFile(serial_port, GENERIC_READ | GENERIC_WRITE, 0, NULL,
                OPEN_EXISTING, 0, NULL);

        if (h_serial_port == INVALID_HANDLE_VALUE) {
                return 0;
        }

        serial_flush(h_serial_port);

        // Length initialization of DCB
        dcb_port.DCBlength = sizeof(dcb_port);
        // Get the default settings of port configuration
        GetCommState(h_serial_port, &dcb_port);

        dcb_port.BaudRate = baudrate;
        dcb_port.ByteSize = 8;
        dcb_port.Parity = NOPARITY;
        dcb_port.StopBits = ONESTOPBIT;

        dcb_port.fBinary = TRUE;
        dcb_port.fParity = FALSE;
        dcb_port.fOutxCtsFlow = FALSE;
        dcb_port.fOutxDsrFlow = FALSE;
        dcb_port.fDtrControl = DTR_CONTROL_ENABLE;
        dcb_port.fDsrSensitivity = FALSE;
        dcb_port.fTXContinueOnXoff = TRUE;
        dcb_port.fOutX = FALSE;
        dcb_port.fInX = FALSE;
        dcb_port.fErrorChar = FALSE;
        dcb_port.fNull = FALSE;
        dcb_port.fRtsControl = RTS_CONTROL_ENABLE;
        dcb_port.fAbortOnError = FALSE;

        if (!SetCommState(h_serial_port, &dcb_port)) {
                prog_print_err("Unable to configure serial port.\n");
                return -1;
        }

        return 1;
}

int serial_set_baudrate(int baudrate)
{
        DCB dcb_port;
        int prev_baudrate;

        GetCommState(h_serial_port, &dcb_port);

        prev_baudrate = (int) dcb_port.BaudRate;

        prog_print_log("Setting serial port baud rate to %d.\n", baudrate);
        /* Open loop wait here to make sure that last transaction is complete. */
        Sleep(200);
        dcb_port.BaudRate = baudrate;
        dcb_port.ByteSize = 8;
        dcb_port.Parity = NOPARITY;
        dcb_port.StopBits = ONESTOPBIT;

        dcb_port.fBinary = TRUE;
        dcb_port.fParity = FALSE;
        dcb_port.fOutxCtsFlow = FALSE;
        dcb_port.fOutxDsrFlow = FALSE;
        dcb_port.fDtrControl = DTR_CONTROL_ENABLE;
        dcb_port.fDsrSensitivity = FALSE;
        dcb_port.fTXContinueOnXoff = TRUE;
        dcb_port.fOutX = FALSE;
        dcb_port.fInX = FALSE;
        dcb_port.fErrorChar = FALSE;
        dcb_port.fNull = FALSE;
        dcb_port.fRtsControl = RTS_CONTROL_ENABLE;
        dcb_port.fAbortOnError = FALSE;

        if (!SetCommState(h_serial_port, &dcb_port)) {
                prog_print_err("Unable to configure serial port.\n");
                return -1;
        }
        serial_byte_time_ns = 1000000000 / baudrate * 10;
        return prev_baudrate;
}

static int serial_timeouts(DWORD timeout)
{
        COMMTIMEOUTS comm_timeouts;

        if (!GetCommTimeouts(h_serial_port, &comm_timeouts)) {
                prog_print_err("Unable to get timeouts.\n");
                return -1;
        }

        comm_timeouts.ReadTotalTimeoutConstant = timeout;
        comm_timeouts.ReadTotalTimeoutMultiplier = 0;
        comm_timeouts.ReadIntervalTimeout = 0;

        if (!SetCommTimeouts(h_serial_port, &comm_timeouts)) {
                prog_print_err("Unable to set timeouts.\n");
                return -1;
        }

        return 1;
}

int serial_write(const uint8_t *buffer, size_t length)
{
        DWORD bytes_written, t_start, t_end;
        long int expected_time_us = length * (serial_byte_time_ns / 1000);
        long int time_taken_ms;

        t_start = GetTickCount();

        if (!WriteFile(h_serial_port, buffer, length, &bytes_written, NULL)) {
                return -1;
        }

        t_end = GetTickCount();

        time_taken_ms = t_end - t_start;
        if (time_taken_ms + 10 < expected_time_us / 1000) {
                Sleep(expected_time_us / 1000 - time_taken_ms);
        }

        return (int) bytes_written;
}

int serial_read(uint8_t *buffer, size_t length, uint32_t timeout)
{
        DWORD bytes_transferred;

        serial_timeouts(timeout);

        if (!ReadFile(h_serial_port, buffer, length, &bytes_transferred, NULL)) {
                return -1;
        }

        return (int) bytes_transferred;
}

void serial_close(void)
{
        if (h_serial_port != NULL) {
                CloseHandle(h_serial_port);
                h_serial_port = NULL;
        }
}