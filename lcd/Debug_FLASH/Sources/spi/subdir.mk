################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../../makefile.local

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS_QUOTED += \
"../Sources/spi/spi.c" \

C_SRCS += \
../Sources/spi/spi.c \

OBJS_OS_FORMAT += \
./Sources/spi/spi.o \

C_DEPS_QUOTED += \
"./Sources/spi/spi.d" \

OBJS += \
./Sources/spi/spi.o \

OBJS_QUOTED += \
"./Sources/spi/spi.o" \

C_DEPS += \
./Sources/spi/spi.d \


# Each subdirectory must supply rules for building sources it contributes
Sources/spi/spi.o: ../Sources/spi/spi.c
	@echo 'Building file: $<'
	@echo 'Executing target #24 $<'
	@echo 'Invoking: Standard S32DS C Compiler'
	arm-none-eabi-gcc "@Sources/spi/spi.args" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "Sources/spi/spi.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '


