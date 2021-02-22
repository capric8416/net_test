#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include <netinet/in.h>
#include <sys/socket.h>

#include "desc.h"

#define PORT 8080
/////////////////////////// TODO - 仅保留一个crc

int main(int argc, char const *argv[])
{

	// Creating socket file descriptor
	int server_fd;
	if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)
	{
		return -1;
	}

	// Forcefully attaching socket to the port 8080
	int opt = 1;
	if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)))
	{
		return -2;
	}

	struct sockaddr_in address;
	address.sin_family = AF_INET;
	address.sin_addr.s_addr = INADDR_ANY;
	address.sin_port = htons(PORT);
	int addrlen = sizeof(address);

	// Forcefully attaching socket to the port 8080
	if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0)
	{
		return -3;
	}
	if (listen(server_fd, 3) < 0)
	{
		return -4;
	}

	int sock;
	if ((sock = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen)) < 0)
	{
		return -5;
	}

	Desc desc;

	int i = 0;
	while (++i)
	{
		size_t count = read(sock, (void *)&desc, SIZE_DESC);
		if (count == 0)
		{
			break;
		}

		uint32_t desc_crc32 = desc.self_crc32;
		desc.self_crc32 = 0;
		assert(desc_crc32 == crc32((const char *)&desc, SIZE_DESC));

		char *header = (char *)calloc(desc.header_length + 1, sizeof(char));
		if (desc.header_length > 0)
		{
			read(sock, (void *)header, desc.header_length);
			assert(desc.header_crc32 == crc32(header, desc.header_length));
		}

		char *body = (char *)calloc(desc.body_length + 1, sizeof(char));
		if (desc.body_length > 0)
		{
			read(sock, (void *)body, desc.body_length);
			assert(desc.body_crc32 == crc32(body, desc.body_length));
		}

		printf("========== %04d ==========\n\n"
			   "---------- desc ----------\n"
			   "         name: %s\n"
			   "      version: %d.%d.%d.%d\n"
			   "header-length: %u\n"
			   "  body-length: %llu\n"
			   " header-crc32: %u\n"
			   "   body-crc32: %u\n"
			   "   self-crc32: %u\n"
			   "    timestamp: %llu\n\n\n"
			   "--------- header ---------\n"
			   "%s\n\n"
			   "---------- body ----------\n"
			   "%s\n\n",
			   i,
			   desc.name,
			   desc.version[0], desc.version[1], desc.version[2], desc.version[3],
			   desc.header_length,
			   desc.body_length,
			   desc.header_crc32,
			   desc.body_crc32,
			   desc_crc32,
			   desc.timestamp,
			   header,
			   body);

		free(header);
		free(body);
	}

	return 0;
}
