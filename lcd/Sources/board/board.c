/*
 * board.c
 *
 *  Created on: 2018Äê8ÔÂ21ÈÕ
 *      Author: Administrator
 */

#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#include "Cpu.h"
#include "board.h"

////////////////////////////////////////////////////////////////////////////////
/// Definitions
////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////
/// Function prototypes
////////////////////////////////////////////////////////////////////////////////
static void pin_irq_handler(void);
static void wdog_irq_handler(void);

////////////////////////////////////////////////////////////////////////////////
/// Functions
////////////////////////////////////////////////////////////////////////////////
void board_init(void)
{
    /* Initialize and configure clocks
     *  -   Setup system clocks, dividers
     *  -   see clock manager component for more details
     */
    CLOCK_SYS_Init(g_clockManConfigsArr, CLOCK_MANAGER_CONFIG_CNT,
            g_clockManCallbacksArr, CLOCK_MANAGER_CALLBACK_CNT);
    CLOCK_SYS_UpdateConfiguration(0U, CLOCK_MANAGER_POLICY_AGREEMENT);
}

void gpio_init(void)
{
#ifdef NUM_OF_CONFIGURED_PINS
    /* Initialize pins
     *  -   See PinSettings component for more info
     */
    PINS_DRV_Init(NUM_OF_CONFIGURED_PINS, g_pin_mux_InitConfigArr);
#endif

	// Setup LEDs
	PINS_DRV_SetMuxModeSel(LED0_PORT, LED0_PIN, PORT_MUX_AS_GPIO);
	PINS_DRV_SetPinDirection(LED0_GPIO, LED0_PIN, GPIO_OUTPUT_DIRECTION);
	PINS_DRV_WritePin(LED0_GPIO, LED0_PIN, LED_OFF);
	PINS_DRV_SetMuxModeSel(LED1_PORT, LED1_PIN, PORT_MUX_AS_GPIO);
	PINS_DRV_SetPinDirection(LED1_GPIO, LED1_PIN, GPIO_OUTPUT_DIRECTION);
	PINS_DRV_WritePin(LED1_GPIO, LED1_PIN, LED_OFF);
	PINS_DRV_SetMuxModeSel(LED2_PORT, LED2_PIN, PORT_MUX_AS_GPIO);
	PINS_DRV_SetPinDirection(LED2_GPIO, LED2_PIN, GPIO_OUTPUT_DIRECTION);
	PINS_DRV_WritePin(LED2_GPIO, LED2_PIN, LED_OFF);

    // Setup button
	PINS_DRV_SetMuxModeSel(BTN_PORT, BTN_PIN, PORT_MUX_AS_GPIO);
	PINS_DRV_SetPinDirection(BTN_GPIO, BTN_PIN, GPIO_INPUT_DIRECTION);
    PINS_DRV_SetPinIntSel(BTN_PORT, BTN_PIN, PORT_INT_RISING_EDGE);
    INT_SYS_InstallHandler(BTN_PORT_IRQn, &pin_irq_handler, NULL);
    INT_SYS_EnableIRQ(BTN_PORT_IRQn);

#ifdef USING_OS_FREERTOS
    /* The interrupt calls an interrupt safe API function - so its priority must
    be equal to or lower than configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY. */
    INT_SYS_SetPriority( BTN_PORT_IRQn, configLIBRARY_MAX_SYSCALL_INTERRUPT_PRIORITY );
#endif

#if defined MX_TB
	// Setup upper computer(EC20) pins
	PINS_DRV_SetMuxModeSel(UC_POWER_PORT, UC_POWER_PIN, PORT_MUX_AS_GPIO);
	PINS_DRV_SetPinDirection(UC_POWER_GPIO, UC_POWER_PIN, GPIO_OUTPUT_DIRECTION);
	PINS_DRV_WritePin(UC_POWER_GPIO, UC_POWER_PIN, 0);
	PINS_DRV_SetMuxModeSel(UC_RESET_PORT, UC_RESET_PIN, PORT_MUX_AS_GPIO);
	PINS_DRV_SetPinDirection(UC_RESET_GPIO, UC_RESET_PIN, GPIO_OUTPUT_DIRECTION);
	PINS_DRV_WritePin(UC_RESET_GPIO, UC_RESET_PIN, 0);
    // Install and enable accelerometer interrupt
    INT_SYS_InstallHandler(ACCR_INT_PORT_IRQn, &pin_irq_handler, NULL);
    INT_SYS_EnableIRQ(ACCR_INT_PORT_IRQn);
#endif
}

void gpio_deinit(void)
{
	// Disable and clear button interrupt
	INT_SYS_DisableIRQ(BTN_PORT_IRQn);
	PINS_DRV_ClearPinIntFlagCmd(BTN_PORT, BTN_PIN);

#if defined MX_TB
	// Disable accelerometer interrupt
	INT_SYS_DisableIRQ(ACCR_INT_PORT_IRQn);
#endif
}

uint32_t sys_time_ms(void)
{
	return OSIF_GetMilliseconds();
}

void delay_ms(const uint32_t _ms)
{
	OSIF_TimeDelay(_ms);
}

void sys_reset(void)
{
	SystemSoftwareReset();
}

void pwr_mode_trans(const uint8_t _mode)
{
	switch(_mode)
	{
	case PWR_MODE_DEEPSLEEP:
	    /* Allow very low power modes*/
	    SMC->PMPROT |= SMC_PMPROT_AVLP_MASK;

	    /* CLKBIASDIS=1: In VLPS mode, the bias currents and reference voltages
	     * for the following clock modules are disabled: SIRC, FIRC, PLL */
	    PMC->REGSC |= PMC_REGSC_BIASEN_MASK | PMC_REGSC_CLKBIASDIS_MASK;

	    /* Enable Stop Modes in the Core */
	    S32_SCB->SCR |= S32_SCB_SCR_SLEEPDEEP_MASK;

	    /*  Select VLPS Mode */
	    SMC->PMCTRL = SMC_PMCTRL_STOPM(0b10);
	    /*
	     *
	     *  Transition from RUN to VLPR
	     *
	     *                              */
	    if(0b01 == SMC->PMSTAT)
	    {
	        __asm("DSB");
	        __asm("ISB");
	        /* Call WFI to enter DeepSleep mode */
	        __asm("WFI");
	    }
	    else
	    {
	    	//error
	    }

	    /* Verify VLPSA bit is not set */
	    if (0 != (SMC->PMCTRL & SMC_PMCTRL_VLPSA_MASK))
	    {
	        //error
	    }
		break;
	default:
		break;
	}
}

void iwdog_enable(void)
{
	// Install IRQ handlers for WDOG/EWM
	INT_SYS_InstallHandler(WDOG_EWM_IRQn, wdog_irq_handler, (isr_t *)0);
    // Enable WDOG/EWM IRQ
    INT_SYS_EnableIRQ(WDOG_EWM_IRQn);
#ifdef INST_WATCHDOG1
	// Initialize WDOG
    WDOG_DRV_Init(INST_WATCHDOG1, &watchdog1_Config0);
#endif
}

void iwdog_refresh(void)
{
#ifdef INST_WATCHDOG1
	WDOG_DRV_Trigger(INST_WATCHDOG1);
#endif
}

void iwdog_disable(void)
{
#ifdef INST_WATCHDOG1
	WDOG_DRV_Deinit(INST_WATCHDOG1);
#endif
	// Disable WDOG/EWM IRQ
	INT_SYS_DisableIRQ(WDOG_EWM_IRQn);
}

void wwdog_enable(void)
{
	// Install IRQ handlers for WDOG/EWM
	INT_SYS_InstallHandler(WDOG_EWM_IRQn, wdog_irq_handler, (isr_t *)0);
    // Enable WDOG/EWM IRQ
    INT_SYS_EnableIRQ(WDOG_EWM_IRQn);
#ifdef EXTWDOG1
	// Initialize EWM
	EWM_DRV_Init(EXTWDOG1, &extWdog1_Config0);
#endif
}

void wwdog_refresh(void)
{
#ifdef EXTWDOG1
	EWM_DRV_Refresh(EXTWDOG1);
#endif
}

void wwdog_disable(void)
{
	// Disable WDOG/EWM IRQ
	INT_SYS_DisableIRQ(WDOG_EWM_IRQn);

}

////////////////////////////////////////////////////////////////////////////////
/// Local Functions
////////////////////////////////////////////////////////////////////////////////
//------------------------------------------------------------------------------
// IRQ handlers
//------------------------------------------------------------------------------
/// @brief Pin interrupt handler
static void pin_irq_handler(void)
{
    uint32_t pins = PINS_DRV_GetPortIntFlag(BTN_PORT) & ((1 << BTN_PIN)
#if defined MX_TB
    		| (1 << ACCR_INT_PIN )
#endif
			);
    if(pins != 0)
    {
        switch (pins)
        {
            case (1 << BTN_PIN):
                PINS_DRV_ClearPinIntFlagCmd(BTN_PORT, BTN_PIN);
                break;
#if defined MX_TB
            case (1 << ACCR_INT_PIN):
				PINS_DRV_ClearPinIntFlagCmd(ACCR_INT_PORT, ACCR_INT_PIN);
                break;
#endif
            default:
                PINS_DRV_ClearPortIntFlagCmd(BTN_PORT);
                break;
        }
    }
}

/// @brief Watch dog interrupt handler
static void wdog_irq_handler(void)
{
#ifdef INST_WATCHDOG1
	WDOG_DRV_Deinit(INST_WATCHDOG1);
#endif
	/* Disable WDOG/EWM IRQ */
	INT_SYS_DisableIRQ(WDOG_EWM_IRQn);
	gpio_deinit();
	sys_reset();
}

