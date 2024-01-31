################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../makefile.init

RM := rm -rf

# All of the sources participating in the build are defined here
-include sources.mk
-include startup/subdir.mk
-include sdk/sys_man/subdir.mk
-include sdk/peripherals/src/subdir.mk
-include sdk/osal/subdir.mk
-include sdk/memory/src/subdir.mk
-include sdk/free_rtos/portable/MemMang/subdir.mk
-include sdk/free_rtos/portable/GCC/ARM_CM0/subdir.mk
-include sdk/free_rtos/subdir.mk
-include sdk/adapters/src/subdir.mk
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


BUILD_ARTIFACT_NAME := blink-led
BUILD_ARTIFACT_EXTENSION := elf
BUILD_ARTIFACT_PREFIX :=
BUILD_ARTIFACT := $(BUILD_ARTIFACT_PREFIX)$(BUILD_ARTIFACT_NAME)$(if $(BUILD_ARTIFACT_EXTENSION),.$(BUILD_ARTIFACT_EXTENSION),)

# Add inputs and outputs from these tool invocations to the build variables 
SECONDARY_FLASH += \
blink-led.bin \

SECONDARY_SIZE += \
blink-led.siz \


# All Target
all:
	+@$(MAKE) --no-print-directory pre-build && $(MAKE) --no-print-directory main-build

# Main-build Target
main-build: blink-led.elf secondary-outputs

# Tool invocations
blink-led.elf: $(OBJS) $(USER_OBJS) makefile objects.mk $(OPTIONAL_TOOL_DEPS)
	@echo 'Building target: $@'
	@echo 'Invoking: Cross ARM C Linker'
	arm-none-eabi-gcc -mcpu=cortex-m0 -mthumb -Os -fmessage-length=0 -fsigned-char -ffunction-sections -fdata-sections -Werror  -g -T "C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\apps\blink_led/DA14683-00-Release_QSPI/mem.ld" -T "C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\apps\blink_led/DA14683-00-Release_QSPI/sections.ld" -Xlinker --gc-sections -L"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\misc" -Wl,-Map,"blink-led.map" --specs=nano.specs --specs=nosys.specs -o "blink-led.elf" $(OBJS) $(USER_OBJS) $(LIBS)
	@echo 'Finished building target: $@'
	@echo ' '

blink-led.bin: blink-led.elf makefile objects.mk $(OPTIONAL_TOOL_DEPS)
	@echo 'Invoking: Cross ARM GNU Create Flash Image'
	arm-none-eabi-objcopy -O binary "blink-led.elf"  "blink-led.bin"
	@echo 'Finished building: $@'
	@echo ' '

blink-led.siz: blink-led.elf makefile objects.mk $(OPTIONAL_TOOL_DEPS)
	@echo 'Invoking: Cross ARM GNU Print Size'
	arm-none-eabi-size --format=berkeley "blink-led.elf"
	@echo 'Finished building: $@'
	@echo ' '

# Other Targets
clean:
	-$(RM) $(OBJS)$(SECONDARY_FLASH)$(SECONDARY_SIZE)$(ASM_DEPS)$(S_UPPER_DEPS)$(C_DEPS) blink-led.elf
	-@echo ' '

pre-build:
	-@echo 'Generate linker scripts.'
	-make generate_ldscripts PRE_BUILD_EXTRA_DEFS="" IC_REV=B IC_STEP=B APP_CONFIG_H="C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\apps\blink_led\config\custom_config_qspi.h" CC="arm-none-eabi-gcc" BSP_CONFIG_DIR="C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\config" LDSCRIPT_PATH="C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\ldscripts\non_ble_projects"
	-@echo ' '

secondary-outputs: $(SECONDARY_FLASH) $(SECONDARY_SIZE)

.PHONY: all clean dependents main-build pre-build

-include ../makefile.targets
