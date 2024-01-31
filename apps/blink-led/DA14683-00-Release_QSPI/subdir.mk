################################################################################
# Automatically-generated file. Do not edit!
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../main.c 

OBJS += \
./main.o 

C_DEPS += \
./main.d 


# Each subdirectory must supply rules for building sources it contributes
%.o: ../%.c subdir.mk
	@echo 'Building file: $<'
	@echo 'Invoking: Cross ARM C Compiler'
	arm-none-eabi-gcc -mcpu=cortex-m0 -mthumb -Os -fmessage-length=0 -fsigned-char -ffunction-sections -fdata-sections -Werror  -g -Ddg_configBLACK_ORCA_IC_REV=BLACK_ORCA_IC_REV_B -Ddg_configBLACK_ORCA_IC_STEP=BLACK_ORCA_IC_STEP_B -DRELEASE_BUILD -I"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\adapters\include" -I"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\memory\include" -I"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\config" -I"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\include" -I"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\osal" -I"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\peripherals\include" -I"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\free_rtos\include" -I"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\sdk\sdk\bsp\system\sys_man\include" -include"C:\Users\amir2\Downloads\GitHub\BLE_DA14683-U\apps\blink_led\config\custom_config_qspi.h" -std=gnu11 -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" -c -o "$@" "$<"
	@echo 'Finished building: $<'
	@echo ' '


