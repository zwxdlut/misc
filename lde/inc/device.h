#pragma once

#ifndef __CAN_H__
#define __CAN_H__

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/*******************************************************************************
 * Definitions
 ******************************************************************************/

/*******************************************************************************
 * Function prototypes
 ******************************************************************************/
/**
 * Open and initialize a CAN device.
 *
 * @param [in] _name the CAN device name
 * @param [in] _filter the CAN filter ids
 * @param [in] _count the CAN filter ids count
 * @return the CAN file destriptor or -1(error)
 */
int32_t can_init(const char _name[], const uint32_t _filter[], const uint8_t _count);

/**
 * Open and initialize a UART device.
 *
 * @param [in] _name the UART device name
 * @param [in] _baudrate the UART baudrate
 * @param [in] _databits the data bits, must one value of 5, 6, 7, 8
 * @param [in] _parity the parity check bits, must one value as follow:
 * <ul>
 * <li>'O'- odd parity</li>
 * <li>'E'- even parity</li>
 * <li>'N'- no parity</li>
 * </ul>
 * @param [in] _stopbits the stop bits, 1 or 2
 * @return the UART file destriptor or error(-1)
 */
int32_t uart_init(const char _name[], const uint32_t _baudrate, const uint8_t _databits, const char _parity, const uint8_t _stopbits);

#ifdef __cplusplus
}
#endif

#endif // __CAN_H__
