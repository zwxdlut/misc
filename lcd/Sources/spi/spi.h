/*
 * spi.h
 *
 *  Created on: 2019Äê4ÔÂ28ÈÕ
 *      Author: Administrator
 */

#ifndef SPI_SPI_H_
#define SPI_SPI_H_

/******************************************************************************
 * Definitions
 ******************************************************************************/
#define SPI0              0u
#define SPI1              1u
#define SPI2              2u

/******************************************************************************
 * Function prototypes
 ******************************************************************************/
/*
 * @brief : Initializes SPI device
 * @param [in]: _no     SPI device number
 * @param [in]: _master Definite if the SPI device is master or slave
 * @return success(0) or failure(other values)
 */
int32_t spi_init(const uint8_t _no, const bool _master);

/*
 * @brief : De-initializes SPI device
 * @param [in]: _no     SPI device number
 * @param [in]: _master Definite if the SPI device is master or slave
 * @return success(0) or failure(other values)
 */
int32_t spi_deinit(const uint8_t _no, const bool _master);

/*
 * @brief : Simultaneously transfers(sends and receives) data on the SPI bus with blocking mode
 * @param [in]: _no      SPI number
 * @param [in]: _tx_buf  Sending buffer
 * @param [in]: _rx_buf  Receiving number
 * @param [in]: _size    Transfer size in bytes
 * @param [in]: _timeout Timeout in milliseconds
 * @param [in]: _master  Definite if the SPI is master or slave
 * @return success(0) or failure(other values)
 */
int32_t spi_transer_blocking(const uint8_t _no, const uint8_t *const _tx_buf, uint8_t *const _rx_buf, const uint16_t _size
		,const uint32_t _timeout, const bool _master);
/*
 * @brief : Simultaneously transfers(sends and receives) data on the SPI bus with non-blocking mode
 * @param [in]: _no     SPI number
 * @param [in]: _tx_buf Sending buffer
 * @param [in]: _rx_buf Receiving number
 * @param [in]: _size   Transfer size in bytes
 * @param [in]: _master Definite if the SPI is master or slave
 * @return success(0) or failure(other values)
 */
int32_t spi_transer(const uint8_t _no, const uint8_t *const _tx_buf, uint8_t *const _rx_buf, const uint16_t _size
		, const bool _master);

#endif /* SPI_SPI_H_ */
