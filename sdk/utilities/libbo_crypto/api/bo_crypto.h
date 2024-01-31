/**
 ****************************************************************************************
 *
 * @file bo_crypto.h
 *
 * @brief Cryptographic API.
 *
 * Copyright (C) 2017 Dialog Semiconductor.
 * This computer program includes Confidential, Proprietary Information
 * of Dialog Semiconductor. All Rights Reserved.
 *
 ****************************************************************************************
 */

#ifndef LIBBO_CRYPTO_H_
#define LIBBO_CRYPTO_H_

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
#extern "C" {
#endif

#ifdef _MSC_VER
#ifdef LIBBO_CRYPTO_EXPORTS
#define DLLEXPORT __declspec(dllexport)
#else
#define DLLEXPORT __declspec(dllimport)
#endif
#else
#define DLLEXPORT
#endif

/**
 * Elliptic curve
 */
typedef enum {
        ELLIPTIC_CURVE_NONE = 0,       /**< Dummy value */
        ELLIPTIC_CURVE_SECP192R1,      /**< NIST (192-bits) */
        ELLIPTIC_CURVE_SECP224R1,      /**< NIST (224-bits) */
        ELLIPTIC_CURVE_SECP256R1,      /**< NIST (256-bits) */
        ELLIPTIC_CURVE_SECP384R1,      /**< NIST (384-bits) */
        ELLIPTIC_CURVE_BP256R1,        /**< Brainpool (256-bits) */
        ELLIPTIC_CURVE_BP384R1,        /**< Brainpool (384-bits) */
        ELLIPTIC_CURVE_BP512R1,        /**< Brainpool (512-bits) */
        ELLIPTIC_CURVE_CURVE25519,     /**< Curve25519, cannot be used in ECDSA */
        ELLIPTIC_CURVE_SECP192K1,      /**< Koblitz (192-bits) */
        ELLIPTIC_CURVE_SECP224K1,      /**< Koblitz (224-bits) */
        ELLIPTIC_CURVE_SECP256K1,      /**< Koblitz (256-bits) */
        ELLIPTIC_CURVE_EDWARDS25519,   /**< Edwards25519, for EdDSA */
} elliptic_curve_t;

/**
 * Hash method
 */
typedef enum {
        HASH_METHOD_NONE = 0,   /**< Dummy value */
        HASH_METHOD_MD5,        /**< MD5 */
        HASH_METHOD_SHA1,       /**< SHA-1 */
        HASH_METHOD_SHA224,     /**< SHA-224 */
        HASH_METHOD_SHA256,     /**< SHA-256 */
        HASH_METHOD_SHA384,     /**< SHA-384 */
        HASH_METHOD_SHA512,     /**< SHA-512 */
} hash_method_t;

/**
 * Value and its size
 */
typedef struct {
        /** Value's size in bytes */
        size_t size;
        /** Buffer with value */
        uint8_t *value;
} crypto_buffer_t;

/**
 * \brief Allocate and initialize crypto_buffer_t instance
 *
 * Function allocates memory for buffer and sets its size. If \p buffer is given then its content is
 * copied to the value field of the output buffer. If \p buffer is NULL then value field of the
 * output buffer is zeroed.
 *
 * \param [in] buffer_size      requested buffer size
 * \param [in] buffer           buffer with data to copy, could be NULL
 *
 * \note Buffer allocated with this function must be freed with crypto_buffer_free().
 *
 * \return NULL if \p buffer_size is 0 or allocation error occurs, pointer to allocated buffer otherwise
 *
 */
crypto_buffer_t * DLLEXPORT crypto_buffer_alloc(size_t buffer_size, const uint8_t *buffer);

/**
 * \brief Initialize crypto_buffer_t instance
 *
 * Function initializes crypto-buffer intance in the static way. Value field in the output buffer
 * is not allocated - it points to the given \p buffer.
 *
 * \param [in/out] crypto_buffer    crypto-buffer instance which should be initialized
 * \param [in]     buffer_size      requested buffer size
 * \param [in]     buffer           pointer to data buffer
 *
 * \note Buffer initialized with this function cannot be freed with crypto_buffer_free().
 *
 */
void DLLEXPORT crypto_buffer_init(crypto_buffer_t *crypto_buffer, size_t buffer_size,
                                                                                uint8_t *buffer);

/**
 * \brief Free crypto_buffer_t instance
 *
 * \note Buffer allocated by crypto_buffer_alloc() should be freed in this function only.
 *
 * \param [in] buffer           pointer to the crypto_buffer_t instance
 *
 */
void DLLEXPORT crypto_buffer_free(crypto_buffer_t *buffer);

/**
 * \brief Generate symmetric key
 *
 * Function generates a symmetric key which could be used in symmetric cryptography algorithms.
 *
 * \param [in/out] key          requested key length and buffer as input and generated key as output
 *
 * \return true on success, false on failure
 *
 */
bool DLLEXPORT crypto_symmetric_key_gen(crypto_buffer_t *key);

/**
 * \brief Encrypt data using AES Cipher Block Chaining mode
 *
 * \note The input buffer length must be multiple of a block size (16 bytes). The output buffer has
 * the same length as the input buffer. \p init_vec should be 16-bytes in length. \p key must have
 * 16, 24 or 32 bytes in length.
 *
 * \param [in]  key             symmetric key
 * \param [in]  init_vec        initialization vector
 * \param [in]  input           data buffer
 * \param [out] output          output buffer (ciphertext)
 *
 * \return true on success, false on failure
 */
bool DLLEXPORT crypto_aes_cbc_encrypt(const crypto_buffer_t *key, const uint8_t *init_vec,
                                                const crypto_buffer_t *input, uint8_t *output);

/**
 * \brief Decrypt data using AES Cipher Block Chaining mode
 *
 * \note The output buffer has the same length as the input buffer. \p init_vec should be 16-bytes
 * in length. It must be the same as an initialization vector used during encryption.
 *
 * \param [in]  key             symmetric key
 * \param [in]  init_vec        initialization vector
 * \param [in]  input           input buffer (ciphertext)
 * \param [out] output          decrypted data buffer
 *
 * \return true on success, false on failure
 *
 */
bool DLLEXPORT crypto_aes_cbc_decrypt(const crypto_buffer_t *key, const uint8_t *init_vec,
                                                const crypto_buffer_t *input,  uint8_t *output);

/**
 * \brief Encrypt data using AES Counter mode
 *
 * \note The input buffer length must be multiple of a block size (16 bytes). The output buffer has
 * the same length as the input buffer. \p nonce should be 16-bytes in length. \p key must have
 * 16, 24 or 32 bytes in length.
 *
 * \param [in]  key             symmetric key
 * \param [in]  nonce           initial nonce
 * \param [in]  input           data buffer
 * \param [out] output          output buffer (ciphertext)
 *
 * \return true on success, false on failure
 */
bool DLLEXPORT crypto_aes_ctr_encrypt(const crypto_buffer_t *key, const uint8_t *nonce,
                                                const crypto_buffer_t *input,  uint8_t *output);

/**
 * CTR Mode uses the same algorithm for encryption and decryption.
 */
#define crypto_aes_ctr_decrypt crypto_aes_ctr_encrypt

/**
 * \brief Generate asymmetric keys pair
 *
 * Function generates asymmetric keys pair (private and public keys). The key pair is generate
 * using a specific elliptic curve.
 *
 * \note Key length depends on the used elliptic curve.
 *
 * \param [in]     elliptic_curve       elliptic curve
 * \param [in/out] priv_key             buffer as input, private key (d) as output
 * \param [in/out] pub_key              buffer as input, public key (X, Y) as output
 *
 * \return true on success, false on failure
 *
 */
bool DLLEXPORT crypto_asymmetric_key_pair_gen(elliptic_curve_t elliptic_curve,
                                               crypto_buffer_t *priv_key, crypto_buffer_t *pub_key);

/**
 * \brief Validate asymmetric keys pair
 *
 * Function validates asymmetric keys pair (private and public keys) with specified elliptic curve.
 * \p result is changed only when function was executed without errors.
 *
 * \param [in]  elliptic_curve  elliptic curve
 * \param [in]  priv_key        private key (d)
 * \param [in]  pub_key         public key (X, Y)
 * \param [out] result          validation result
 *
 * \return true on success, false on failure
 *
 */
bool DLLEXPORT crypto_asymmetric_key_pair_valid(elliptic_curve_t elliptic_curve,
                                                                const crypto_buffer_t *priv_key,
                                                                const crypto_buffer_t *pub_key,
                                                                                bool *result);

/**
 * \brief Generate ECDSA signature
 *
 * Function generates ECDSA signature using specified elliptic curve, hash method and private key.
 *
 * \note Curve25519 cannot be used in this function.
 *
 * \param [in]     elliptic_curve       elliptic curve
 * \param [in]     hash_method          hash method
 * \param [in]     priv_key             private key (d)
 * \param [in]     input                data buffer
 * \param [in/out] sig                  buffer as input, signature (r, s) as output
 *
 * \return true on success, false on failure
 *
 */
bool DLLEXPORT crypto_ecdsa_sig_gen(elliptic_curve_t elliptic_curve, hash_method_t hash_method,
                                                                const crypto_buffer_t *priv_key,
                                                                const crypto_buffer_t *input,
                                                                        crypto_buffer_t *sig);

/**
 * \brief Validate ECDSA signature
 *
 * Function validates ECDSA signature using specified elliptic curve, hash method and public key.
 *
 * \param [in]  elliptic_curve  elliptic curve
 * \param [in]  hash_method     hash method
 * \param [in]  pub_key         public key (X, Y)
 * \param [in]  input           data buffer
 * \param [in]  sig             signature (r, s)
 * \param [out] result          validation result
 *
 * \return true on success, false on failure
 *
 */
bool DLLEXPORT crypto_ecdsa_sig_valid(elliptic_curve_t elliptic_curve, hash_method_t hash_method,
                                        const crypto_buffer_t *pub_key, const crypto_buffer_t *input,
                                                        const crypto_buffer_t *sig, bool *result);

/**
 * \brief Generate EdDSA signature
 *
 * \param [in]     elliptic_curve       Edward Curve (must be ELLIPTIC_CURVE_EDWARDS25519)
 * \param [in]     priv_key             private key (d)
 * \param [in]     input                data buffer
 * \param [in/out] sig                  buffer as input, signature as output
 *
 * \return true on success, false on failure
 *
 */
bool DLLEXPORT crypto_eddsa_sig_gen(elliptic_curve_t elliptic_curve,
                                        const crypto_buffer_t *priv_key, const crypto_buffer_t *input,
                                                                        crypto_buffer_t *sig);

/**
 * \brief Validate EdDSA signature
 *
 * \param [in]  elliptic_curve  Edward Curve (must be ELLIPTIC_CURVE_EDWARDS25519)
 * \param [in]  pub_key         public key
 * \param [in]  input           data buffer
 * \param [in]  sig             signature
 * \param [out] result          validation result
 *
 * \return true on success, false on failure
 *
 */
bool DLLEXPORT crypto_eddsa_sig_valid(elliptic_curve_t elliptic_curve,
                                        const crypto_buffer_t *pub_key, const crypto_buffer_t *input,
                                                        const crypto_buffer_t *sig, bool *result);

#ifdef __cplusplus
}
#endif

#endif /* LIBBO_CRYPTO_H_ */
