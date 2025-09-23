#ifndef __CONVERTER_H__
#define __CONVERTER_H__

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stddef.h>

/*******************************************************************************
 * Definitions
 ******************************************************************************/

/*******************************************************************************
 * Function prototypes
 ******************************************************************************/
void print_buffer(const char _prefix[], const uint32_t _id, const void *_buf, const size_t _size);

void bytes_to_string(const void *_bytes, const size_t _size, char _str[]);

void string_to_bcd(const char _str[], uint8_t _bcd[], const size_t _size);

int code_convert(char *from_charset, char *to_charset, char *inbuf, size_t inlen, char *outbuf, size_t outlen);

int utf8_to_gbk(char *inbuf, size_t inlen, char *outbuf, size_t outlen);

int gbk_to_utf8(char *inbuf, size_t inlen, char *outbuf, size_t outlen);

#ifdef __cplusplus
}
#endif

#endif // __CONVERTER_H__
