################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../../../../../makefile.local

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS_QUOTED += \
"D:/NXP/S32DS_ARM_v2018.R1/S32DS/S32SDK_S32K1xx_RTM_3.0.0/platform/drivers/src/edma/edma_driver.c" \
"D:/NXP/S32DS_ARM_v2018.R1/S32DS/S32SDK_S32K1xx_RTM_3.0.0/platform/drivers/src/edma/edma_hw_access.c" \
"D:/NXP/S32DS_ARM_v2018.R1/S32DS/S32SDK_S32K1xx_RTM_3.0.0/platform/drivers/src/edma/edma_irq.c" \

C_SRCS += \
D:/NXP/S32DS_ARM_v2018.R1/S32DS/S32SDK_S32K1xx_RTM_3.0.0/platform/drivers/src/edma/edma_driver.c \
D:/NXP/S32DS_ARM_v2018.R1/S32DS/S32SDK_S32K1xx_RTM_3.0.0/platform/drivers/src/edma/edma_hw_access.c \
D:/NXP/S32DS_ARM_v2018.R1/S32DS/S32SDK_S32K1xx_RTM_3.0.0/platform/drivers/src/edma/edma_irq.c \

OBJS_OS_FORMAT += \
./SDK/platform/drivers/src/edma/edma_driver.o \
./SDK/platform/drivers/src/edma/edma_hw_access.o \
./SDK/platform/drivers/src/edma/edma_irq.o \

C_DEPS_QUOTED += \
"./SDK/platform/drivers/src/edma/edma_driver.d" \
"./SDK/platform/drivers/src/edma/edma_hw_access.d" \
"./SDK/platform/drivers/src/edma/edma_irq.d" \

OBJS += \
./SDK/platform/drivers/src/edma/edma_driver.o \
./SDK/platform/drivers/src/edma/edma_hw_access.o \
./SDK/platform/drivers/src/edma/edma_irq.o \

OBJS_QUOTED += \
"./SDK/platform/drivers/src/edma/edma_driver.o" \
"./SDK/platform/drivers/src/edma/edma_hw_access.o" \
"./SDK/platform/drivers/src/edma/edma_irq.o" \

C_DEPS += \
./SDK/platform/drivers/src/edma/edma_driver.d \
./SDK/platform/drivers/src/edma/edma_hw_access.d \
./SDK/platform/drivers/src/edma/edma_irq.d \


# Each subdirectory must supply rules for building sources it contributes
SDK/platform/drivers/src/edma/edma_driver.o: D:/NXP/S32DS_ARM_v2018.R1/S32DS/S32SDK_S32K1xx_RTM_3.0.0/platform/drivers/src/edma/edma_driver.c
	@echo 'Building file: $<'
	@echo 'Executing target #10 $<'
	@echo 'Invoking: Standard S32DS C Compiler'
	arm-none-eabi-gcc "@SDK/platform/drivers/src/edma/edma_driver.args" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "SDK/platform/drivers/src/edma/edma_driver.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '

SDK/platform/drivers/src/edma/edma_hw_access.o: D:/NXP/S32DS_ARM_v2018.R1/S32DS/S32SDK_S32K1xx_RTM_3.0.0/platform/drivers/src/edma/edma_hw_access.c
	@echo 'Building file: $<'
	@echo 'Executing target #11 $<'
	@echo 'Invoking: Standard S32DS C Compiler'
	arm-none-eabi-gcc "@SDK/platform/drivers/src/edma/edma_hw_access.args" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "SDK/platform/drivers/src/edma/edma_hw_access.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '

SDK/platform/drivers/src/edma/edma_irq.o: D:/NXP/S32DS_ARM_v2018.R1/S32DS/S32SDK_S32K1xx_RTM_3.0.0/platform/drivers/src/edma/edma_irq.c
	@echo 'Building file: $<'
	@echo 'Executing target #12 $<'
	@echo 'Invoking: Standard S32DS C Compiler'
	arm-none-eabi-gcc "@SDK/platform/drivers/src/edma/edma_irq.args" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "SDK/platform/drivers/src/edma/edma_irq.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '


