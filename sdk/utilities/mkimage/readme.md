MkImage {#mkimage}
==================

## Overview

`mkimage` is a command line tool for generating private and public keys and
generating images used for SUOTA.

Features:
- generate image for SUOTA from input file(s)
- generate symmetric keys
- generate asymmetric keys
- generate secure image files which use elliptic curves used in ECDSA or SdDSA
  algorithms to generate signature

## Usage

Run `mkimage` witout any parameter to see below description.
```
Usage depends on the option selected. Possible parameters:
#1 single           - generate single image
#2 multi            - generate multi image - output image contains 2 input
                      images
#3 gen_sym_key      - generate symmetric key or keys
#4 gen_asym_key     - generate asymmetric key or keys
#5 secure           - generate signed image file


Usage case #1:
mkimage single <in_file> <version_file> <out_file> [enc [<key> <iv>]]

parameters:
  in_file         input binary file which is converted to output image
  version_file    version file which contains version, timestamp and
                  housekeeping information (e.g. sw_version.h)
  out_file        output image file
  enc             use image encryption (AES, CBC)
  key             encryption key. String of 32 hex characters (without any
                  prefix). If no key is given, the default value is
                  used
  iv              initialization vector. String of 32 hex characters (without
                  any prefix). If no initialization vector is given,
                  the default value is used

note:
  The 'version_file' is usually called sw_version.h
  and this program looks in it for definitions like below:

  #define BLACKORCA_SW_VERSION "v_1.0.0.1"
  #define BLACKORCA_SW_VERSION_DATE "2015-03-11 14:04 "

example:
  mkimage single pxp_reporter.bin sw_version.h output.img
  mkimage single pxp_reporter.bin sw_version.h output.img enc
         123456789aBCdef1234567890deeac27 BCA123456789aBCdef1234567890deea


Usage case #2:
mkimage multi <destination> [<bootloader>] <in_image1> <offset1> <in_image2>
              <offset2> <offset3> [cfg <offset4>] <out_file>

parameters:
  destinations    where out_file is loaded - 'spi' or 'eeprom'
  bootloader      bootloader file at offset 0, if provided
  in_image1       first input image file loaded at <offset1>
  offset1         offset where <in_image1> is loaded (look at note below)
  in_image2       second input image file loaded at <offset2>
  offset2         offset where <in_image2> is loaded
                  (>= <offset1> + size of <in_image1>)
  offset3         offset where product header is loaded
                  (>= <offset2> + size of <in_image2>)
  cfg             add configuration to output image
  offset4         offset where configuration is loaded
  out_file        output image file

note:
  The offsets can be given either as decimal or hex numbers.
  If bootloader is provided <offset1> need to be given at least
  header size + bootloader size. Header size is equal 8 bytes for 'spi'
  destination and 32 bytes for 'eeprom'.

example:
  mkimage multi spi pxp_reporter.bin 0 pxp_reporter_2.bin 97056 194112 output.img
  mkimage multi spi bootloader pxp_reporter.bin 9000 pxp_reporter_2.bin 106056 203112
        output.img
  mkimage multi eeprom bootloader pxp_reporter.bin 9024 pxp_reporter_2.bin 106080 203136
        output.img


Usage case #3:
mkimage gen_sym_key [<keys_count> [<key_length>]]

parameters:
  keys_count      number of generated symmetric keys (> 0, default: 1)
  key_length      length of generated symmetric keys (> 0, default: 32 bytes)

example:
  mkimage gen_sym_key
  mkimage gen_sym_key 3 16

Usage case #4:
mkimage gen_asym_key <elliptic_curve> [<keys_count>]

parameters:
  elliptic_curve  Key pair is generated using elliptic curve. Supported elliptic
                  curves:
                  * NIST:         SECP192R1, SECP224R1, SECP256R1, SECP384R1
                  * Brainpool:    BP256R1, BP384R1, BP512R1
                  * Koblitz:      SECP192K1, SECP224K1, SECP256K1
                  * Curve25519:   CURVE25519
                  * Edward:       EDWARDS25519
  keys_count      number of generated asymmetric keys (> 0, default: 1)

example:
  mkimage gen_asym_key SECP192R1
  mkimage gen_asym_key BP512R1 6


Usage case #5:
mkimage secure <in_file> <version_file> <out_file> <elliptic_curve> <hash>
               <private_key> <key_id> [rev <cmd>] [min_ver [<version>]]

parameters:
  in_file         input binary file which is converted to output image
  version_file    version file which contains version, timestamp and
                  housekeeping information (e.g. sw_version.h)
  out_file        output image file
  elliptic_curve  elliptic curve used in ECDSA or EdDSA algorithms to generate
                  signature. Supported elliptic curves:
                  * For ECDSA:    SECP192R1, SECP224R1, SECP256R1
                  * For EdDSA     EDWARDS25519
  hash            Supported hash method:
                  * For ECDSA:    SHA-224, SHA-256, SHA-384, SHA-512
                  * For EdDSA:    SHA-512
  private_key     private key which is used in ECDSA/EdDSA - it must have
                  proper (for chosen elliptic curve) length. This key can be
                  generated by 'gen_asym_key' command with the same
                  <elliptic_curve> parameter.
  key_id          index or memory address of the key which should be used for
                  signature validation by bootloader. Supported key ID:
                  - 0, 1, 2, 3
  rev             use public key or keys revocation command
  cmd             public key or keys revocation command which should be revoked
                  (index or memory address). If more than one key is passed,
                  parameter should be given in quotation marks
                  (look at an example). Supported values:
                  - 1, 2, 3
  min_ver         use minimal version - default or given by user
  version         minimal version of firmware. String value which contains two
                  values separated by dot characters (e.g. 314.033 or 103.13).
                  Every additional dots and values after it will be skipped
                  (e.g. 343.3234.235.334 will be taken as 343.3234).
                  Maximum value of version between dots is 65535 (0xFFFF) ->
                  (65535.65535). If this value is not given, by default it is
                  taken from <version_file>

example:
  mkimage secure pxp_reporter.bin sw_version.h output.img SECP192R1 SHA-224
         BD9A333C56A9DBC99C4E9D71DE52E81F06CF90E383DE3BCF 1
  mkimage secure pxp_reporter.bin sw_version.h output.img SECP256R1 SHA-384
         6A34675F2F5885A4EDC9011D7B815E5999AE578D7804266A7383D79F72949EDD 2
         rev "1 3" min_ver 23.53
```
