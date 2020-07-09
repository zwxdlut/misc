/*
 * board.h
 *
 *  Created on: 2018Äê8ÔÂ21ÈÕ
 *      Author: Administrator
 */

#ifndef BOARD_H_
#define BOARD_H_

#include <stdint.h>

////////////////////////////////////////////////////////////////////////////////
/// Definitions
////////////////////////////////////////////////////////////////////////////////
#if defined EVB
    // LEDs
	#define LED0_PORT       					PORTD
    #define LED0_GPIO      						PTD
    #define LED0_PIN          					0U
	#define LED1_PORT       					PORTD
    #define LED1_GPIO       					PTD
    #define LED1_PIN           					16U
	#define LED2_PORT       					PORTD
    #define LED2_GPIO      						PTD
    #define LED2_PIN           					15U
	#define LED_ON          					0U
	#define LED_OFF         					1U

	// Button
    #define BTN_PORT        					PORTC
    #define BTN_GPIO        					PTC
    #define BTN_PIN         					13U
    #define BTN_PORT_IRQn   					PORTC_IRQn
#elif defined MX_TB
	// LEDs
	#define LED0_PORT       					PORTE
    #define LED0_GPIO       					PTE
    #define LED0_PIN           					8U
	#define LED1_PORT       					PORTB
    #define LED1_GPIO       					PTB
    #define LED1_PIN           					5U
	#define LED2_PORT       					PORTB
    #define LED2_GPIO       					PTB
    #define LED2_PIN           					4U
	#define LED_ON          					1U
	#define LED_OFF         					0U

	// Button
    #define BTN_PORT        					PORTA
    #define BTN_GPIO        					PTA
    #define BTN_PIN         					0U
	#define BTN_PORT_IRQn   					PORTA_IRQn

	// Accelerometer(MMA8452Q) INT2 pin
	#define ACCR_INT_PORT			         	PORTA
	#define ACCR_INT_GPIO    			        PTA
	#define ACCR_INT_PIN					    1u
	#define ACCR_INT_PORT_IRQn   		        PORTA_IRQn

	// Upper computer(EC20) pins
	#define UC_POWER_PORT						PORTE
	#define UC_POWER_GPIO 					    PTE
	#define UC_POWER_PIN						2U
	#define UC_WAKEUP_PORT						PORTA
	#define UC_WAKEUP_GPIO 					    PTA
	#define UC_WAKEUP_PIN						12U
	#define UC_RESET_PORT						PORTA
	#define UC_RESET_GPIO 					    PTA
	#define UC_RESET_PIN						13U
#else // Default board FRDM
	// LEDs
	#define LED0_PORT       					PORTE
    #define LED0_GPIO       					PTE
    #define LED0_PIN           					8U
	#define LED1_PORT       					PORTB
    #define LED1_GPIO       					PTB
    #define LED1_PIN           					5U
	#define LED2_PORT       					PORTB
    #define LED2_GPIO       					PTB
    #define LED2_PIN        	    			4U
	#define LED_ON          					1U
	#define LED_OFF         					0U

	// Button
    #define BTN_PORT        					PORTD
    #define BTN_GPIO        					PTD
    #define BTN_PIN         					15U
 	#define BTN_PORT_IRQn   					PORTD_IRQn
#endif

#define GPIO_WRITE_PIN(GPIO, PIN, LEVEL)        PINS_DRV_WritePin(GPIO, PIN, LEVEL)
#define GPIO_TOGGLE_PIN(GPIO, PIN)              PINS_DRV_TogglePins(GPIO, (1 << PIN))

// Power mode
#define PWR_MODE_SLEEP                      0u
#define PWR_MODE_DEEPSLEEP                  1u

////////////////////////////////////////////////////////////////////////////////
/// Function prototypes
////////////////////////////////////////////////////////////////////////////////
/// @brief : Initialize clocks, pins and power modes
void board_init(void);

/// @brief Function which initialize GPIO
void gpio_init(void);

/// @brief Function which de-initialize GPIO
void gpio_deinit(void);

/// @brief Get current system time since startup
/// @return Time in milliseconds
uint32_t sys_time_ms(void);

/// @brief Delay function
/// @param [in]: _ms Time is milliseconds
void delay_ms(const uint32_t _ms);

/// @brief Reset system
void sys_reset(void);

/// @brief : Transfer power mode
/// @param [in]: _mode Power mode, one of PWR_MODE_XXX
void pwr_mode_trans(const uint8_t _mode);

/// @brief : Enable independent watch dog
void iwdog_enable(void);

/// @brief : Refresh independent watch dog
void iwdog_refresh(void);

/// @brief : Disable independent watch dog
void iwdog_disable(void);

/// @brief : Enable window watch dog
void wwdog_enable(void);

/// @brief : Refresh window watch dog
void wwdog_refresh(void);

/// @brief : Disable window watch dog
void wwdog_disable(void);

#endif /* BOARD_H_ */
