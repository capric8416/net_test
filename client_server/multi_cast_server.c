/* 

multicast.c

The following program sends or receives multicast packets. If invoked
with one argument, it sends a packet containing the current time to an
arbitrarily chosen multicast group and UDP port. If invoked with no
arguments, it receives and prints these packets. Start it as a sender on
just one host and as a receiver on all the other hosts

*/

#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <time.h>
#include <stdio.h>

#define EXAMPLE_PORT 6000
#define EXAMPLE_GROUP "234.2.3.4"

main(int argc)
{
    struct sockaddr_in addr;
    int addrlen, sock, cnt;
    struct ip_mreq mreq;
    char message[50];

    /* set up socket */
    sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0)
    {
        perror("socket");
        exit(1);
    }
    bzero((char *)&addr, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(EXAMPLE_PORT);
    addrlen = sizeof(addr);

    /* send */
    addr.sin_addr.s_addr = inet_addr(EXAMPLE_GROUP);
    while (1)
    {
        time_t t = time(0);
        sprintf(message, "time is %-24.24s", ctime(&t));
        printf("sending: %s\n", message);
        cnt = sendto(sock, message, sizeof(message), 0,
                     (struct sockaddr *)&addr, addrlen);
        if (cnt < 0)
        {
            perror("sendto");
            exit(1);
        }
        sleep(5);
    }
}
