################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include startup/subdir.mk
-include sdk/peripherals/src/subdir.mk
-include sdk/osal/subdir.mk
-include sdk/memory/src/subdir.mk
-include sdk/cpm/subdir.mk
-include sdk/ble_services/src/subdir.mk
-include sdk/ble/src/util/subdir.mk
-include sdk/ble/src/stack/plf/black_orca/src/driver/rf/src/subdir.mk
-include sdk/ble/src/stack/plf/black_orca/src/arch/main/ble/subdir.mk
-include sdk/ble/src/stack/modules/rwip/src/subdir.mk
-include sdk/ble/src/stack/modules/nvds/src/subdir.mk
-include sdk/ble/src/stack/ip/ble/profiles/subdir.mk
-include sdk/ble/src/stack/ip/ble/ll/src/rwble/subdir.mk
-include sdk/ble/src/manager/subdir.mk
-include sdk/ble/src/adapter/subdir.mk
-include sdk/ble/src/subdir.mk
-include sdk/adapters/src/subdir.mk
-include sdk/FreeRTOS/portable/MemMang/subdir.mk
-include sdk/FreeRTOS/portable/GCC/ARM_CM0/subdir.mk
-include sdk/FreeRTOS/subdir.mk
-include subdir.mk
-include objects.mk

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(strip $(ASM_DEPS)),)
-include $(ASM_DEPS)
endif
ifneq ($(strip $(S_UPPER_DEPS)),)
-include $(S_UPPER_DEPS)
endif
ifneq ($(strip $(C_DEPS)),)
-include $(C_DEPS)
endif
endif

-include ../makefile.defs

OPTIONAL_TOOL_DEPS := \
$(wildcard ../makefile.defs) \
$(wildcard ../makefile.init) \
$(wildcard ../makefile.targets) \


BUILD_ARTIFACT_NAME := custom-encrypted-service
BUILD_ARTIFACT_EXTENSION := elf
BUILD_ARTIFACT_PREFIX :=
BUILD_ARTIFACT := $(BUILD_ARTIFACT_PREFIX)$(BUILD_ARTIFACT_NAME)$(if $(BUILD_ARTIFACT_EXTENSION),.$(BUILD_ARTIFACT_EXTENSION),)

# Add inputs and outputs from these tool invocations to the build variables 
SECONDARY_FLASH += \
custom-encrypted-service.bin \

SECONDARY_SIZE += \
custom-encrypted-service.siz \


# All Target
all:
	+@$(MAKE) --no-print-directory pre-build && $(MAKE) --no-print-directory main-build

# Main-build Target
main-build: custom-encrypted-service.elf secondary-outputs

# Tool invocations
custom-encrypted-service.elf: $(OBJS) $(USER_OBJS) makefile objects.mk $(OPTIONAL_TOOL_DEPS)
	@echo 'Building target: $@'
	@echo 'Invoking: Cross ARM C Linker'
	arm-none-eabi-gcc -mcpu=cortex-m0 -mthumb -Os -fmessage-length=0 -fsigned-char -ffunction-sections -fdata-sections -Werror -Wall  -g3 -T "C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\apps\custom-encrypted-service/DA14683-00-Release_QSPI/mem.ld" -T "C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\apps\custom-encrypted-service/DA14683-00-Release_QSPI/sections.ld" -Xlinker --gc-sections -L"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\misc" -L"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\apps\custom-encrypted-service/../../sdk/sdk/interfaces/ble_stack/DA14683-00-Release" -Wl,-Map,"custom-encrypted-service.map" --specs=nano.specs --specs=nosys.specs -o "custom-encrypted-service.elf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '

custom-encrypted-service.bin: custom-encrypted-service.elf makefile objects.mk $(OPTIONAL_TOOL_DEPS)
	@echo 'Invoking: Cross ARM GNU Create Flash Image'
	arm-none-eabi-objcopy -O binary "custom-encrypted-service.elf"  "custom-encrypted-service.bin"
	@echo 'Finished building: $@'
	@echo ' '

custom-encrypted-service.siz: custom-encrypted-service.elf makefile objects.mk $(OPTIONAL_TOOL_DEPS)
	@echo 'Invoking: Cross ARM GNU Print Size'
	arm-none-eabi-size --format=berkeley "custom-encrypted-service.elf"
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) $(OBJS)$(SECONDARY_FLASH)$(SECONDARY_SIZE)$(ASM_DEPS)$(S_UPPER_DEPS)$(C_DEPS) custom-encrypted-service.elf
	-@echo ' '

pre-build:
	-@echo 'Generate linker scripts.'
	-make generate_ldscripts PRE_BUILD_EXTRA_DEFS="" LD_DEFS=-DRELEASE_BUILD IC_REV=B IC_STEP=B APP_CONFIG_H="C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\apps\custom-encrypted-service\config\custom_config_qspi.h" CC="arm-none-eabi-gcc" BSP_CONFIG_DIR="C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\config" LDSCRIPT_PATH="C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\ldscripts\ble_projects"
	-@echo ' '

secondary-outputs: $(SECONDARY_FLASH) $(SECONDARY_SIZE)

.PHONY: all clean dependents main-build pre-build

-include ../makefile.targets
