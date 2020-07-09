/* 
 * Copyright (c) 2015 - 2016 , Freescale Semiconductor, Inc.                             
 * Copyright 2016-2017 NXP                                                                    
 * All rights reserved.                                                                  
 *                                                                                       
 * THIS SOFTWARE IS PROVIDED BY NXP "AS IS" AND ANY EXPRESSED OR
 * IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 * IN NO EVENT SHALL NXP OR ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 * INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
 * HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
 * STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
 * IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 * THE POSSIBILITY OF SUCH DAMAGE.                          
 */
/* ###################################################################
**     Filename    : main.c
**     Project     : lpspi_dma_s32k144
**     Processor   : S32K144_100
**     Version     : Driver 01.00
**     Compiler    : GNU C Compiler
**     Date/Time   : 2017-08-02, 14:08, # CodeGen: 1
**     Abstract    :
**         Main module.
**         This module contains user's application code.
**     Settings    :
**     Contents    :
**         No public methods
**
** ###################################################################*/
/*!
** @file main.c
** @version 01.00
** @brief
**         Main module.
**         This module contains user's application code.
*/
/*!
**  @addtogroup main_module main module documentation
**  @{
*/
/* MODULE main */


/* Including needed modules to compile this module/procedure */
#include "Cpu.h"
#include "clockMan1.h"
#include "pin_mux.h"
#include "spi_0.h"
#include "dmaController1.h"

#include "board/board.h"
#include "spi/spi.h"
#include "image_data.h"

  volatile int exit_code = 0;
/* User includes (#include below this line is not maintained by Processor Expert) */
#include <stdint.h>
#include <stdbool.h>

/* LCD pins */
#define LCD_RS_PORT      PORTA
#define LCD_RS_GIIO      PTA
#define LCD_RS_PIN       1u

#define                  USE_LANDSCAPE

/* Define colors */
#define RED  		     0xf800
#define GREEN		     0x07e0
#define BLUE 		     0x001f
#define WHITE		     0xffff
#define BLACK		     0x0000
#define YELLOW           0xFFE0
#define GRAY0            0xEF7D
#define GRAY1            0x8410
#define GRAY2            0x4208

void delay(volatile uint32_t _time)
{
	uint32_t i, j;
	for(i=0; i < _time;i++)
		for(j=0; j < 250; j++);
}

void lcd_write_cmd(uint8_t _data)
{
	PINS_DRV_WritePin(LCD_RS_GIIO, LCD_RS_PIN, 0u);
	spi_transer_blocking(SPI0, &_data, NULL, 1u, OSIF_WAIT_FOREVER, true);
}

void lcd_write_data8(uint8_t _data)
{
	PINS_DRV_WritePin(LCD_RS_GIIO, LCD_RS_PIN, 1u);
	spi_transer_blocking(SPI0, &_data, NULL, 1u, OSIF_WAIT_FOREVER, true);
}

void lcd_write_data16(uint16_t _data)
{
	PINS_DRV_WritePin(LCD_RS_GIIO, LCD_RS_PIN, 1u);
	spi_transer_blocking(SPI0, &_data, NULL, 2u, OSIF_WAIT_FOREVER, true);
}

void lcd_init()
{
	/* Configure RS pin */
	PINS_DRV_SetMuxModeSel(LCD_RS_PORT, LCD_RS_PIN, PORT_MUX_AS_GPIO);
	PINS_DRV_SetPinDirection(LCD_RS_GIIO, LCD_RS_PIN, GPIO_OUTPUT_DIRECTION);
	PINS_DRV_WritePin(LCD_RS_GIIO, LCD_RS_PIN, 0u);

	/* LCD Init For 1.44Inch LCD Panel with ST7735R */
	lcd_write_cmd(0x11);
	delay(120);

	/* ST7735R Frame Rate */
	lcd_write_cmd(0xB1);
	lcd_write_data8(0x01);
	lcd_write_data8(0x2C);
	lcd_write_data8(0x2D);

	lcd_write_cmd(0xB2);
	lcd_write_data8(0x01);
	lcd_write_data8(0x2C);
	lcd_write_data8(0x2D);

	lcd_write_cmd(0xB3);
	lcd_write_data8(0x01);
	lcd_write_data8(0x2C);
	lcd_write_data8(0x2D);
	lcd_write_data8(0x01);
	lcd_write_data8(0x2C);
	lcd_write_data8(0x2D);

	lcd_write_cmd(0xB4); /**< Column inversion */
	lcd_write_data8(0x07);

	/* ST7735R Power Sequence */
	lcd_write_cmd(0xC0);
	lcd_write_data8(0xA2);
	lcd_write_data8(0x02);
	lcd_write_data8(0x84);
	lcd_write_cmd(0xC1);
	lcd_write_data8(0xC5);

	lcd_write_cmd(0xC2);
	lcd_write_data8(0x0A);
	lcd_write_data8(0x00);

	lcd_write_cmd(0xC3);
	lcd_write_data8(0x8A);
	lcd_write_data8(0x2A);
	lcd_write_cmd(0xC4);
	lcd_write_data8(0x8A);
	lcd_write_data8(0xEE);

	lcd_write_cmd(0xC5); /**< VCOM */
	lcd_write_data8(0x0E);

	lcd_write_cmd(0x36); /**< MX, MY, RGB mode */
#ifdef USE_LANDSCAPE
	lcd_write_data8(0xA8); //ÊúÆÁC8 ºáÆÁ08 A8
#else
	lcd_write_data8(0xC8); //ÊúÆÁC8 ºáÆÁ08 A8
#endif

	/* ST7735R Gamma Sequence */
	lcd_write_cmd(0xe0);
	lcd_write_data8(0x0f);
	lcd_write_data8(0x1a);
	lcd_write_data8(0x0f);
	lcd_write_data8(0x18);
	lcd_write_data8(0x2f);
	lcd_write_data8(0x28);
	lcd_write_data8(0x20);
	lcd_write_data8(0x22);
	lcd_write_data8(0x1f);
	lcd_write_data8(0x1b);
	lcd_write_data8(0x23);
	lcd_write_data8(0x37);
	lcd_write_data8(0x00);
	lcd_write_data8(0x07);
	lcd_write_data8(0x02);
	lcd_write_data8(0x10);

	lcd_write_cmd(0xe1);
	lcd_write_data8(0x0f);
	lcd_write_data8(0x1b);
	lcd_write_data8(0x0f);
	lcd_write_data8(0x17);
	lcd_write_data8(0x33);
	lcd_write_data8(0x2c);
	lcd_write_data8(0x29);
	lcd_write_data8(0x2e);
	lcd_write_data8(0x30);
	lcd_write_data8(0x30);
	lcd_write_data8(0x39);
	lcd_write_data8(0x3f);
	lcd_write_data8(0x00);
	lcd_write_data8(0x07);
	lcd_write_data8(0x03);
	lcd_write_data8(0x10);

	lcd_write_cmd(0x2a);
	lcd_write_data8(0x00);
	lcd_write_data8(0x00+2);
	lcd_write_data8(0x00);
	lcd_write_data8(0x80+2);

	lcd_write_cmd(0x2b);
	lcd_write_data8(0x00);
	lcd_write_data8(0x00+3);
	lcd_write_data8(0x00);
	lcd_write_data8(0x80+3);

	lcd_write_cmd(0xF0); /**< Enable test command */
	lcd_write_data8(0x01);
	lcd_write_cmd(0xF6); /**< Disable ram power save mode */
	lcd_write_data8(0x00);

	lcd_write_cmd(0x3A); /**< 65k mode */
	lcd_write_data8(0x05);

	lcd_write_cmd(0x29); /**< Display on */
}

void lcd_set_region(uint32_t _x_start, uint32_t _y_start, uint32_t _x_end, uint32_t _y_end)
{
#ifdef USE_LANDSCAPE
	lcd_write_cmd(0x2a);
	lcd_write_data8(0x00);
	lcd_write_data8(_x_start + 3);
	lcd_write_data8(0x00);
	lcd_write_data8(_x_end + 3);

	lcd_write_cmd(0x2b);
	lcd_write_data8(0x00);
	lcd_write_data8(_y_start + 2);
	lcd_write_data8(0x00);
	lcd_write_data8(_y_end + 2);
#else
	lcd_write_cmd(0x2a);
	lcd_write_data8(0x00);
	lcd_write_data8(_x_start + 2);
	lcd_write_data8(0x00);
	lcd_write_data8(_x_end + 2);

	lcd_write_cmd(0x2b);
	lcd_write_data8(0x00);
	lcd_write_data8(_y_start + 3);
	lcd_write_data8(0x00);
	lcd_write_data8(_y_end + 3);
#endif
	lcd_write_cmd(0x2c);

}

void lcd_clear(uint32_t _color)
{
	uint8_t i, j;
	lcd_set_region(0, 0, 128-1, 128-1);
	for (i = 0; i < 128; i++)
    	for (j = 0; j < 128; j++)
        	lcd_write_data16(_color);
}

void lcd_show_image(const uint8_t *_buf)
{
  	int i,j,k;
	unsigned char picH,picL;
	lcd_clear(WHITE);

	for(k=0; k < 3; k++)
	{
	   	for(j = 0;j < 3; j++)
		{
	   		lcd_set_region(40 * j, 40 * k, 40 * j + 39, 40 * k + 39);
		    for(i = 0;i < 40 * 40; i++)
			 {
			 	picL=*(_buf + i*2);
				picH=*(_buf + i * 2 + 1);
				lcd_write_data16(picH << 8 | picL);
			 }
		 }
	}
}

/*!
  \brief The main function for the project.
  \details The startup initialization sequence is the following:
 * - startup asm routine
 * - main()
*/
int main(void)
{

	/*** Processor Expert internal initialization. DON'T REMOVE THIS CODE!!! ***/
	#ifdef PEX_RTOS_INIT
	PEX_RTOS_INIT();                   /* Initialization of the selected RTOS. Macro is defined by the RTOS component. */
	#endif
	/*** End of Processor Expert internal initialization.                    ***/

	board_init();
	gpio_init(NULL);
	EDMA_DRV_Init(&dmaController1_State, &dmaController1_InitConfig0, edmaChnStateArray, edmaChnConfigArray, EDMA_CONFIGURED_CHANNELS_COUNT);
	spi_init(SPI0, true);
	lcd_init();

	while(1)
	{
		/*lcd_clear(RED);
		delay(500);
		lcd_clear(GREEN);
		delay(500);
		lcd_clear(BLUE);
		delay(500);
		lcd_clear(BLACK);
		delay(500);
		lcd_clear(WHITE);
		delay(500);*/

		lcd_show_image(g_image);
		delay(1500);
	}
 
	/*** Don't write any code pass this line, or it will be deleted during code generation. ***/
  /*** RTOS startup code. Macro PEX_RTOS_START is defined by the RTOS component. DON'T MODIFY THIS CODE!!! ***/
  #ifdef PEX_RTOS_START
    PEX_RTOS_START();                  /* Startup of the selected RTOS. Macro is defined by the RTOS component. */
  #endif
  /*** End of RTOS startup code.  ***/
  /*** Processor Expert end of main routine. DON'T MODIFY THIS CODE!!! ***/
  for(;;) {
    if(exit_code != 0) {
      break;
    }
  }
  return exit_code;
  /*** Processor Expert end of main routine. DON'T WRITE CODE BELOW!!! ***/
} /*** End of main routine. DO NOT MODIFY THIS TEXT!!! ***/

/* END main */
/*!
** @}
*/
/*
** ###################################################################
**
**     This file was created by Processor Expert 10.1 [05.21]
**     for the NXP C55 series of microcontrollers.
**
** ###################################################################
*/
