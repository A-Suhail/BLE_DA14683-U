/**
 ****************************************************************************************
 *
 * @file mkimage.c
 *
 * @brief Library for creating a firmware image.
 *
 * Copyright (C) 2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include "suota.h"
#include "suota_security_ext.h"
#include "bo_crypto.h"
#include "mkimage.h"

/* Number of asymmetric key/signature generation tries */
#define GEN_RETRY_NUM   10
/* Block size for AES encryption  */
#define AES_BLOCKSIZE   16

/* Start address of the OTP memory */
#define OTP_START_ADDRESS       0x07F80000

static crypto_buffer_t *aes_key;
static uint8_t aes_iv[16];

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

static elliptic_curve_t map_elliptic_curve(mkimage_elliptic_curve_t elliptic_curve)
{
        switch(elliptic_curve) {
                case MKIMAGE_ELLIPTIC_CURVE_SECP192R1:
                        return ELLIPTIC_CURVE_SECP192R1;
                case MKIMAGE_ELLIPTIC_CURVE_SECP224R1:
                        return ELLIPTIC_CURVE_SECP224R1;
                case MKIMAGE_ELLIPTIC_CURVE_SECP256R1:
                        return ELLIPTIC_CURVE_SECP256R1;
                case MKIMAGE_ELLIPTIC_CURVE_SECP384R1:
                        return ELLIPTIC_CURVE_SECP384R1;
                case MKIMAGE_ELLIPTIC_CURVE_BP256R1:
                        return ELLIPTIC_CURVE_BP256R1;
                case MKIMAGE_ELLIPTIC_CURVE_BP384R1:
                        return ELLIPTIC_CURVE_BP384R1;
                case MKIMAGE_ELLIPTIC_CURVE_BP512R1:
                        return ELLIPTIC_CURVE_BP512R1;
                case MKIMAGE_ELLIPTIC_CURVE_CURVE25519:
                        return ELLIPTIC_CURVE_CURVE25519;
                case MKIMAGE_ELLIPTIC_CURVE_SECP192K1:
                        return ELLIPTIC_CURVE_SECP192K1;
                case MKIMAGE_ELLIPTIC_CURVE_SECP224K1:
                        return ELLIPTIC_CURVE_SECP224K1;
                case MKIMAGE_ELLIPTIC_CURVE_SECP256K1:
                        return ELLIPTIC_CURVE_SECP256K1;
                case MKIMAGE_ELLIPTIC_CURVE_EDWARDS25519:
                        return ELLIPTIC_CURVE_EDWARDS25519;
                default:
                        break;
        }

        return ELLIPTIC_CURVE_NONE;
}

static hash_method_t map_hash_method(mkimage_hash_method_t hash_method)
{
        switch(hash_method) {
                case MKIMAGE_HASH_METHOD_SHA224:
                        return HASH_METHOD_SHA224;
                case MKIMAGE_HASH_METHOD_SHA256:
                        return HASH_METHOD_SHA256;
                case MKIMAGE_HASH_METHOD_SHA384:
                        return HASH_METHOD_SHA384;
                case MKIMAGE_HASH_METHOD_SHA512:
                        return HASH_METHOD_SHA512;
                default:
                        break;
        }

        return HASH_METHOD_NONE;
}

/* Returns 0 when elliptic curve is not supported in ECDSA */
static security_hdr_ecc_curve_t elliptic_curve_to_hdr_ecc_curve(mkimage_elliptic_curve_t ec)
{
        switch (ec) {
        case MKIMAGE_ELLIPTIC_CURVE_SECP192R1:
                return SECURITY_HDR_ECC_CURVE_SECP192R1;
        case MKIMAGE_ELLIPTIC_CURVE_SECP224R1:
                return SECURITY_HDR_ECC_CURVE_SECP224R1;
        case MKIMAGE_ELLIPTIC_CURVE_SECP256R1:
                return SECURITY_HDR_ECC_CURVE_SECP256R1;
        case MKIMAGE_ELLIPTIC_CURVE_EDWARDS25519:
                return SECURITY_HDR_ECC_CURVE_EDWARDS25519;
        default:
                return 0;
        }
}

/* Returns 0 when hash method is not supported in ECDSA */
static security_hdr_hash_t hash_method_to_hdr_hash(mkimage_hash_method_t h)
{
        switch (h) {
        case MKIMAGE_HASH_METHOD_SHA224:
                return SECURITY_HDR_HASH_SHA_224;
        case MKIMAGE_HASH_METHOD_SHA256:
                return SECURITY_HDR_HASH_SHA_256;
        case MKIMAGE_HASH_METHOD_SHA384:
                return SECURITY_HDR_HASH_SHA_384;
        case MKIMAGE_HASH_METHOD_SHA512:
                return SECURITY_HDR_HASH_SHA_512;
        default:
                return 0;
        }
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

static inline void store16(uint8_t* buf, uint16_t val)
{
#ifdef MKIMAGE_LITTLE_ENDIAN
        buf[0] = val & 0xff;
        val >>= 8;
        buf[1] = val & 0xff;
        val >>= 8;
#else
        buf[1] = val & 0xff;
        val >>= 8;
        buf[0] = val & 0xff;
#endif
}

/*
 * Look for a C string (i.e. string enclosed in "") inside text. \" is not handled as escaped
 * double quote. Returns a strdup'ed string - the caller should free it.
 */
static char *find_cstring(const char *text)
{
        char *from, *to, *s;
        size_t length;

        from = strchr(text, '"');
        if (!from) {
                return NULL;
        }

        to = strchr(++from, '"');
        if (!to) {
                return NULL;
        }

        length = to - from;

        /* 'strndup' substitute */
        s = malloc(length + 1);
        strncpy(s, from, length);
        s[length] = '\0';
        return s;
}

static bool get_version(size_t size, const char *buffer, suota_1_1_image_header_t *hdr)
{
        const char *from;
        char *version;
        char *version_start;

        from = strstr(buffer, "BLACKORCA_SW_VERSION ");

        if (!from || (from > buffer + size)) {
                return false;
        }

        version = find_cstring(from);
        if (!version) {
                return false;
        }

        version_start = version;

        /* Skip any leading v_ */
        if ('v' == version[0]  &&  '_' == version[1]) {
                version_start = version + 2;
        }

        if (strlen(version_start) >= sizeof(hdr->version)) {
                /* Force '\0' sign at the end of the string */
                strncpy((char *) hdr->version, version_start, sizeof(hdr->version) - 1);
                hdr->version[sizeof(hdr->version) - 1] = '\0';
        } else {
                /* Copy whole string (with '\0' sign). Unused bytes should keep 0xFF value */
                strcpy((char *) hdr->version, version_start);
        }

        free(version);

        return true;
}

static bool get_date(size_t size, const char *buffer, suota_1_1_image_header_t *hdr)
{
        const char *from;
        char *timestamp;
        struct tm tm;
        time_t secs;

        from = strstr(buffer, "BLACKORCA_SW_VERSION_DATE ");

        if (!from || (from > buffer + size)) {
                return false;
        }

        timestamp = find_cstring(from);
        if (!timestamp) {
                return false;
        }

        memset(&tm, 0, sizeof tm);
        tm.tm_isdst = -1;

        if (sscanf(timestamp, "%d-%d-%d %d:%d", &tm.tm_year, &tm.tm_mon, &tm.tm_mday, &tm.tm_hour,
                                                                                &tm.tm_min) != 5) {
                return false;
        }
        tm.tm_year -= 1900;
        tm.tm_mon--;

        secs = mktime(&tm);
        if (-1 == secs) {
                return false;
        }

        store32((uint8_t *) &hdr->timestamp, (uint32_t) secs);
        free(timestamp);

        return true;
}

static uint32_t compute_crc32(size_t data_length, const uint8_t *data)
{
        uint32_t crc32 = ~0;

        while (data_length--) {
                crc32 = crc32_tab[(crc32 ^ *data++) & 0xff] ^ (crc32 >> 8);
        }

        return crc32 ^ ~0;
}

static bool check_key_id(int key_id)
{
        if (key_id < 0 || (key_id < OTP_START_ADDRESS && key_id > 3)) {
                return false;
        }

        return true;
}

/* Return pointer points to the byte after the last written byte */
static uint8_t *put_tlv(uint8_t *buffer, uint16_t type, uint16_t length, const uint8_t *value)
{
        uint8_t *ptr = buffer;

        store16(ptr, type);
        ptr += 2;
        store16(ptr, length);
        ptr += 2;

        if (length > 0) {
                memcpy(ptr, value, length);
                ptr += length;
        }

        return ptr;
}

static mkimage_status_t create_signature(size_t in_size, const uint8_t *in,
                                                        mkimage_elliptic_curve_t elliptic_curve,
                                                        mkimage_hash_method_t hash_method,
                                                        size_t priv_key_len, const uint8_t *priv_key,
                                                        size_t *signature_len, uint8_t *signature)
{
        elliptic_curve_t ec;
        hash_method_t hm;
        mkimage_status_t status = MKIMAGE_STATUS_OK;
        crypto_buffer_t crypto_in, crypto_priv_key, crypto_signature;

        /* Create crypto-library buffers, constant buffers (input and private key) won't be modified */
        crypto_buffer_init(&crypto_in, in_size, (uint8_t *) in);
        crypto_buffer_init(&crypto_priv_key, priv_key_len, (uint8_t *) priv_key);
        crypto_buffer_init(&crypto_signature, *signature_len, signature);

        /* Convert elliptic curve and hash method to crypto-library types */
        ec = map_elliptic_curve(elliptic_curve);
        hm = map_hash_method(hash_method);

        if (ec == ELLIPTIC_CURVE_NONE || hm == HASH_METHOD_NONE ||
                (ec == ELLIPTIC_CURVE_EDWARDS25519 && hm != HASH_METHOD_SHA512)) {
                status = MKIMAGE_STATUS_INVALID_PARAMETER;
                goto done;
        }

        if (ec == ELLIPTIC_CURVE_EDWARDS25519) {
                if (!crypto_eddsa_sig_gen(ec, &crypto_priv_key, &crypto_in, &crypto_signature)) {
                        status = MKIMAGE_STATUS_CRYPTO_LIBRARY_ERROR;
                        goto done;
                }
        } else if (!crypto_ecdsa_sig_gen(ec, hm, &crypto_priv_key, &crypto_in, &crypto_signature)) {
                status = MKIMAGE_STATUS_CRYPTO_LIBRARY_ERROR;
                goto done;
        }

        /* Copy signature and its length */
        *signature_len = crypto_signature.size;

done:

        return status;
}

static bool version_str_to_version_number(const char *str, security_hdr_fw_version_t *version)
{
        char *end;

        version->major = (uint16_t) strtol(str, &end, 10);

        if (*end != '.') {
                return false;
        }

        /* Any character could occur after minor version number - skip them */
        version->minor = (uint16_t) strtol(end + 1, &end, 10);

        return true;
}
/*
 * Parse version file content - with version string e.g. "1.0***" to two uint16 values. Version
 * string must have at least 2 numbers separated with dots. These numbers must be in range 0 -  to
 * 65535 (uint16 range). Characters following the last number will be skipped. Function returns
 * false when version string cannot be parsed.
 */
static bool get_version_number(size_t size, const char *buffer, security_hdr_fw_version_t *version)
{
        suota_1_1_image_header_t tmp_hdr;

        if (!buffer || size < 1) {
                return false;
        }

        if (!get_version(size, buffer, &tmp_hdr)) {
                return false;
        }

        return version_str_to_version_number((char *) tmp_hdr.version, version);
}

/*
 * Note: if encryption is enabled then out_size must cover encrypted image size (aligned to the AES
 * block size).
 */
static int create_image(unsigned int version, size_t in_size, const uint8_t *in, size_t ver_size,
                                const uint8_t *ver, bool encrypt, size_t data_length, void *data,
                                                                size_t out_size, uint8_t *out)
{
        suota_1_1_image_header_t header;
        size_t header_size = sizeof(header);
        uint8_t *ptr = out;
        const uint8_t *end = out + out_size;
        uint32_t crc;

        memset(&header, 0xff, header_size);
        header.flags = ~0x0000;
        header.signature[0] = SUOTA_1_1_IMAGE_HEADER_SIGNATURE_B1;
        header.signature[1] = SUOTA_1_1_IMAGE_HEADER_SIGNATURE_B2;
        /* For single images 'data_length' should be 0 */
        store32((uint8_t *) &header.exec_location, header_size + data_length);

        if (encrypt) {
                /* 'out_size' should be aligned to the AES block size */
                header.flags |= SUOTA_1_1_IMAGE_FLAG_FORCE_CRC;
        }

        store32((uint8_t *) &header.code_size, in_size);

        if (!get_version(ver_size, (char *) ver, &header)) {
                return MKIMAGE_STATUS_INVALID_DATA;
        }

        if (!get_date(ver_size, (char *) ver, &header)) {
                return MKIMAGE_STATUS_INVALID_DATA;
        }

        crc = compute_crc32(in_size, in);
        store32((uint8_t *) &header.crc, crc);

        if (ptr + header_size > end) {
                return MKIMAGE_STATUS_BUFFER_TOO_SMALL;
        }

        memcpy(ptr, &header, header_size);
        ptr += header_size;

        /* Write security extension */
        if (version == SUOTA_VERSION_1_4 && data) {
                uint8_t *security_ext;

                if (ptr + data_length > end) {
                        return MKIMAGE_STATUS_BUFFER_TOO_SMALL;
                }

                security_ext = (uint8_t *) data;
                memcpy(ptr, security_ext, data_length);
                ptr += data_length;
        }

        if (encrypt) {
                size_t enc_size = in_size;
                crypto_buffer_t *aes_in;

                /* Align binary size (in created image) to the AES block size */
                if (enc_size % AES_BLOCKSIZE) {
                        enc_size += AES_BLOCKSIZE - (enc_size % AES_BLOCKSIZE);
                }

                if (ptr + enc_size > end) {
                        return MKIMAGE_STATUS_BUFFER_TOO_SMALL;
                }

                /*
                 * Input length could be shorter than encrypted size due to the AES block size
                 * alignment - the last bytes should be zeroed.
                 */
                aes_in = crypto_buffer_alloc(enc_size, NULL);

                if (!aes_in) {
                        return MKIMAGE_STATUS_ALLOCATION_ERROR;
                }

                memcpy(aes_in->value, in, in_size);

                if (!crypto_aes_cbc_encrypt(aes_key, aes_iv, aes_in, ptr)) {
                        crypto_buffer_free(aes_in);
                        return MKIMAGE_STATUS_CRYPTO_LIBRARY_ERROR;
                }

                ptr += enc_size;
                crypto_buffer_free(aes_in);
        } else {
                if (ptr + in_size > end) {
                        return MKIMAGE_STATUS_BUFFER_TOO_SMALL;
                }

                memcpy(ptr, in, in_size);
        }

        return MKIMAGE_STATUS_OK;
}

/*
 * Function writes device administration section content to the buffer. It returns number of the
 * written bytes if no error occurs, 0 otherwise.
 */
static size_t fill_device_administration_section(uint8_t *buffer,
                                                        const security_hdr_fw_version_t *image_version,
                                                        mkimage_secure_image_opt_data_t *data)
{
        uint16_t version_le[2];
        uint8_t payload[1024] = { 0 };
        uint8_t *payload_ptr = payload;

        if (!data) {
                /* This section is empty - write only the type and the size */
                goto write_section;
        }

        /* Store key revocation record if given */
        if (data->rev_key_id && data->rev_key_number > 0) {
                int i;
                uint8_t key_rev_record[256] = { 0 };
                uint8_t *tmp_ptr = key_rev_record;

                for (i = 0; i < data->rev_key_number; i++) {
                        if (data->rev_key_id[i].type == MKIMAGE_KEY_TYPE_PUBLIC) {
                                *tmp_ptr = SECURITY_HDR_KEY_TYPE_PUBLIC;
                        } else if (data->rev_key_id[i].type == MKIMAGE_KEY_TYPE_SYMMETRIC) {
                                *tmp_ptr = SECURITY_HDR_KEY_TYPE_SYMMETRIC;
                        } else {
                                /* Unrecognized key ID */
                                continue;
                        }

                        ++tmp_ptr;
                        store32(tmp_ptr, data->rev_key_id[i].id);
                        tmp_ptr += sizeof(uint32_t);
                }

                if (tmp_ptr > key_rev_record) {
                        payload_ptr = put_tlv(payload_ptr, SECURITY_HDR_TYPE_KEY_REVOCATION_RECORD,
                                                        tmp_ptr - key_rev_record, key_rev_record);
                }
        }

        /* Store firmware version number in little-endian */
        store16((uint8_t *) &version_le[0], image_version->major);
        store16((uint8_t *) &version_le[1], image_version->minor);
        payload_ptr = put_tlv(payload_ptr, SECURITY_HDR_TYPE_FW_VERSION_NUMBER, sizeof(version_le),
                                                                        (uint8_t *) version_le);

        /* Store the new minimal firmware version*/
        if (data->change_min_fw_version) {
                security_hdr_fw_version_t min_version;

                min_version = *image_version;

                if (data->min_fw_version && !version_str_to_version_number(data->min_fw_version,
                                                                                &min_version)) {
                        /* Cannot parse version string */
                        return 0;
                }

                /* Store minimum version in little-endian */
                store16((uint8_t *) &version_le[0], min_version.major);
                store16((uint8_t *) &version_le[1], min_version.minor);
                payload_ptr = put_tlv(payload_ptr, SECURITY_HDR_TYPE_ROLLBACK_PREVENTION_SEGMENT,
                                                        sizeof(version_le), (uint8_t *) version_le);
        }

write_section:
        return put_tlv(buffer, SECURITY_HDR_TYPE_DEVICE_ADMIN_SECTION, payload_ptr - payload,
                                                                                payload) - buffer;
}

/* Function writes security section content to the buffer. It returns number of written bytes. */
static size_t fill_security_section(uint8_t *buffer, const suota_security_header_t *hdr,
                                                const uint8_t *signature, uint32_t signature_len)
{
        uint8_t payload[1024] = { 0 };
        uint8_t *payload_ptr = payload;

        memcpy(payload_ptr, hdr, sizeof(*hdr));
        payload_ptr += sizeof(*hdr);
        payload_ptr = put_tlv(payload_ptr, SECURITY_HDR_TYPE_SIGNATURE_SECTION, signature_len,
                                                                                        signature);

        return put_tlv(buffer, SECURITY_HDR_TYPE_SECURITY_SECTION, payload_ptr - payload, payload) -
                                                                                        buffer;
}

/*
 * Function calculates how many bytes of pattern (0xFF) is needed after image header - it should
 * be aligned to 1024 bytes
 */
static size_t calculate_pattern_size(size_t dev_adm_section_size, size_t security_section_size)
{
        size_t padding_size = 0;
        size_t header_size;

        header_size = sizeof(suota_1_1_image_header_t) + security_section_size +
                                                                        dev_adm_section_size;

        /* Calculate pattern size - 1024 bytes alignment is needed for image header */
        if (header_size % 1024) {
                padding_size = 1024 - header_size % 1024;
        }

        return padding_size;
}

const char *mkimage_status_message(mkimage_status_t status)
{
        switch (status) {
        case MKIMAGE_STATUS_OK:
                return "ok";
        case MKIMAGE_STATUS_INVALID_LENGTH:
                return "invalid length";
        case MKIMAGE_STATUS_INVALID_PARAMETER:
                return "invalid parameter";
        case MKIMAGE_STATUS_INVALID_DATA:
                return "invalid data";
        case MKIMAGE_STATUS_ALLOCATION_ERROR:
                return "allocation error";
        case MKIMAGE_STATUS_BUFFER_TOO_SMALL:
                return "buffer too small";
        case MKIMAGE_STATUS_CRYPTO_LIBRARY_ERROR:
                return "crypto library error";
        default:
                return "unknown";
        }

        return "unknown";
}

mkimage_elliptic_curve_t mkimage_string_to_elliptic_curve(const char *name)
{
        if (!strcmp(name, "SECP192R1")) {
                return MKIMAGE_ELLIPTIC_CURVE_SECP192R1;
        } else if (!strcmp(name, "SECP224R1")) {
                return MKIMAGE_ELLIPTIC_CURVE_SECP224R1;
        } else if (!strcmp(name, "SECP256R1")) {
                return MKIMAGE_ELLIPTIC_CURVE_SECP256R1;
        } else if (!strcmp(name, "SECP384R1")) {
                return MKIMAGE_ELLIPTIC_CURVE_SECP384R1;
        } else if (!strcmp(name, "BP256R1")) {
                return MKIMAGE_ELLIPTIC_CURVE_BP256R1;
        } else if (!strcmp(name, "BP384R1")) {
                return MKIMAGE_ELLIPTIC_CURVE_BP384R1;
        } else if (!strcmp(name, "BP512R1")) {
                return MKIMAGE_ELLIPTIC_CURVE_BP512R1;
        } else if (!strcmp(name, "CURVE25519")) {
                return MKIMAGE_ELLIPTIC_CURVE_CURVE25519;
        } else if (!strcmp(name, "SECP192K1")) {
                return MKIMAGE_ELLIPTIC_CURVE_SECP192K1;
        } else if (!strcmp(name, "SECP224K1")) {
                return MKIMAGE_ELLIPTIC_CURVE_SECP224K1;
        } else if (!strcmp(name, "SECP256K1")) {
                return MKIMAGE_ELLIPTIC_CURVE_SECP256K1;
        } else if (!strcmp(name, "EDWARDS25519")) {
                return MKIMAGE_ELLIPTIC_CURVE_EDWARDS25519;
        }

        return MKIMAGE_ELLIPTIC_CURVE_INVALID;
}

mkimage_hash_method_t mkimage_string_to_hash_method(const char *name)
{
        if (!strcmp(name, "SHA-224")) {
                return MKIMAGE_HASH_METHOD_SHA224;
        } else if (!strcmp(name, "SHA-256")) {
                return MKIMAGE_HASH_METHOD_SHA256;
        } else if (!strcmp(name, "SHA-384")) {
                return MKIMAGE_HASH_METHOD_SHA384;
        } else if (!strcmp(name, "SHA-512")) {
                return MKIMAGE_HASH_METHOD_SHA512;
        }

        return MKIMAGE_HASH_METHOD_INVALID;
}

mkimage_status_t mkimage_create_single_image(size_t in_size, const uint8_t *in, size_t ver_size,
                                                const uint8_t *ver, const uint8_t *key,
                                                const uint8_t *iv, uint8_t **out, size_t *out_size)
{
        mkimage_status_t res;
        bool encryption;
        size_t size = sizeof(suota_1_1_image_header_t) + in_size;

        if (!in || !ver || !out_size || !out) {
                return MKIMAGE_STATUS_INVALID_PARAMETER;
        }

        *out = NULL;

        if (in_size < 1 || ver_size < 1) {
                return MKIMAGE_STATUS_INVALID_LENGTH;
        }

        if (!key && !iv) {
                encryption = false;
        } else if (key && iv) {
                /*
                 * Copy key and initialization vector to the global variables - they will be used in
                 * other functions.
                 */
                aes_key = crypto_buffer_alloc(16, key);
                memcpy(aes_iv, iv, sizeof(aes_iv));
                encryption = true;

                /* Align binary size (in created image) to the AES block size */
                if (in_size % AES_BLOCKSIZE) {
                        size += AES_BLOCKSIZE - (in_size % AES_BLOCKSIZE);
                }
        } else {
                /* Both or none - key and initialization vector must be given */
                return MKIMAGE_STATUS_INVALID_PARAMETER;
        }

        /*
         * Output image = SUOTA 1.1 header + the app binary (aligned to AES block size when
         * encryption enabled).
         */
        *out = malloc(size);

        if (!*out) {
                res = MKIMAGE_STATUS_ALLOCATION_ERROR;
                goto done;
        }

        *out_size = size;
        res = create_image(SUOTA_VERSION_1_1, in_size, in, ver_size, ver, encryption, 0, NULL,
                                                                                        size, *out);
done:
        crypto_buffer_free(aes_key);

        return res;
}

mkimage_status_t mkimage_generate_symmetric_key(size_t key_length, uint8_t *key)
{
        crypto_buffer_t tmp;
        mkimage_status_t status;

        if (!key) {
               return MKIMAGE_STATUS_INVALID_PARAMETER;
        }

        if (key_length < 1) {
               return MKIMAGE_STATUS_INVALID_LENGTH;
        }

        crypto_buffer_init(&tmp, key_length, key);
        status = crypto_symmetric_key_gen(&tmp) ? MKIMAGE_STATUS_OK :
                                                               MKIMAGE_STATUS_CRYPTO_LIBRARY_ERROR;

        return status;
}

mkimage_status_t mkimage_generate_asymmetric_key(mkimage_elliptic_curve_t elliptic_curve,
                                                        size_t *priv_key_length, uint8_t *priv_key,
                                                        size_t *pub_key_length, uint8_t *pub_key)
{
        crypto_buffer_t private;
        crypto_buffer_t public;
        mkimage_status_t status;
        elliptic_curve_t ec;
        bool val_result = false;
        int cnt = 0;

        if (!priv_key_length || !priv_key_length || !pub_key_length || !pub_key) {
                return MKIMAGE_STATUS_INVALID_PARAMETER;
        }

        if (*priv_key_length < 1 || *pub_key_length < 1) {
                return MKIMAGE_STATUS_INVALID_LENGTH;
        }

        ec = map_elliptic_curve(elliptic_curve);

        if (ec == ELLIPTIC_CURVE_NONE) {
                return MKIMAGE_STATUS_INVALID_PARAMETER;
        }

        crypto_buffer_init(&private, *priv_key_length, priv_key);
        crypto_buffer_init(&public, *pub_key_length, pub_key);

        do {
                status = crypto_asymmetric_key_pair_gen(ec, &private, &public) ? MKIMAGE_STATUS_OK :
                                                                MKIMAGE_STATUS_CRYPTO_LIBRARY_ERROR;

                if (status != MKIMAGE_STATUS_OK) {
                        goto done;
                }

                status = crypto_asymmetric_key_pair_valid(ec, &private, &public, &val_result) ?
                                        MKIMAGE_STATUS_OK : MKIMAGE_STATUS_CRYPTO_LIBRARY_ERROR;

                if (status != MKIMAGE_STATUS_OK) {
                        goto done;
                }

                if (val_result) {
                        break;
                }

                /* Restore original sizes */
                private.size = *priv_key_length;
                public.size = *pub_key_length;
        } while (++cnt < GEN_RETRY_NUM);

        if (val_result) {
                *priv_key_length = private.size;
                *pub_key_length = public.size;
        }

done:

        return status;
}

mkimage_status_t mkimage_create_single_secure_image(size_t in_size, const uint8_t *in,
                                                        size_t ver_size, const uint8_t *ver,
                                                        mkimage_elliptic_curve_t elliptic_curve,
                                                        mkimage_hash_method_t hash_method,
                                                        unsigned int priv_key_length,
                                                        const uint8_t *priv_key,
                                                        unsigned int key_id,
                                                        mkimage_secure_image_opt_data_t *opt_data,
                                                                uint8_t **out, size_t *out_size)
{
        suota_security_header_t hdr;
        mkimage_status_t status = MKIMAGE_STATUS_OK;
        uint8_t dev_adm_section[2048] = { 0 };
        uint8_t security_section[2048] = { 0 };
        uint8_t signature[1024];
        uint8_t *data_buffer = NULL;
        size_t signature_len = sizeof(signature);
        unsigned int tlv_length;
        unsigned int dev_adm_section_size;
        unsigned int security_section_size;
        unsigned int pattern_size;
        security_hdr_fw_version_t image_version;

        /* Check pointers */
        if (!in || !ver || !priv_key) {
                return MKIMAGE_STATUS_INVALID_PARAMETER;
        }

        /* Check lengths */
        if (in_size < 1 || ver_size < 1 || priv_key_length < 1) {
                return MKIMAGE_STATUS_INVALID_LENGTH;
        }

        /* Check values */
        if (elliptic_curve == MKIMAGE_ELLIPTIC_CURVE_INVALID ||
                hash_method == MKIMAGE_HASH_METHOD_INVALID ||
                (elliptic_curve == MKIMAGE_ELLIPTIC_CURVE_EDWARDS25519 &&
                                                hash_method != MKIMAGE_HASH_METHOD_SHA512) ||
                !check_key_id(key_id)) {
                return MKIMAGE_STATUS_INVALID_PARAMETER;
        }

        if (!get_version_number(ver_size, (char *) ver, &image_version)) {
                status = MKIMAGE_STATUS_INVALID_DATA;
                goto done;
        }

        hdr.mode = elliptic_curve != MKIMAGE_ELLIPTIC_CURVE_EDWARDS25519 ?
                                                SECURITY_HDR_MODE_ECDSA : SECURITY_HDR_MODE_EDDSA;
        store32((uint8_t *) &hdr.public_key_id, key_id);
        hdr.curve = elliptic_curve_to_hdr_ecc_curve(elliptic_curve);
        hdr.hash = hash_method_to_hdr_hash(hash_method);

        if (hdr.curve == 0 || hdr.hash == 0) {
                status = MKIMAGE_STATUS_INVALID_PARAMETER;
                goto done;
        }

        /*
         * Generate dummy signature using specified curve - signatue's size and dedicated space for
         * it is needed in security section
         */
        status = create_signature(in_size, in, elliptic_curve, hash_method, priv_key_length,
                                                        priv_key, &signature_len, signature);

        if (status != MKIMAGE_STATUS_OK) {
                goto done;
        }

        /* Create security section with dummy signature - it will be overwritten later */
        security_section_size = fill_security_section(security_section, &hdr, signature,
                                                                                signature_len);

        /* Create device administration section */
        dev_adm_section_size = fill_device_administration_section(dev_adm_section, &image_version,
                                                                                        opt_data);

        if (dev_adm_section_size == 0) {
                status = MKIMAGE_STATUS_INVALID_DATA;
                goto done;
        }

        /* Calculate pattern size */
        pattern_size = calculate_pattern_size(dev_adm_section_size, security_section_size);

        /* Glue aligned device administration section and the input (application binary) */
        data_buffer = malloc(dev_adm_section_size + pattern_size + in_size);

        if (!data_buffer) {
                status = MKIMAGE_STATUS_ALLOCATION_ERROR;
                goto done;
        }

        memcpy(data_buffer, dev_adm_section, dev_adm_section_size);
        memset(data_buffer + dev_adm_section_size, 0xFF, pattern_size);
        memcpy(data_buffer + dev_adm_section_size + pattern_size, in, in_size);

        /* Generate signature (it covers aligned device administration section and the input) */
        status = create_signature(dev_adm_section_size + pattern_size + in_size, data_buffer,
                                        elliptic_curve, hash_method, priv_key_length, priv_key,
                                                                        &signature_len, signature);

        /* This buffer is not needed anymore - could be freed here */
        free(data_buffer);
        data_buffer = NULL;

        if (status != MKIMAGE_STATUS_OK) {
                goto done;
        }

        /* Overwrite the signature. It is placed at the and of the security section */
        memcpy(security_section + (security_section_size - signature_len), signature, signature_len);

        /* Glue security section, device administration section and pattern */
        tlv_length = security_section_size + dev_adm_section_size + pattern_size;
        data_buffer = malloc(tlv_length);

        if (!data_buffer) {
                status = MKIMAGE_STATUS_ALLOCATION_ERROR;
                goto done;
        }

        memcpy(data_buffer, security_section, security_section_size);
        memcpy(data_buffer + security_section_size, dev_adm_section, dev_adm_section_size);
        memset(data_buffer + security_section_size + dev_adm_section_size, 0xFF, pattern_size);

        /*
         * Output = SUOTA 1.1 header + security section + device administration section + pattern +
         *          app binary
         */
        *out_size = sizeof(suota_1_1_image_header_t) + tlv_length + in_size;
        *out = malloc(*out_size);

        if (!*out) {
                status = MKIMAGE_STATUS_ALLOCATION_ERROR;
                goto done;
        }

        status = create_image(SUOTA_VERSION_1_4, in_size, in, ver_size, ver, false, tlv_length,
                                                                data_buffer, *out_size, *out);
done:
        free(data_buffer);

        return status;
}

