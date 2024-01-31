SECTIONS {
        .bss : {
                // just need to define this so linker does not complain
                __bss_start__ = .;
                __bss_end__ = .;
        }

        .nvparam : {
                FILL(0xFF);

#define NVPARAM_AREA(NAME, PARTITION, OFFSET) \
                s = OFFSET;

#define NVPARAM_PARAM(TAG, OFFSET, LENGTH) \
                . = s + OFFSET; \
                *(section_ ## TAG)

#define NVPARAM_VARPARAM(TAG, OFFSET, LENGTH) \
                . = s + OFFSET; \
                *(section_ ## TAG ## _size) \
                *(section_ ## TAG)

#define NVPARAM_AREA_END()

// define this so preprocessor does not try to include ad_nvparam_defs.h
#define AD_NVPARAM_DEFS_H_
#include <platform_nvparam.h>

        }
}
