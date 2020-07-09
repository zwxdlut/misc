/*
 * spi.c
 *
 *  Created on: 2019Äê4ÔÂ28ÈÕ
 *      Author: Administrator
 */

#include <stdint.h>
#include <stdbool.h>

#include "Cpu.h"
#include "spi/spi.h"

/******************************************************************************
 * Definitions
 ******************************************************************************/
#ifdef SPI_0
#define SPI0_INST              SPI_0
#define SPI0_STATE             &spi_0State
#define SPI0_MASTER_CFG        &spi_0_MasterConfig0
#define SPI0_SLAVE_CFG         NULL
#else
#define SPI0_INST              0xFFu
#define SPI0_STATE             NULL
#define SPI0_MASTER_CFG        NULL
#define SPI0_SLAVE_CFG         NULL
#endif

#ifdef SPI_1
#define SPI1_INST              SPI_1
#define SPI1_STATE             &spi_1State
#define SPI1_MASTER_CFG        NULL
#define SPI1_SLAVE_CFG         &spi_1_SlaveConfig0
#else
#define SPI1_INST              0xFFu
#define SPI1_STATE             NULL
#define SPI1_MASTER_CFG        NULL
#define SPI1_SLAVE_CFG         NULL
#endif

#ifdef SPI_2
#define SPI2_INST              SPI_2
#define SPI2_STATE             &spi_2State
#define SPI2_MASTER_CFG        NULL
#define SPI2_SLAVE_CFG         NULL
#else
#define SPI2_INST              0xFFu
#define SPI2_STATE             NULL
#define SPI2_MASTER_CFG        NULL
#define SPI2_SLAVE_CFG         NULL
#endif

static uint8_t g_spi_inst[SPI2 + 1] = {SPI0_INST, SPI1_INST, SPI2_INST};
static lpspi_state_t *g_spi_state[SPI2 + 1] = {SPI0_STATE, SPI1_STATE, SPI2_STATE};
static const lpspi_master_config_t * g_spi_master_cfg[SPI2 + 1] = {SPI0_MASTER_CFG, SPI1_MASTER_CFG, SPI2_MASTER_CFG};
static const lpspi_slave_config_t *g_spi_slave_cfg[SPI2 + 1] = {SPI0_SLAVE_CFG, SPI1_SLAVE_CFG, SPI2_SLAVE_CFG};

/******************************************************************************
 * Local Function prototypes
 ******************************************************************************/
/******************************************************************************
 * Functions
 ******************************************************************************/
int32_t spi_init(const uint8_t _no, const bool _master)
{
	if(SPI2 < _no || 0xFFu == g_spi_inst[_no])
		return -1;

	if(_master)
	{
		if(NULL == g_spi_master_cfg[_no])
			return -1;

		/* SPI master configuration: clock speed: 500 kHz, 8 bits/frame, MSB first */
		LPSPI_DRV_MasterInit(g_spi_inst[_no], g_spi_state[_no], g_spi_master_cfg[_no]);
		/* Configure delay between transfer, delay between SCK and PCS and delay between PCS and SCK */
		LPSPI_DRV_MasterSetDelay(g_spi_inst[_no], 1, 1, 1);
	}
	else
	{
		if(NULL == g_spi_slave_cfg[_no])
			return -1;
		/* SPI slave configuration: clock spe DSPI_Mastered: 500 kHz, 8 bits/frame, MSB first */
		LPSPI_DRV_SlaveInit(g_spi_inst[_no], g_spi_state[_no],  g_spi_slave_cfg[_no]);
	}

	return 0;
}

int32_t spi_deinit(const uint8_t _no, const bool _master)
{
	if(SPI2 < _no || 0xFFu == g_spi_inst[_no])
		return -1;

	if(_master)
	{
		LPSPI_DRV_MasterAbortTransfer(g_spi_inst[_no]);
		LPSPI_DRV_MasterDeinit(g_spi_inst[_no]);
	}
	else
	{
		LPSPI_DRV_SlaveAbortTransfer(g_spi_inst[_no]);
		LPSPI_DRV_SlaveDeinit(g_spi_inst[_no]);
	}

	return 0;
}

int32_t spi_transer_blocking(const uint8_t _no, const uint8_t *const _tx_buf, uint8_t *const _rx_buf, const uint16_t _size
		,const uint32_t _timeout, const bool _master)
{
	if(SPI2 < _no || 0xFFu == g_spi_inst[_no])
		return -1;

	/* Start the blocking transfer */
	if(_master)
		LPSPI_DRV_MasterTransferBlocking(g_spi_inst[_no], _tx_buf, _rx_buf, _size, _timeout);
	else
		LPSPI_DRV_SlaveTransferBlocking(g_spi_inst[_no], _tx_buf, _rx_buf, _size, _timeout);

	return 0;
}

int32_t spi_transer(const uint8_t _no, const uint8_t *const _tx_buf, uint8_t *const _rx_buf, const uint16_t _size
		, const bool _master)
{
	if(SPI2 < _no || 0xFFu == g_spi_inst[_no])
		return -1;

	/* Start the non-blocking transfer */
	if(_master)
		LPSPI_DRV_MasterTransfer(g_spi_inst[_no], _tx_buf, _rx_buf, _size);
	else
		LPSPI_DRV_SlaveTransfer(g_spi_inst[_no], _tx_buf, _rx_buf, _size);

	return 0;
}
