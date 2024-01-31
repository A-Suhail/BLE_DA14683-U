#include <stdint.h>

#define NVPARAM_PARAM_VALUE(TAG, TYPE, ...) \
        TYPE param_ ## TAG[] __attribute__((section("section_" #TAG))) __attribute__((aligned(1))) = { __VA_ARGS__ }; \
        uint16_t param_ ## TAG ## _size __attribute__((section("section_" #TAG "_size"))) __attribute__((aligned(1))) = sizeof(param_ ##TAG);

#include <platform_nvparam_values.h>

#define NVPARAM_AREA(NAME, PARTITION, OFFSET)

#define NVPARAM_PARAM(TAG, OFFSET, LENGTH) \
                char sizeofcheck_ ## TAG[LENGTH - sizeof(param_ ## TAG)];

#define NVPARAM_VARPARAM(TAG, OFFSET, LENGTH) \
                char sizeofcheck_ ## TAG[LENGTH - sizeof(param_ ## TAG) - 2];

#define NVPARAM_AREA_END()

// define this so preprocessor does not try to include ad_nvparam_defs.h
#define AD_NVPARAM_DEFS_H_
#include <platform_nvparam.h>

// dummy main
int main() { }

