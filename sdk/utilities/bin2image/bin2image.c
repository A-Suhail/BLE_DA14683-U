/**
 ****************************************************************************************
 *
 * @file bin2image.c
 *
 * @brief Utility for creating a bootable image from an executable raw binary.
 *
 * Copyright (C) 2015-2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */
#define _XOPEN_SOURCE 700
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#ifdef _MSC_VER
#include <io.h>
#else
#include <unistd.h>
#endif
#ifdef __linux__
#include <endian.h>
#endif
#include <string.h>
#include <errno.h>
#include <time.h>

#include "programmer.h"

#ifdef _MSC_VER
#  define RW_RET_TYPE	int
#  define snprintf	_snprintf
#  define S_IRUSR	S_IREAD
#  define S_IWUSR	S_IWRITE
#else
#  define RW_RET_TYPE	ssize_t
#endif


#define BIN2IMAGE_VERSION "1.13"

static void usage(const char* my_name)
{
	fprintf(stderr,
		"Version: " BIN2IMAGE_VERSION "\n"
		"\n"
		"  %s <type> <binary_file> <image_file>"
		" [DA14680-01|DA14681-01] "
		"\n"
                "  Convert the executable binary file 'binary_file' to a "
                "bootable image file 'image_file'.\n"
                "  The 'type' argument defines what kind of image to be "
                "generated:\n"
                "    qspi_cached    		QSPI flash image for cached mode (production & development paths)\n"
		"    qspi_mirrored  		QSPI flash image for mirrored mode (production path only)\n"
		"    qspi_single_mirrored   	QSPI flash image for mirrored mode (development path only, qspi operating in single mode)\n"
		"    otp_cached     		OTP image for cached mode\n"
		"    otp_mirrored   		OTP image for mirrored mode\n"
                "\n"
		"  Note: For cached mode images, the MSBit of the length is set to 1\n"
		"\n",
		my_name);
}


static int safe_write(int fd, const void* buf, size_t len)
{
	RW_RET_TYPE n;
	const uint8_t* _buf = buf;

	do {
		n = write(fd, _buf, len);
		if (n > 0) {
			len -= n;
			_buf += n;
		} else if (n < 0  &&  errno != EINTR)
			return -1;
	} while (len);

	return 0;
}


static int safe_read(int fd, void* buf, size_t len)
{
	RW_RET_TYPE n;
	uint8_t* _buf = buf;

	do {
		n = read(fd, _buf, len);
		if (n > 0) {
			len -= n;
			_buf += n;
		} else if (n == 0) {
			return len;  /* EOF: return number of bytes missing */
		} else if (n < 0  &&  errno != EINTR) {
			return -1;
		}
	} while (len);

	return 0;
}

int main(int argc, const char* argv[])
{
	int inf = -1, outf = -1;
	int oflags, res = EXIT_FAILURE;
        int binary_file_size;                   /* Input binary file size */
        int image_size;                         /* Output image size */
        uint8_t *buf = NULL;
	struct stat sbuf;
	char chip_ver[6] = "680BB";             /* Step for BB */
	image_type_t type;
	image_mode_t mode;

	if (argc < 4 ) {
		usage(argv[0]);
		exit(EXIT_FAILURE);
	}

	/* parse image type */
	if (strcmp(argv[1], "qspi_cached") == 0) {
		type = IMG_QSPI;
		mode = IMG_CACHED;
	} else if (strcmp(argv[1], "qspi_mirrored") == 0) {
		type = IMG_QSPI;
		mode = IMG_MIRRORED;
	} else if (strcmp(argv[1], "qspi_single_mirrored") == 0) {
		type = IMG_QSPI_S;
		mode = IMG_MIRRORED;
	} else if (strcmp(argv[1], "otp_cached") == 0) {
		type = IMG_OTP;
		mode = IMG_CACHED;
	} else if (strcmp(argv[1], "otp_mirrored") == 0) {
		type = IMG_OTP;
		mode = IMG_MIRRORED;
	} else {
		fprintf(stderr, "Invalid image type '%s'\n", argv[1]);
		usage(argv[0]);
		goto cleanup_and_exit;
	}
        if (argc > 4) {
                if ((strcmp(argv[4], "DA14680-01") == 0) ||
                        (strcmp(argv[4], "DA14681-01") == 0)) {
                        strcpy(chip_ver, "680AH");
                } else {
                        usage(argv[0]);
                        goto cleanup_and_exit;
                }
        }
	/* open input file and get its size */
	oflags = O_RDONLY;
#ifdef O_BINARY
	oflags |= O_BINARY;
#endif
	inf = open(argv[2], oflags);
	if (-1 == inf) {
		perror(argv[2]);
		goto cleanup_and_exit;
	}
	if (fstat(inf, &sbuf)) {
		perror(argv[2]);
		goto cleanup_and_exit;
	}
	binary_file_size = (int) sbuf.st_size;

	/* open the output file */
	oflags = O_RDWR | O_CREAT | O_TRUNC;
#ifdef O_BINARY
	oflags |= O_BINARY;
#endif
	outf = open(argv[3], oflags, S_IRUSR | S_IWUSR);
	if (-1 == outf) {
		perror(argv[3]);
		goto cleanup_and_exit;
	}

        buf = malloc(binary_file_size + 16);
        if (NULL == buf) {
                fprintf(stderr, "Memory allocation error\n");
                goto cleanup_and_exit;
        }

        safe_read(inf, buf, binary_file_size);

        /* Request libprogrammer to prepare image */
        image_size = prog_make_image(buf, binary_file_size, chip_ver,
                                type, mode, buf, binary_file_size + 16, NULL);

        if (image_size < 0) {
                fprintf(stderr, "Preparing image failed: %s (%d)\n",
                                                prog_get_err_message(image_size), image_size);
                goto cleanup_and_exit;
        }

        safe_write(outf, buf, image_size);

	res = EXIT_SUCCESS;

cleanup_and_exit:
        if (buf) {
                free(buf);
        }

        if (outf != -1) {
		if (close(outf))
			perror(argv[3]);
	}

	if (inf != -1) {
		if (close(inf))
			perror(argv[2]);
	}

	exit(res);
}

