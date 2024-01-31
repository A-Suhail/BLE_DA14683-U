/**
 ****************************************************************************************
 *
 * @file mkimage.h
 *
 * @brief Library for creating a firmware image - API.
 *
 * Copyright (C) 2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#ifndef MKIMAGE_H_
#define MKIMAGE_H_

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
#extern "C" {
#endif

#ifdef _MSC_VER
#ifdef LIBMKIMAGE_EXPORTS
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT __declspec(dllimport)
#endif
#else
#define DLLEXPORT
#endif

/** Comment to store multi-byte values in big-endian order */
#define MKIMAGE_LITTLE_ENDIAN

/** Statuses which could be returned by library's functions */
typedef enum {
        MKIMAGE_STATUS_OK                       = 0,    /**< There is no error */
        MKIMAGE_STATUS_INVALID_LENGTH,                  /**< Invalid parameter/data length */
        MKIMAGE_STATUS_INVALID_PARAMETER,               /**< Invalid parameter */
        MKIMAGE_STATUS_INVALID_DATA,                    /**< Invalid data */
        MKIMAGE_STATUS_ALLOCATION_ERROR,                /**< Allocation error */
        MKIMAGE_STATUS_BUFFER_TOO_SMALL,                /**< Given buffer is too small */
        MKIMAGE_STATUS_CRYPTO_LIBRARY_ERROR,            /**< Error returned by crypto-library call */
} mkimage_status_t;

/** Elliptic curve */
typedef enum {
        MKIMAGE_ELLIPTIC_CURVE_INVALID          = 0,    /**< Dummy value */
        MKIMAGE_ELLIPTIC_CURVE_SECP192R1,               /**< NIST (192-bits) */
        MKIMAGE_ELLIPTIC_CURVE_SECP224R1,               /**< NIST (224-bits) */
        MKIMAGE_ELLIPTIC_CURVE_SECP256R1,               /**< NIST (256-bits) */
        MKIMAGE_ELLIPTIC_CURVE_SECP384R1,               /**< NIST (384-bits) */
        MKIMAGE_ELLIPTIC_CURVE_BP256R1,                 /**< Brainpool (256-bits) */
        MKIMAGE_ELLIPTIC_CURVE_BP384R1,                 /**< Brainpool (384-bits) */
        MKIMAGE_ELLIPTIC_CURVE_BP512R1,                 /**< Brainpool (512-bits) */
        MKIMAGE_ELLIPTIC_CURVE_CURVE25519,              /**< Curve25519, cannot be used in ECDSA */
        MKIMAGE_ELLIPTIC_CURVE_SECP192K1,               /**< Koblitz (192-bits) */
        MKIMAGE_ELLIPTIC_CURVE_SECP224K1,               /**< Koblitz (224-bits) */
        MKIMAGE_ELLIPTIC_CURVE_SECP256K1,               /**< Koblitz (256-bits) */
        MKIMAGE_ELLIPTIC_CURVE_EDWARDS25519,            /**< Edwards25519, for EdDSA */
} mkimage_elliptic_curve_t;

/** Hash method */
typedef enum {
        MKIMAGE_HASH_METHOD_INVALID             = 0,    /**< Dummy value */
        MKIMAGE_HASH_METHOD_SHA224,                     /**< SHA-224 */
        MKIMAGE_HASH_METHOD_SHA256,                     /**< SHA-256 */
        MKIMAGE_HASH_METHOD_SHA384,                     /**< SHA-384 */
        MKIMAGE_HASH_METHOD_SHA512,                     /**< SHA-512 */
} mkimage_hash_method_t;

/** Key type */
typedef enum {
        /** Asymmetric, public key used in signature verification */
        MKIMAGE_KEY_TYPE_PUBLIC,
        /** Symmetric key used in user data encryption */
        MKIMAGE_KEY_TYPE_SYMMETRIC,
} mkimage_key_type_t;

/** Key identifier */
typedef struct {
        /** Key type */
        mkimage_key_type_t type;
        /** Key ID - address or index */
        uint32_t id;
} mkimage_key_id_t;

/** Single secure image function optional data */
typedef struct {
        /** Number of keys which will be revoked */
        unsigned int rev_key_number;
        /** ID of the keys which will be revoked */
        mkimage_key_id_t *rev_key_id;
        /** Change minimal firmware version */
        bool change_min_fw_version;
        /**
         * Minimal firmware version string, if empty then the firmware version of the current
         * image will be used (only if 'change_min_fw_version' is true)
         */
        const char *min_fw_version;
} mkimage_secure_image_opt_data_t;

/**
 * \brief Convert status code to the status message
 *
 * \param [in] status                   status code
 *
 * \return constant string with status message, 'unknown' string if \p status has been not recognized
 *
 */
const char * DLLEXPORT mkimage_status_message(mkimage_status_t status);

/**
 * \brief Parse elliptic curve name
 *
 * \param [in] name                     elliptic curve name
 *
 * \return elliptic curve id
 */
mkimage_elliptic_curve_t DLLEXPORT mkimage_string_to_elliptic_curve(const char *name);

/**
 * \brief Parse hash method name
 *
 * \param [in] name                     hash method name
 *
 * \return hash method id
 */
mkimage_hash_method_t DLLEXPORT mkimage_string_to_hash_method(const char *name);

/**
 * \brief Create single image
 *
 * Function creates a single image which could be used as the SUOTA 1.1 image. The image is created
 * from binary and version file data. Image (application binary data part) could be encrypted using
 * AES CBC mode - in this case both \p iv and \p key must be given.
 *
 * \param [in]  in_size                 input data size
 * \param [in]  in                      input data (binary file content)
 * \param [in]  ver_size                version data size
 * \param [in]  ver                     version data (text file content)
 * \param [in]  key                     symmetric key used in AES CBC encryption (16 bytes)
 * \param [in]  iv                      initialization vector used in AES CBC encryption (16 bytes)
 * \param [out] out                     allocated buffer with image data
 * \param [out] out_size                output buffer size
 *
 * \note \p out should be freed after use.
 *
 * \return command execution status
 *
 */
mkimage_status_t DLLEXPORT mkimage_create_single_image(size_t in_size, const uint8_t *in,
                                                        size_t ver_size, const uint8_t *ver,
                                                        const uint8_t *key, const uint8_t *iv,
                                                                uint8_t **out, size_t *out_size);

/**
 * \brief Generate asymmetric key pair
 *
 * Function generates asymmetric key pair (public and private keys). Keys are generated using
 * specified elliptic curve. Buffers must have sufficient length. This keys could be used in
 * asymmetric, elliptic curve cryptography algorithms like ECDSA.
 *
 * \param [in]     elliptic_curve       elliptic curve id
 * \param [in/out] priv_key_length      buffer length as input, private key length as output
 * \param [out]    priv_key             private key
 * \param [in/out] pub_key_length       buffer length as input, public key length as output
 * \param [out]    pub_key              public key
 *
 * \return command execution status
 *
 */
mkimage_status_t DLLEXPORT mkimage_generate_asymmetric_key(mkimage_elliptic_curve_t elliptic_curve,
                                                                        size_t *priv_key_length,
                                                                        uint8_t *priv_key,
                                                                        size_t *pub_key_length,
                                                                                uint8_t *pub_key);

/**
 * \brief Generate symmetric key
 *
 * Function generates symmetric key. Key length is given as input parameter. Buffer must have
 * sufficient length. This key could be used in symmetric cryptography algorithms like AES.
 *
 * \param [in]  key_length              symmetric key length
 * \param [out] key                     symmetric key
 *
 * \return command execution status
 *
 */
mkimage_status_t DLLEXPORT mkimage_generate_symmetric_key(size_t key_length, uint8_t *key);

/**
 * \brief Create single secure image
 *
 * Function creates a single secure image which could be used as the SUOTA 1.4 image. The image is
 * created from binary, version file and some security data. This function is similar to the
 * \sa mkimage_create_single_image(). Generated image contains extra data related to image
 * security in the header (compared to the SUOTA 1.1 image). Security data is related to image
 * digital signature - header extension includes information about used elliptic curve, hash method,
 * id of the public key which should be used for image signature verification. Optionally it could
 * contain administration commands like public key revocation and change minimal FW version.
 *
 * \param [in]  in_size                 input data size
 * \param [in]  in                      input data (binary file content)
 * \param [in]  ver_size                version data size
 * \param [in]  ver                     version data (text file content)
 * \param [in]  elliptic_curve          elliptic curve id
 * \param [in]  hash_method             hash method
 * \param [in]  priv_key_length         private key length
 * \param [in]  priv_key                private key
 * \param [in]  key_id                  public key id (index or address in OTP)
 * \param [in]  opt_data                optional commands data, could be NULL
 * \param [out] out                     allocated buffer with image data
 * \param [out] out_size                output buffer size
 *
 * \return command execution status
 */
mkimage_status_t DLLEXPORT mkimage_create_single_secure_image(size_t in_size, const uint8_t *in,
                                                                size_t ver_size, const uint8_t *ver,
                                                                mkimage_elliptic_curve_t elliptic_curve,
                                                                mkimage_hash_method_t hash_method,
                                                                unsigned int priv_key_length,
                                                                const uint8_t *priv_key,
                                                                unsigned int key_id,
                                                                mkimage_secure_image_opt_data_t *opt_data,
                                                                uint8_t **out, size_t *out_size);

#ifdef __cplusplus
}
#endif

#endif /* MKIMAGE_H_ */
