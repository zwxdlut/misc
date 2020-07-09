/*
 * board_config.h
 *
 *  Created on: 2019Äê3ÔÂ22ÈÕ
 *      Author: Administrator
 */

#ifndef BOARD_BOARD_CONFIG_H_
#define BOARD_BOARD_CONFIG_H_

/******************************************************************************
 * Definitions
 ******************************************************************************/
#define EVB
//#define FRDM
//#define MX_TB

#if defined EVB
	/* LED */
	#define LED0_PORT       					PORTD
    #define LED0_GPIO      						PTD
    #define LED0            					15U
	#define LED1_PORT       					PORTD
    #define LED1_GPIO       					PTD
    #define LED1            					16U
	#define LED2_PORT       					PORTD
    #define LED2_GPIO      						PTD
    #define LED2            					0U
	#define LED_ON          					0U
	#define LED_OFF         					1U

	/* Button */
    #define BTN_PORT        					PORTC
    #define BTN_GPIO        					PTC
    #define BTN_PIN         					13U
    #define BTN_PORT_IRQn   					PORTC_IRQn

	/* CAN RX and TX pins */
	#define CAN_0_RX_PORT                       PORTE
	#define CAN_0_RX_PIN                        4u
	#define CAN_0_TX_PORT                       PORTE
	#define CAN_0_TX_PIN                        5u
	#define CAN_1_RX_PORT                       PORTC
	#define CAN_1_RX_PIN                        16u
	#define CAN_1_TX_PORT                       PORTC
	#define CAN_1_TX_PIN                        17u
#elif defined FRDM
	/* LED */
	#define LED0_PORT       					PORTB
    #define LED0_GPIO       					PTB
    #define LED0           	    				4U
	#define LED1_PORT       					PORTB
    #define LED1_GPIO       					PTB
    #define LED1            					5U
	#define LED2_PORT       					PORTE
    #define LED2_GPIO       					PTE
    #define LED2            					8U
	#define LED_ON          					1U
	#define LED_OFF         					0U

	/* Button */
    #define BTN_PORT        					PORTD
    #define BTN_GPIO        					PTD
    #define BTN_PIN         					15U
 	#define BTN_PORT_IRQn   					PORTD_IRQn

	/* CAN RX and TX pins */
	#define CAN_0_RX_PORT                       PORTE
	#define CAN_0_RX_PIN                        4u
	#define CAN_0_TX_PORT                       PORTE
	#define CAN_0_TX_PIN                        5u
	#define CAN_1_RX_PORT                       PORTC
	#define CAN_1_RX_PIN                        16u
	#define CAN_1_TX_PORT                       PORTC
	#define CAN_1_TX_PIN                        17u
#elif defined MX_TB
	/* LED */
	#define LED0_PORT       					PORTB
    #define LED0_GPIO       					PTB
    #define LED0            					4U
	#define LED1_PORT       					PORTB
    #define LED1_GPIO       					PTB
    #define LED1            					5U
	#define LED2_PORT       					PORTE
    #define LED2_GPIO       					PTE
    #define LED2            					8U
	#define LED_ON          					1U
	#define LED_OFF         					0U

	/* Button */
    #define BTN_PORT        					PORTA
    #define BTN_GPIO        					PTA
    #define BTN_PIN         					0U
	#define BTN_PORT_IRQn   					PORTA_IRQn

	/* CAN RX and TX pins */
	#define CAN_0_RX_PORT                       PORTE
	#define CAN_0_RX_PIN                        4u
	#define CAN_0_TX_PORT                       PORTE
	#define CAN_0_TX_PIN                        5u
	#define CAN_1_RX_PORT                       PORTC
	#define CAN_1_RX_PIN                        6u
	#define CAN_1_TX_PORT                       PORTC
	#define CAN_1_TX_PIN                        7u

	/* CAN Transceiver(TJA1043) pins */
	#define CAN_TRANS_0_STB_N_PORT				PORTC
	#define CAN_TRANS_0_STB_N_GPIO    			PTC
	#define CAN_TRANS_0_STB_N_PIN				8u
	#define CAN_TRANS_0_EN_PORT				    PORTC
	#define CAN_TRANS_0_EN_GPIO    			    PTC
	#define CAN_TRANS_0_EN_PIN 					9u
	#define CAN_TRANS_0_INH_PORT				PORTC
	#define CAN_TRANS_0_INH_GPIO    			PTC
	#define CAN_TRANS_0_INH_PIN					17u
	#define CAN_TRANS_0_INH_PORT_IRQn   		PORTC_IRQn
	#define CAN_TRANS_1_STB_N_PORT				PORTC
	#define CAN_TRANS_1_STB_N_GPIO				PTC
	#define CAN_TRANS_1_STB_N_PIN				14u
	#define CAN_TRANS_1_EN_PORT    				PORTC
	#define CAN_TRANS_1_EN_GPIO    				PTC
	#define CAN_TRANS_1_EN_PIN 					15u
	#define CAN_TRANS_1_INH_PORT				PORTB
	#define CAN_TRANS_1_INH_GPIO    			PTB
	#define CAN_TRANS_1_INH_PIN					2u
	#define CAN_TRANS_1_INH_PORT_IRQn   		PORTB_IRQn

	/* Interrupt pin <- accelerometer(MMA8452Q) INT2 pin */
	#define ACCR_INT_PORT			         	PORTA
	#define ACCR_INT_GPIO    			        PTA
	#define ACCR_INT_PIN					    1u
	#define ACCR_INT_PORT_IRQn   		        PORTA_IRQn

	/* Host computer(EC20) power pin */
	#define HC_POWER_PORT						PORTA
	#define HC_POWER_GPIO 					    PTA
	#define HC_POWER_PIN						12U
#else
#endif

#define PWR_MODE_RUN                            0u
#define PWR_MODE_SLEEP                          1u
#define PWR_MODE_DEEPSLEEP                      2u


#endif /* BOARD_BOARD_CONFIG_H_ */
