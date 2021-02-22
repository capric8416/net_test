#include <stdio.h>
#include <string.h>
#include <unistd.h>

#include <arpa/inet.h>
#include <sys/socket.h>

#include "desc.h"

#define PORT 8080

/////////////////////////// TODO - 仅保留一个crc


int main(int argc, char const *argv[])
{
	// Create socket
	int sock = 0;
	if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
	{
		return -1;
	}

	// Convert ip from text to binary
	struct sockaddr_in serv_addr;
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(PORT);
	if (inet_pton(AF_INET, "127.0.0.1", &serv_addr.sin_addr) <= 0)
	{
		return -2;
	}

	// Connect socket
	if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0)
	{
		return -3;
	}

	Desc desc;
	const char name[] = "cast";
	const uint16_t version[] = {2021, 1, 0, 1};

	char header[100];
	char body[100];

	int i = 0;
	while (++i)
	{
		printf("========== %04d ==========\n\n", i);

		printf("--------- header ---------\n");
		gets(header);
		size_t header_length = strlen(header);

		printf("\n---------- body ----------\n");
		gets(body);
		size_t body_length = strlen(body);

		INIT_DESC(desc, name, version, header, header_length, body, body_length);

		printf("\n---------- desc ----------\n"
			   "         name: %s\n"
			   "      version: %d.%d.%d.%d\n"
			   "header-length: %u\n"
			   "  body-length: %llu\n"
			   " header-crc32: %u\n"
			   "   body-crc32: %u\n"
			   "   self-crc32: %u\n"
			   "    timestamp: %llu\n\n\n",
			   desc.name,
			   desc.version[0], desc.version[1], desc.version[2], desc.version[3],
			   desc.header_length,
			   desc.body_length,
			   desc.header_crc32,
			   desc.body_crc32,
			   desc.self_crc32,
			   desc.timestamp);

		uint8_t *message;
		size_t message_length;
		NEW_MESSAGE(message, message_length, desc, header, header_length, body, body_length);

		send(sock, message, message_length, 0);

		DEL_MESSAGE(message);

		printf("\n");
	}

	return 0;
}
