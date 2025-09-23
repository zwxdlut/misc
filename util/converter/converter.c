#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdlib.h>

#include <iconv.h>

#include "converter.h"
#include "log.h"

#define TAG "converter"

/*******************************************************************************
 * Definitions
 ******************************************************************************/

/*******************************************************************************
 * Local function prototypes
 ******************************************************************************/

/*******************************************************************************
 * Functions
 ******************************************************************************/
void print_buffer(const char _prefix[], const uint32_t _id, const void *_buf, const size_t _size)
{
#ifdef _UDEBUG
    if (NULL == _buf)
    {
        LOGE("BUFFER", "%s: Buffer is null!\n", _prefix);
    }

    char str[4 * _size + strlen(_prefix) + 100];
    uint8_t *buf = (uint8_t*)_buf;
    
    sprintf(str, "%s(0x%X,%ld): ", _prefix, _id, _size);

    for (size_t i = 0; i < _size; i++)
    {
        char s[10] = "";

        sprintf(s, "%02X ", buf[i]);
        strcat(str, s);
    }

    strcat(str, "\n");

    LOGD("BUFFER", "%s", str);
#endif
}

void bytes_to_string(const void *_bytes, const size_t _size, char _str[])
{
    if (NULL == _bytes || NULL == _str)
    {
        LOGE(TAG, "bytes_to_string: Bytes or string is null!\n");   
    }

    uint8_t *bytes = (uint8_t*)_bytes;
    
    strcpy(_str, "");
    
    for (size_t i = 0; i < _size; i++)
    {
        char s[3] = "";

        sprintf(s, "%02X", bytes[i]);
        strcat(_str, s);
    }		
}

void string_to_bcd(const char _str[], uint8_t _bcd[], const size_t _size)
{
    if (NULL == _bcd)
    {       
        LOGE(TAG, "string_to_bcd: Buffer is null!\n"); 
    }

    size_t len = strlen(_str);
    bool is_even = !(len % 2);

    memset(_bcd, 0, _size);

    for (size_t i = 0; i < len; ++i)
    {
        char c = _str[i];
        int value = atoi(&c);
        int j = (2 * _size - len + i) / 2;

        if (j >= _size)
        {
            LOGE(TAG, "string_to_bcd: Out of range!\n"); 
            return;
        }
        
        _bcd[(2 * _size - len + i) / 2] |= value << (4 * ((is_even ? i + 1 : i) % 2));
    }
}

int code_convert(char *from_charset, char *to_charset, char *inbuf, size_t inlen, char *outbuf, size_t outlen) 
{
    iconv_t cd;
    char **pin = &inbuf;
    char **pout = &outbuf;

    cd = iconv_open(to_charset, from_charset);
    if (cd == 0)
        return -1;
    memset(outbuf, 0, outlen);
    if (iconv(cd, pin, &inlen, pout, &outlen) != 0)
        return -1;
    iconv_close(cd);
    *pout = '\0';

    return 0;
}

int utf8_to_gbk(char *inbuf, size_t inlen, char *outbuf, size_t outlen) 
{
    return code_convert((char*)"utf-8", (char*)"gb2312", inbuf, inlen, outbuf, outlen);
}

int gbk_to_utf8(char *inbuf, size_t inlen, char *outbuf, size_t outlen) 
{
    return code_convert((char*)"gb2312", (char*)"utf-8", inbuf, inlen, outbuf, outlen);
}

/*******************************************************************************
 * Local functions
 ******************************************************************************/