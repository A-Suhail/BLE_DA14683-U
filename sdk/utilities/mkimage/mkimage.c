/**
 ****************************************************************************************
 *
 * @file mkimage.c
 *
 * @brief Utility for creating a firmware image.
 *
 * Copyright (C) 2015-2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */
#define _XOPEN_SOURCE 700
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
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

#include "image.h"
#include "mkimage.h"

#ifdef _MSC_VER
#  define RW_RET_TYPE   int
#  define snprintf      snprintf
#  define S_IRUSR       S_IREAD
#  define S_IWUSR       S_IWRITE
#  define inline        __inline
#else
#  define RW_RET_TYPE   ssize_t
#endif

/* If 'O_BINARY' flag is not define then use empty flag */
#ifndef O_BINARY
#define O_BINARY        0
#endif

/* pre-determined cryptography key and IV */
static uint8_t def_key[16] = {
        0x06, 0xa9, 0x21, 0x40, 0x36, 0xb8, 0xa1, 0x5b,
        0x51, 0x2e, 0x03, 0xd5, 0x34, 0x12, 0x00, 0x06
};
static uint8_t def_iv[16] = {
        0x3d, 0xaf, 0xba, 0x42, 0x9d, 0x9e, 0xb4, 0x30,
        0xb4, 0x22, 0xda, 0x80, 0x2c, 0x9f, 0xac, 0x41
};

#define MKIMAGE_VERSION "1.12"

/* Number of asymmetric key generation tries */
#define GEN_RETRY_NUM   10

static void usage(const char* my_name)
{
        fprintf(stderr,
                "Version: " MKIMAGE_VERSION "\n"
                "\n"
                "\n"
                "Usage depends on the option selected. Possible parameters:\n"
                "#1 single           - generate single image\n"
                "#2 multi            - generate multi image - output image contains 2 input\n"
                "                      images\n"
                "#3 gen_sym_key      - generate symmetric key or keys\n"
                "#4 gen_asym_key     - generate asymmetric key or keys\n"
                "#5 secure           - generate signed image file\n"
                "\n"
                "\n"
                "Usage case #1:\n"
                "mkimage single <in_file> <version_file> <out_file> [enc [<key> <iv>]]\n"
                "\n"
                "parameters:\n"
                "  in_file         input binary file which is converted to output image\n"
                "  version_file    version file which contains version, timestamp and\n"
                "                  housekeeping information (e.g. sw_version.h)\n"
                "  out_file        output image file\n"
                "  enc             use image encryption (AES, CBC)\n"
                "  key             encryption key. String of 32 hex characters (without any\n"
                "                  prefix). If no key is given, the default value is\n"
                "                  used\n"
                "  iv              initialization vector. String of 32 hex characters (without\n"
                "                  any prefix). If no initialization vector is given,\n"
                "                  the default value is used\n"
                "\n"
                "note:\n"
                "  The 'version_file' is usually called sw_version.h\n"
                "  and this program looks in it for definitions like below:\n"
                "\n"
                "  #define BLACKORCA_SW_VERSION \"v_1.0.0.1\"\n"
                "  #define BLACKORCA_SW_VERSION_DATE \"2015-03-11 14:04 \"\n"
                "\n"
                "example:\n"
                "  mkimage single pxp_reporter.bin sw_version.h output.img\n"
                "  mkimage single pxp_reporter.bin sw_version.h output.img enc\n"
                "         123456789aBCdef1234567890deeac27 BCA123456789aBCdef1234567890deea\n"
                "\n"
                "\n"
                "Usage case #2:\n"
                "mkimage multi <destination> [<bootloader>] <in_image1> <offset1> <in_image2>\n"
                "              <offset2> <offset3> [cfg <offset4>] <out_file>\n"
                "\n"
                "parameters:\n"
                "  destinations    where out_file is loaded - 'spi' or 'eeprom'\n"
                "  bootloader      bootloader file at offset 0, if provided\n"
                "  in_image1       first input image file loaded at <offset1>\n"
                "  offset1         offset where <in_image1> is loaded (look at note below)\n"
                "  in_image2       second input image file loaded at <offset2>\n"
                "  offset2         offset where <in_image2> is loaded\n"
                "                  (>= <offset1> + size of <in_image1>)\n"
                "  offset3         offset where product header is loaded\n"
                "                  (>= <offset2> + size of <in_image2>)\n"
                "  cfg             add configuration to output image\n"
                "  offset4         offset where configuration is loaded\n"
                "  out_file        output image file\n"
                "\n"
                "note:\n"
                "  The offsets can be given either as decimal or hex numbers.\n"
                "  If bootloader is provided <offset1> need to be given at least\n"
                "  header size + bootloader size. Header size is equal 8 bytes for 'spi'\n"
                "  destination and 32 bytes for 'eeprom'.\n"
                "\n"
                "example:\n"
                "  mkimage multi spi pxp_reporter.bin 0 pxp_reporter_2.bin 97056 194112 output.img\n"
                "  mkimage multi spi bootloader pxp_reporter.bin 9000 pxp_reporter_2.bin 106056 203112\n"
                "        output.img\n"
                "  mkimage multi eeprom bootloader pxp_reporter.bin 9024 pxp_reporter_2.bin 106080 203136\n"
                "        output.img\n"
                "\n"
                "\n"
                "Usage case #3:\n"
                "mkimage gen_sym_key [<keys_count> [<key_length>]]\n"
                "\n"
                "parameters:\n"
                "  keys_count      number of generated symmetric keys (> 0, default: 1)\n"
                "  key_length      length of generated symmetric keys (> 0, default: 32 bytes)\n"
                "\n"
                "example:\n"
                "  mkimage gen_sym_key\n"
                "  mkimage gen_sym_key 3 16\n"
                "\n"
                "Usage case #4:\n"
                "mkimage gen_asym_key <elliptic_curve> [<keys_count>]\n"
                "\n"
                "parameters:\n"
                "  elliptic_curve  Key pair is generated using elliptic curve. Supported elliptic\n"
                "                  curves:\n"
                "                  * NIST:         SECP192R1, SECP224R1, SECP256R1, SECP384R1\n"
                "                  * Brainpool:    BP256R1, BP384R1, BP512R1\n"
                "                  * Koblitz:      SECP192K1, SECP224K1, SECP256K1\n"
                "                  * Curve25519:   CURVE25519\n"
                "                  * Edward:       EDWARDS25519\n"
                "  keys_count      number of generated asymmetric keys (> 0, default: 1)\n"
                "\n"
                "example:\n"
                "  mkimage gen_asym_key SECP192R1\n"
                "  mkimage gen_asym_key BP512R1 6\n"
                "\n"
                "\n"
                "Usage case #5:\n"
                "mkimage secure <in_file> <version_file> <out_file> <elliptic_curve> <hash>\n"
                "               <private_key> <key_id> [rev <cmd>] [min_ver [<version>]]\n"
                "\n"
                "parameters:\n"
                "  in_file         input binary file which is converted to output image\n"
                "  version_file    version file which contains version, timestamp and\n"
                "                  housekeeping information (e.g. sw_version.h)\n"
                "  out_file        output image file\n"
                "  elliptic_curve  elliptic curve used in ECDSA or EdDSA algorithms to generate\n"
                "                  signature. Supported elliptic curves:\n"
                "                  * For ECDSA:    SECP192R1, SECP224R1, SECP256R1\n"
                "                  * For EdDSA     EDWARDS25519\n"
                "  hash            Supported hash method:\n"
                "                  * For ECDSA:    SHA-224, SHA-256, SHA-384, SHA-512\n"
                "                  * For EdDSA:    SHA-512\n"
                "  private_key     private key which is used in ECDSA/EdDSA - it must have\n"
                "                  proper (for chosen elliptic curve) length. This key can be\n"
                "                  generated by 'gen_asym_key' command with the same\n"
                "                  <elliptic_curve> parameter.\n"
                "  key_id          index or memory address of the key which should be used for\n"
                "                  signature validation by bootloader. Supported key ID:\n"
                "                  - 0, 1, 2, 3\n"
                "  rev             use public key or keys revocation command\n"
                "  cmd             public key or keys revocation command which should be revoked\n"
                "                  (index or memory address). If more than one key is passed,\n"
                "                  parameter should be given in quotation marks\n"
                "                  (look at an example). Supported values:\n"
                "                  - 1, 2, 3\n"
                "  min_ver         use minimal version - default or given by user\n"
                "  version         minimal version of firmware. String value which contains two\n"
                "                  values separated by dot characters (e.g. 314.033 or 103.13).\n"
                "                  Every additional dots and values after it will be skipped\n"
                "                  (e.g. 343.3234.235.334 will be taken as 343.3234).\n"
                "                  Maximum value of version between dots is 65535 (0xFFFF) ->\n"
                "                  (65535.65535). If this value is not given, by default it is\n"
                "                  taken from <version_file>\n"
                "\n"
                "example:\n"
                "  mkimage secure pxp_reporter.bin sw_version.h output.img SECP192R1 SHA-224\n"
                "         BD9A333C56A9DBC99C4E9D71DE52E81F06CF90E383DE3BCF 1\n"
                "  mkimage secure pxp_reporter.bin sw_version.h output.img SECP256R1 SHA-384\n"
                "         6A34675F2F5885A4EDC9011D7B815E5999AE578D7804266A7383D79F72949EDD 2\n"
                "         rev \"1 3\" min_ver 23.53\n");
}

static inline void store32(uint8_t* buf, uint32_t val)
{
#ifdef MKIMAGE_LITTLE_ENDIAN
        buf[0] = val & 0xff;
        val >>= 8;
        buf[1] = val & 0xff;
        val >>= 8;
        buf[2] = val & 0xff;
        val >>= 8;
        buf[3] = val & 0xff;
#else
        buf[3] = val & 0xff;
        val >>= 8;
        buf[2] = val & 0xff;
        val >>= 8;
        buf[1] = val & 0xff;
        val >>= 8;
        buf[0] = val & 0xff;
#endif
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


static int set_active_image(int img,unsigned char active){
        struct image_header hdr;
        if (safe_read(img,&hdr,sizeof(struct image_header))<0)
                return -1;
        hdr.image_id = active;

        if (lseek(img, 0, SEEK_SET)<0)
                return -1;
        if (safe_write(img,&hdr,sizeof(struct image_header))<0)
                return -1;
        if (lseek(img, 0, SEEK_SET)<0)
                return -1;
        return 0;
}

static int append_file_csum(int outf, int inf, uint8_t* _csum)
{
        RW_RET_TYPE n;
        uint8_t csum = 0;
        uint8_t copy_buf_clr[16];

        do {
                size_t count;
                int size;
                const uint8_t* data;

                count = sizeof copy_buf_clr;
                n = read(inf, copy_buf_clr, count);
                if (n < 0) {
                        if (EINTR == errno)
                                continue;
                        else {
                                fprintf(stderr, "Error while reading input image\r\n");
                                return -1;
                        }
                }
                if (safe_write(outf, copy_buf_clr, n)) {
                        fprintf(stderr, "writing image\r\n");
                        return -1;
                }

                size = n;
                data = copy_buf_clr;
                while (size--)
                        csum ^= *data++;
        } while (n != 0);

        if (_csum != NULL)
                *_csum = csum;

        return 0;
}

static int parse_hex_string(const char s[], uint8_t buf[], const int len)
{
        int s_i, buf_i;
        char digit[3];
        unsigned long val;
        char* end_ptr;

        digit[2] = '\0';
        for (s_i = buf_i = 0; buf_i < len; s_i += 2, buf_i++) {
                digit[0] = s[s_i];
                digit[1] = s[s_i + 1];
                val = strtol(digit, &end_ptr, 16);
                if (*end_ptr)
                        return -1;  /* should be non-NIL */
                buf[buf_i] = (uint8_t)val;
        }

        return 0;
}

/*
 * Read whole file from a given path. 'flags' - file open flags. 'buffer_size' - read buffer size.
 * 'buffer_size' - allocated buffer with data, should be freed after use.
 */
static bool read_whole_file(const char *path, int flags, size_t *buffer_size, uint8_t **buffer)
{
        struct stat stat_data;
        int fd;
        size_t file_size;

        *buffer = NULL;
        fd = open(path, flags);

        if (fd < 0) {
                /* Cannot open file */
                return false;
        }

        if (fstat(fd, &stat_data)) {
                /* Cannot 'stat' file */
                close(fd);
                return false;
        }

        file_size = stat_data.st_size;

        *buffer = malloc(file_size);

        if (!*buffer) {
                /* Allocation error */
                close(fd);
                return false;
        }

        if (safe_read(fd, *buffer, file_size)) {
                close(fd);
                free(*buffer);
                *buffer = NULL;
                return false;
        }

        *buffer_size = file_size;

        close(fd);

        return true;
}

static int create_single_image(int argc, const char* argv[])
{
        int argix = 5;
        mkimage_status_t lib_status;
        int status = EXIT_FAILURE;
        uint8_t key[16];
        uint8_t iv[16];
        const uint8_t *aes_key = NULL;
        const uint8_t *aes_iv = NULL;
        int out_fd = -1;
        uint8_t *in_buf = NULL, *ver_buf = NULL, *out_buf = NULL;
        size_t in_size, ver_size, out_size;

        if (argc != argix && argc != argix + 1 && argc != argix + 3) {
                usage(argv[0]);
                return EXIT_FAILURE;
        }

        if (argc > argix) {
                if (!strcmp(argv[argix], "enc")) {
                        if (argc == (argix + 1)) {
                                aes_key = def_key;
                                aes_iv = def_iv;
                        } else {
                                if (strlen(argv[argix + 1]) != 32  ||
                                        strlen(argv[argix + 2]) != 32) {
                                        usage(argv[0]);
                                        return EXIT_FAILURE;
                                }
                                if (parse_hex_string(argv[argix + 1], key, sizeof(key))) {
                                        fprintf(stderr, "Invalid key\n");
                                        usage(argv[0]);
                                        return EXIT_FAILURE;
                                }
                                if (parse_hex_string(argv[argix + 2], iv, sizeof(iv))) {
                                        fprintf(stderr, "Invalid iv\n");
                                        usage(argv[0]);
                                        return EXIT_FAILURE;
                                }

                                aes_key = key;
                                aes_iv = iv;
                        }
                } else {
                        usage(argv[0]);
                        return EXIT_FAILURE;
                }
        }

        /* Read input file */
        if (!read_whole_file(argv[2], O_RDONLY | O_BINARY, &in_size, &in_buf) || in_size == 0 ||
                                                                                        !in_buf) {
                fprintf(stderr, "cannot read file - %s\r\n", argv[2]);
                goto done;
        }

        /* Read version file */
        if (!read_whole_file(argv[3], O_RDONLY | O_BINARY, &ver_size, &ver_buf) || ver_size == 0 ||
                                                                                        !ver_buf) {
                fprintf(stderr, "cannot read file - %s\r\n", argv[3]);
                goto done;
        }

        /* Open output file */
        out_fd = open(argv[4], O_RDWR | O_CREAT | O_TRUNC | O_BINARY, S_IRUSR | S_IWUSR);
        if (out_fd < 0) {
                fprintf(stderr, "cannot open file - %s\r\n", argv[4]);
                goto done;
        }

        lib_status = mkimage_create_single_image(in_size, in_buf, ver_size, ver_buf, aes_key,
                                                                aes_iv, &out_buf, &out_size);

        if (lib_status != MKIMAGE_STATUS_OK) {
                fprintf(stderr, "cannot create single image - %s\r\n",
                                                                mkimage_status_message(lib_status));
                goto done;
        }

        if (safe_write(out_fd, out_buf, out_size)) {
                fprintf(stderr, "cannot write to file - %s\r\n", argv[4]);
                goto done;
        }

        status = EXIT_SUCCESS;

done:
        /* Close output file */
        if (out_fd >= 0) {
                close(out_fd);
        }

        /* Free buffers */
        free(in_buf);
        free(ver_buf);
        free(out_buf);

        return status;
}


static int parse_offset(const char* s, unsigned* offset)
{
        long val;
        char* end_ptr;

        /* define a "rational" upper limit of the multi-part image size */
#ifndef MULTI_IMAGE_LIMIT
#  define MULTI_IMAGE_LIMIT     0x100000
#endif

        val = strtol(s, &end_ptr, 0);
        if (end_ptr == s) {
                fprintf(stderr, "Invalid offset '%s'.\n", s);
                return -1;
        }

        if (val > MULTI_IMAGE_LIMIT) {
                fprintf(stderr, "Offset '%ld' is suspiciously high and is "
                        "rejected.\n"
                        "If you really need such an offset, set "
                        "MULTI_IMAGE_LIMIT appropriately.\n", val);
                return -1;
        }

        *offset = val;

        return 0;
}

static int add_padding(int outf, const unsigned count, const uint8_t pad)
{
        unsigned i;
        RW_RET_TYPE n;

        for (i = 0; i < count; i++) {
                do {
                        n = write(outf, &pad, 1);
                        if (n < 0  &&  errno != EINTR)
                                return -1;
                } while (n < 1);
        }

        return 0;
}


static int create_multi_image(int argc, const char* argv[])
{
        enum multi_options {
                SPI = 1,
                EEPROM = 2,
                BOOTLOADER = 4,
                CONFIG = 8
        };
        unsigned options = 0;
        int oflags, arg_base = 3, arg_off = 0, res = EXIT_FAILURE;
        int outf = -1, bloader = -1, img1 = -1, img2 = -1;
        unsigned off1, off2, off3, cfg_off;
        off_t offset;
        struct an_b_001_spi_header spi_hdr;
        struct an_b_001_i2c_header i2c_hdr;
        struct product_header p_hdr;
        struct stat sbuf;
        uint8_t pad_byte;

        /* determine if
         *  - bootloader image is given
         *  - configuration offset is defined
         */
        if (9 == argc) {
                options &= ~(BOOTLOADER | CONFIG);
        }
        else if (10 == argc) {
                options |= BOOTLOADER;
                arg_base++;
        }
        else if (11 == argc) {
                options |= CONFIG;
                arg_off += 2;
        }
        else if (12 == argc) {
                options |= BOOTLOADER | CONFIG;
                arg_base++;
                arg_off += 2;
        }
        else {
                fprintf(stderr, "Invalid number of arguments.\n");
                usage(argv[0]);
                return EXIT_FAILURE;
        }

        /* determine type of multi-part image */
        if (!strcmp(argv[2], "spi"))
                options |= SPI;
        else if (!strcmp(argv[2], "eeprom"))
                options |= EEPROM;
        else {
                fprintf(stderr, "Unkwown multi-part image type '%s'.\n",
                        argv[2]);
                usage(argv[0]);
                return EXIT_FAILURE;
        }
        if (options & SPI)
                pad_byte = 0xff;
        else
                pad_byte = 0xff;

        /* parse offsets */
        if (parse_offset(argv[arg_base + 1], &off1))
                return EXIT_FAILURE;
        if (parse_offset(argv[arg_base + 3], &off2))
                return EXIT_FAILURE;
        if (parse_offset(argv[arg_base + 4], &off3))
                return EXIT_FAILURE;
        if (!(off1 < off2  &&  off2 < off3)) {
                if (off3 < off1) {
                        fprintf(stderr, "Product header will be placed before img1");
                }
                else {
                        fprintf(stderr, "Inconsistent offsets 'off1'=%u, 'off2'=%u, "
                                "'off3'=%u\n", off1, off2, off3);
                        return EXIT_FAILURE;
                }
        }

        /* parse configuration offset */
        if (options & CONFIG) {
                if (strcmp(argv[arg_base + 5], "cfg")) {
                        usage(argv[0]);
                        return EXIT_FAILURE;
                }
                if (parse_offset(argv[arg_base + 6], &cfg_off))
                        return EXIT_FAILURE;
        }
        else {
                cfg_off = 0xffffffff;
        }

        /* open the input files */
        oflags = O_RDWR;
#ifdef O_BINARY
        oflags |= O_BINARY;
#endif

        if (options & BOOTLOADER) {
                bloader = open(argv[3], oflags);
                if (-1 == bloader) {
                        fprintf(stderr, "%s\r\n", argv[3]);
                        goto cleanup_and_exit;
                }
        }

        img1 = open(argv[arg_base], oflags);
        if (-1 == img1) {
                fprintf(stderr, "%s\r\n", argv[arg_base]);
                goto cleanup_and_exit;
        }

        img2 = open(argv[arg_base + 2], oflags);
        if (-1 == img2) {
                fprintf(stderr, "%s\r\n", argv[arg_base + 2]);
                goto cleanup_and_exit;
        }

        /* open the output file */
        oflags = O_RDWR | O_CREAT | O_TRUNC;
#ifdef O_BINARY
        oflags |= O_BINARY;
#endif
        outf = open(argv[arg_base + 5 + arg_off], oflags, S_IRUSR | S_IWUSR);
        if (-1 == outf) {
                fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                goto cleanup_and_exit;
        }

        printf("Creating image '%s'...\n", argv[arg_base + 5]);
        if (options & BOOTLOADER) {
                off_t bloader_size;
                uint8_t csum;

                /*
                 * build AN-B-001 header
                 * we write it here, but it may be rewritten later on
                 */
                if (fstat(bloader, &sbuf)) {
                        fprintf(stderr, "%s\r\n", argv[3]);
                        goto cleanup_and_exit;
                }
                bloader_size = sbuf.st_size;
                if (options & SPI) {
                        spi_hdr.preamble[0] = 0x70;
                        spi_hdr.preamble[1] = 0x50;
                        memset(spi_hdr.empty, 0, sizeof spi_hdr.empty);
                        spi_hdr.len[0] = (uint8_t)((bloader_size & 0xff00) >> 8);
                        spi_hdr.len[1] = (uint8_t)((bloader_size & 0xff));
                        if (safe_write(outf, &spi_hdr, sizeof spi_hdr)) {
                                fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                                goto cleanup_and_exit;
                        }
                        printf("[%08x] AN-B-001 SPI header\n", 0);
                }
                else if (options & EEPROM) {
                        i2c_hdr.preamble[0] = 0x70;
                        i2c_hdr.preamble[1] = 0x50;
                        i2c_hdr.len[0] = (uint8_t)((bloader_size & 0xff00) >> 8);
                        i2c_hdr.len[1] = (uint8_t)((bloader_size & 0xff));
                        memset(i2c_hdr.dummy, 0, sizeof i2c_hdr.dummy);
                        if (safe_write(outf, &i2c_hdr, sizeof i2c_hdr)) {
                                fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                                goto cleanup_and_exit;
                        }
                        printf("[%08x] AN-B-001 I2C header\n", 0);
                }
                offset = lseek(outf, 0, SEEK_CUR);
                if (-1 == offset) {
                        fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                        goto cleanup_and_exit;
                }
                if (append_file_csum(outf, bloader, &csum))
                        goto cleanup_and_exit;
                printf("[%08x] Bootloader\n", (unsigned)offset);
                if (options & EEPROM)
                        i2c_hdr.crc = csum;  /* we'll re-write the header */
        }

        /* Place the product header at the beginning if needed */
        if (off3 < off1) {
                offset = lseek(outf, 0, SEEK_CUR);
                if (-1 == offset) {
                        fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                        goto cleanup_and_exit;
                }
                if ((unsigned)offset > off3) {
                        fprintf(stderr, "'off3'=%s is too low.\n", argv[arg_base + 4]);
                        goto cleanup_and_exit;
                }
                if (off3 > (unsigned)offset) {
                        if (add_padding(outf, off3 - offset, pad_byte)) {
                                fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                                goto cleanup_and_exit;
                        }
                        printf("[%08x] Padding (%02X's)\n", (unsigned)offset, pad_byte);
                }
                memset(&p_hdr, 0, sizeof p_hdr);
                /* no version for now */
                p_hdr.signature[0] = 0x70;
                p_hdr.signature[1] = 0x52;
                store32(p_hdr.offset1, off1);
                store32(p_hdr.offset2, off2);
                memset(p_hdr.bd_address, 0xff, sizeof(p_hdr.bd_address));
                memset(p_hdr.pad, 0xff, sizeof(p_hdr.bd_address));
                store32(p_hdr.cfg_offset, cfg_off);
                if (safe_write(outf, &p_hdr, sizeof p_hdr)) {
                        fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                        goto cleanup_and_exit;
                }
                printf("[%08x] Product header\n", off3);
        }

        /* now place img1 at offset off1 */
        offset = lseek(outf, 0, SEEK_CUR);
        if (-1 == offset) {
                fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                goto cleanup_and_exit;
        }
        if ((unsigned)offset > off1) {
                fprintf(stderr, "'off1'=%s is too low.\n", argv[arg_base + 1]);
                goto cleanup_and_exit;
        }
        if (off1 > (unsigned)offset) {
                if (add_padding(outf, off1 - offset, pad_byte)) {
                        fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                        goto cleanup_and_exit;
                }
                printf("[%08x] Padding (%02X's)\n", (unsigned)offset, pad_byte);
        }

        if (set_active_image(img1, 0x01) < 0){
                goto cleanup_and_exit;
        }



        if (append_file_csum(outf, img1, NULL))
                goto cleanup_and_exit;
        printf("[%08x] '%s'\n", off1, argv[arg_base]);

        /* then goes img2 at offset off2 */
        offset = lseek(outf, 0, SEEK_CUR);
        if (-1 == offset) {
                fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                goto cleanup_and_exit;
        }
        if ((unsigned)offset > off2) {
                fprintf(stderr, "'off2'=%s is too low.\n", argv[arg_base + 3]);
                goto cleanup_and_exit;
        }
        if (off2 > (unsigned)offset) {
                if (add_padding(outf, off2 - offset, pad_byte)) {
                        fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                        goto cleanup_and_exit;
                }
                printf("[%08x] Padding (%02X's)\n", (unsigned)offset, pad_byte);
        }

        if (set_active_image(img2, 0x00) < 0){
                goto cleanup_and_exit;
        }

        if (append_file_csum(outf, img2, NULL))
                goto cleanup_and_exit;
        printf("[%08x] '%s'\n", off2, argv[arg_base + 2]);

        /* finally, the product header goes at off3 */
        if (off3>off2) {
                offset = lseek(outf, 0, SEEK_CUR);
                if (-1 == offset) {
                        fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                        goto cleanup_and_exit;
                }
                if ((unsigned)offset > off3) {
                        fprintf(stderr, "'off3'=%s is too low.\n", argv[arg_base + 4]);
                        goto cleanup_and_exit;
                }
                if (off3 > (unsigned)offset) {
                        if (add_padding(outf, off3 - offset, pad_byte)) {
                                fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                                goto cleanup_and_exit;
                        }
                        printf("[%08x] Padding (%02X's)\n", (unsigned)offset, pad_byte);
                }
                memset(&p_hdr, 0, sizeof p_hdr);
                /* no version for now */
                p_hdr.signature[0] = 0x70;
                p_hdr.signature[1] = 0x52;
                store32(p_hdr.offset1, off1);
                store32(p_hdr.offset2, off2);
                memset(p_hdr.bd_address, 0xff, sizeof(p_hdr.bd_address));
                memset(p_hdr.pad, 0xff, sizeof(p_hdr.bd_address));
                store32(p_hdr.cfg_offset, cfg_off);
                if (safe_write(outf, &p_hdr, sizeof p_hdr)) {
                        fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                        goto cleanup_and_exit;
                }
                printf("[%08x] Product header\n", off3);
        }

        if ((options & BOOTLOADER) && (options & EEPROM))  {
                /* write the header again, to set the checksum */
                if (lseek(outf, 0, SEEK_SET) == -1) {
                        fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                        goto cleanup_and_exit;
                }
                if (safe_write(outf, &i2c_hdr, sizeof i2c_hdr)) {
                        fprintf(stderr, "%s\r\n", argv[arg_base + 5]);
                        goto cleanup_and_exit;
                }
        }

        res = EXIT_SUCCESS;

cleanup_and_exit:
        if (img2 != -1) {
                if (close(img2))
                        fprintf(stderr, "%s\r\n", argv[arg_base + 2]);
        }

        if (img1 != -1) {
                if (close(img1))
                        fprintf(stderr, "%s\r\n", argv[arg_base]);
        }

        if (bloader != -1) {
                if (close(bloader))
                        fprintf(stderr, "%s\r\n", argv[3]);
        }

        return res;
}

static void print_hex_string(const uint8_t *data, size_t data_len, bool new_line)
{
        int i;

        for (i = 0; i < data_len; i++) {
                printf("%02X", data[i]);
        }

        if (new_line) {
                printf("\r\n");
        }
}

static int generate_sym_key(int argc, const char *argv[])
{
        int i;
        int num = 1;
        int key_len = 32;
        uint8_t *key;

        if (argc > 2) {
                num = atoi(argv[2]);
        }

        if (argc > 3) {
                key_len = atoi(argv[3]);
        }

        if (num < 1) {
                fprintf(stderr, "invalid number of keys\r\n");
                usage(argv[0]);
                return EXIT_FAILURE;
        }

        if (key_len < 1) {
                fprintf(stderr, "invalid key length\r\n");
                usage(argv[0]);
                return EXIT_FAILURE;
        }

        key = malloc(key_len);

        if (!key) {
                fprintf(stderr, "allocation error\r\n");
                return EXIT_FAILURE;
        }

        printf("Generating %d keys (%d-bits)...\n", num, key_len * 8);

        for (i = 0; i < num; i++) {
                mkimage_status_t status = mkimage_generate_symmetric_key(key_len, key);

                if (status != MKIMAGE_STATUS_OK) {
                        free(key);
                        fprintf(stderr, "error during key generation: %s\r\n",
                                                                mkimage_status_message(status));
                        return EXIT_FAILURE;
                }

                printf("    #%d: ", i + 1);
                print_hex_string(key, key_len, true);
        }

        free(key);

        return EXIT_SUCCESS;
}

static int generate_asym_key(int argc, const char* argv[])
{
        int i;
        int num = 1;
        uint8_t pub_key[1024] = { 0 };
        uint8_t priv_key[1024] = { 0 };
        size_t pub_key_len = sizeof(pub_key);
        size_t priv_key_len = sizeof(priv_key);
        mkimage_elliptic_curve_t ec;
        int status = EXIT_FAILURE;

        if (argc < 3) {
                fprintf(stderr, "elliptic curve must be passed\r\n");
                usage(argv[0]);
                return EXIT_FAILURE;
        }

        ec = mkimage_string_to_elliptic_curve(argv[2]);

        if (ec == MKIMAGE_ELLIPTIC_CURVE_INVALID) {
                fprintf(stderr, "invalid elliptic curve\r\n");
                usage(argv[0]);
                return EXIT_FAILURE;
        }

        if (argc > 3) {
                num = atoi(argv[3]);
        }

        if (num < 1) {
                fprintf(stderr, "invalid number of keys\r\n");
                usage(argv[0]);
                return EXIT_FAILURE;
        }

        printf("Generating %d keys on %s elliptic curve...\n", num, argv[2]);

        for (i = 0; i < num; i++) {
                mkimage_status_t status = mkimage_generate_asymmetric_key(ec, &priv_key_len,
                                                                priv_key, &pub_key_len, pub_key);

                if (status != MKIMAGE_STATUS_OK) {
                        fprintf(stderr, "error during key generation: %s\r\n",
                                                                mkimage_status_message(status));
                        goto done;
                }

                printf("    #%d (private key length: %zu, public key length: %zu):\n", i + 1,
                                                                        priv_key_len, pub_key_len);
                printf("        PRIVATE KEY: ");
                print_hex_string(priv_key, priv_key_len, true);
                printf("        PUBLIC KEY:  ");
                print_hex_string(pub_key, pub_key_len, true);

                pub_key_len = sizeof(pub_key);
                priv_key_len = sizeof(priv_key);
        }

        status = EXIT_SUCCESS;
done:

        return status;
}

static int create_single_secure_image(int argc, const char *argv[])
{
        int argix = 9; // app_name, option, in_file, version_file, out_file, ec, hash, key, key_id
        mkimage_elliptic_curve_t elliptic_curve;
        mkimage_hash_method_t hash_method;
        mkimage_secure_image_opt_data_t opt_data = { 0 };
        mkimage_status_t lib_status;
        uint8_t priv_key[1024];
        unsigned int priv_key_length;
        unsigned int key_id;
        char *end_ptr;
        int status = EXIT_FAILURE;
        int out_fd = -1;
        uint8_t *in_buf = NULL, *ver_buf = NULL, *out_buf = NULL;
        size_t in_size, ver_size, out_size;

        if (argc < argix) {
                usage(argv[0]);
                return EXIT_FAILURE;
        }

        elliptic_curve = mkimage_string_to_elliptic_curve(argv[5]);

        if (elliptic_curve == MKIMAGE_ELLIPTIC_CURVE_INVALID) {
                fprintf(stderr, "invalid elliptic curve\r\n");
                return EXIT_FAILURE;
        }

        hash_method = mkimage_string_to_hash_method(argv[6]);

        if (hash_method == MKIMAGE_HASH_METHOD_INVALID) {
                fprintf(stderr, "invalid hash method\r\n");
                return EXIT_FAILURE;
        }

        /* Parse private key */
        priv_key_length = strlen(argv[7]);

        if (priv_key_length % 2 || priv_key_length == 0) {
                fprintf(stderr, "invalid private key hex-string length\r\n");
                return EXIT_FAILURE;
        }

        /* String length to buffer length */
        priv_key_length /= 2;

        if (parse_hex_string(argv[7], priv_key, priv_key_length)) {
                fprintf(stderr, "invalid private key hex-string\r\n");
                goto done;
        }

        /*
         * This could be index (decimal value) or address (hexadecimal value) - use numerical base
         * determined by format.
         */
        key_id = strtoll(argv[8], &end_ptr, 0);

        if (*end_ptr != '\0' || end_ptr == argv[8]) {
                fprintf(stderr, "invalid public key ID\r\n");
                goto done;
        }

        /* Parse revocation command if it is passed */
        if (argc > argix && !strcmp(argv[argix], "rev")) {
                /* There is 4 public and 8 symmetric keys */
                mkimage_key_id_t keys_id[12] = { };
                char *arg_dup;
                char *token;
                int i;

                argix += 2;

                if (argc < argix) {
                        fprintf(stderr, "revocation command must be passed\r\n");
                        goto done;
                }

                opt_data.rev_key_id = keys_id;
                arg_dup = strdup(argv[argix - 1]);
                token = strtok(arg_dup, " ");

                for (i = 0; token && i < sizeof(keys_id) / sizeof(keys_id[0]); i++) {
                        if (token[0] == 's') {
                                opt_data.rev_key_id[i].type = MKIMAGE_KEY_TYPE_SYMMETRIC;
                                ++token;
                        } else {
                                opt_data.rev_key_id[i].type = MKIMAGE_KEY_TYPE_PUBLIC;
                        }

                        opt_data.rev_key_id[i].id = (uint32_t) strtol(token, NULL, 0);
                        token = strtok(NULL, " ");
                }

                opt_data.rev_key_number = i;
                free(arg_dup);
        }

        /* Parse minimal FW version if it is passed */
        if (argc > argix && !strcmp(argv[argix], "min_ver")) {
                ++argix;

                opt_data.change_min_fw_version = true;

                /* Version has been passed */
                if (argc > argix) {
                        opt_data.min_fw_version = argv[argix];
                }
        }

        /* Read input file */
        if (!read_whole_file(argv[2], O_RDONLY | O_BINARY, &in_size, &in_buf) || in_size == 0 ||
                                                                                        !in_buf) {
                fprintf(stderr, "cannot read file - %s\r\n", argv[2]);
                goto done;
        }

        /* Read version file */
        if (!read_whole_file(argv[3], O_RDONLY | O_BINARY, &ver_size, &ver_buf) || ver_size == 0 ||
                                                                                        !ver_buf) {
                fprintf(stderr, "cannot read file - %s\r\n", argv[3]);
                goto done;
        }

        lib_status = mkimage_create_single_secure_image(in_size, in_buf, ver_size, ver_buf,
                                                        elliptic_curve, hash_method, priv_key_length,
                                                        priv_key, key_id, &opt_data, &out_buf,
                                                                                        &out_size);

        if (lib_status != MKIMAGE_STATUS_OK) {
                fprintf(stderr, "cannot create secure single image - %s\r\n",
                                                                mkimage_status_message(lib_status));
                goto done;
        }

        /* Open output file */
        out_fd = open(argv[4], O_RDWR | O_CREAT | O_TRUNC | O_BINARY, S_IRUSR | S_IWUSR);
        if (out_fd < 0) {
                fprintf(stderr, "cannot open file - %s\r\n", argv[4]);
                goto done;
        }

        if (safe_write(out_fd, out_buf, out_size)) {
                fprintf(stderr, "cannot write to file - %s\r\n", argv[4]);
                goto done;
        }

        status = EXIT_SUCCESS;

done:
        /* Close output file */
        if (out_fd >= 0) {
                close(out_fd);
        }

        /* Free buffers */
        free(in_buf);
        free(ver_buf);
        free(out_buf);

        return status;
}

int main(int argc, const char* argv[])
{
        int res = EXIT_FAILURE;

        if (argc < 2 ) {
                usage(argv[0]);
                exit(EXIT_FAILURE);
        }

        if (!strcmp(argv[1], "single"))
                res = create_single_image(argc, argv);
        else if (!strcmp(argv[1], "multi"))
                res = create_multi_image(argc, argv);
        else if (!strcmp(argv[1], "gen_sym_key"))
                res = generate_sym_key(argc, argv);
        else if (!strcmp(argv[1], "gen_asym_key"))
                res = generate_asym_key(argc, argv);
        else if (!strcmp(argv[1], "secure"))
                res = create_single_secure_image(argc, argv);
        else
                usage(argv[0]);

        exit(res);
}

