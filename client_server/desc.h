#ifndef _DESC_0EDBEBEA_H_
#define _DESC_0EDBEBEA_H_

#include <stdint.h>

#include <sys/time.h>

#include "crc.h"

#define MAX_NAME_LEN 8
#define MAX_VERSION_LEN 4

typedef struct _Desc
{
    int8_t name[MAX_NAME_LEN];         //  1 x 8 bytes
    uint16_t version[MAX_VERSION_LEN]; //  2 x 4 bytes
    uint32_t self_crc32;               //      4 bytes
    uint32_t header_crc32;             //      4 bytes
    uint32_t body_crc32;               //      4 bytes
    uint32_t header_length;            //      4 bytes
    uint64_t body_length;              //      8 bytes
    uint64_t timestamp;                //      8 bytes
} Desc;

#define SIZE_DESC sizeof(Desc)

#define INIT_DESC(desc, name, version, header, header_length, body, body_length)   \
    {                                                                              \
        memset((void *)&desc, 0, SIZE_DESC);                                       \
                                                                                   \
        memcpy((void *)desc.name, name, sizeof(uint8_t) * MAX_NAME_LEN);           \
        memcpy((void *)desc.version, version, sizeof(uint16_t) * MAX_VERSION_LEN); \
        desc.header_length = header_length;                                        \
        desc.body_length = body_length;                                            \
        desc.header_crc32 = crc32(header, header_length);                          \
        desc.body_crc32 = crc32(body, body_length);                                \
                                                                                   \
        struct timeval tv;                                                         \
        gettimeofday(&tv, NULL);                                                   \
        desc.timestamp = tv.tv_sec * 1000000 + tv.tv_usec;                         \
                                                                                   \
        desc.self_crc32 = crc32((const char *)&desc, SIZE_DESC);                   \
    }

#define NEW_MESSAGE(message, message_length, desc, header, header_length, body, body_length) \
    {                                                                                        \
        message_length = SIZE_DESC + header_length + body_length;                            \
        message = malloc(sizeof(uint8_t) * message_length);                                  \
                                                                                             \
        memcpy((void *)message, &desc, SIZE_DESC);                                           \
        memcpy((void *)(message + SIZE_DESC), header, header_length);                        \
        memcpy((void *)(message + SIZE_DESC + header_length), body, body_length);            \
    }

#define DEL_MESSAGE(message) \
    {                        \
        free(message);       \
    }

#endif
