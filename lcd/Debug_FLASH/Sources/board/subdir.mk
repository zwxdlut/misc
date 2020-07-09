################################################################################
# Automatically-generated file. Do not edit!
################################################################################

-include ../../makefile.local

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS_QUOTED += \
"../Sources/board/board.c" \

C_SRCS += \
../Sources/board/board.c \

OBJS_OS_FORMAT += \
./Sources/board/board.o \

C_DEPS_QUOTED += \
"./Sources/board/board.d" \

OBJS += \
./Sources/board/board.o \

OBJS_QUOTED += \
"./Sources/board/board.o" \

C_DEPS += \
./Sources/board/board.d \


# Each subdirectory must supply rules for building sources it contributes
Sources/board/board.o: ../Sources/board/board.c
	@echo 'Building file: $<'
	@echo 'Executing target #22 $<'
	@echo 'Invoking: Standard S32DS C Compiler'
	arm-none-eabi-gcc "@Sources/board/board.args" -MMD -MP -MF"$(@:%.o=%.d)" -MT"$(@)" -o "Sources/board/board.o" "$<"
	@echo 'Finished building: $<'
	@echo ' '


