NV Parameters image area creation script {#nvparam}
===================================================

## Overview

This script creates image of NV Parameters which can be then written directly to proper partition on
flash using `cli_programmer`. This process can be automated using `program_qspi_nvparam.sh` script
which can be launched directly from Eclipse.

## Installation procedure

The `create_nvparam.sh` script needs a valid path to GNU ARM Toolchain. It should be set in `ARM_TOOLCHAIN`
environment variable, e.g. `export ARM_TOOLCHAIN=/home/user/gcc-arm-none-eabi-4_9-2015q1/bin`.

When using the `program_qspi_nvparam.sh` script, it's possible to enter toolchain path via
interactive prompt when asked by the script.

## Script usage

### From command line

The `create_nvparam.sh` script needs both NV Prameters layout file (`platform_nvparam.h`) and
parameters values file (`platform_nvparam_values.h`) to be present. By default, these files are
stored in the `sdk/bsp/adapters/include` directory, but can be overridden per-project when copied to
project's `config` directory.

To create a `nvparam.bin` image execute the `create_nvparam.sh` script with parameters as follows:
- directory where `nvparam.bin` will be created
- paths to look for configuration files (e.g. project's `config` directory and SDK directory)

For example, to create `nvparam.bin` for `pxp_reporter` application execute as follows (assuming
current working directory is SDK root):

    utilities/nvparam/create_nvparam.sh . projects/dk_apps/demos/pxp_reporter/config sdk/bsp/adapters/include

### From Eclipse

The `program_qspi_nvparam.sh` script is provided to simplify image generation and QSPI flashing.
It can be accessed directly from Eclipse (assuming `scripts` project is imported into workspace).

- Select project in `Project Explorer` window
- Select `program_qspi_nvparam` from `Run -> External Tools` menu
- Follow instructions printed on console

Image is automatically generated in project's output directory and then written to QSPI at address
`0x80000` which is the default address of parameters partition.

## Script workflow

Below is short overview of how `create_nvparam.sh` creates `nvparam.bin` image file. This information
can be helpful to troubleshoot problems.

- `utilities/nvparam/symbols.c` file is compiled to have symbols for defined the NV Parameters values.
  Each value is placed in separate sections.

- `utilities/nvparam/sections.ld.h` is preprocessed to produce a linker script which places symbols
  from `symbols.o` at proper locations (as defined by nvparam offsets) relative to the `nvparam`
  section.

- The resulting files are used to create `nvparam.elf` which has the nvparam image embedded in the
  separete `nvparam` section.

- The `nvparam` section data is extracted to `nvparam.bin` using `objcopy`. The `nvparam.bin` file
  can be written directly to QSPI.
