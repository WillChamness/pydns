# PyDNS

A simple DNS client with no external dependencies

## Usage

```
usage: pydns [-h] [-d IPADDR] [-v] NAME

positional arguments:
  NAME                  the name to query

options:
  -h, --help            show this help message and exit
  -d IPADDR, --dns-server IPADDR
                        the DNS server to be queried. required if using Windows (default: use the first nameserver in /etc/resolv.conf)
  -v, --verbose         be as verbose as possible
```

## Known Limitations

- Only A records and CNAMEs are supported
- Reverse DNS lookup is not supported

## Example Output

```
$ python -m pydns -d 1.1.1.1 image.google.com
172.253.124.113
172.253.124.138
172.253.124.102
172.253.124.139
172.253.124.101
172.253.124.100

$ dig @1.1.1.1 image.google.com
(output omitted)

;; ANSWER SECTION:
image.google.com.       300     IN      CNAME   images.google.com.
images.google.com.      300     IN      CNAME   images.l.google.com.
images.l.google.com.    300     IN      A       173.194.219.102
images.l.google.com.    300     IN      A       173.194.219.101
images.l.google.com.    300     IN      A       173.194.219.139
images.l.google.com.    300     IN      A       173.194.219.113
images.l.google.com.    300     IN      A       173.194.219.138
images.l.google.com.    300     IN      A       173.194.219.100

;; Query time: 31 msec
;; SERVER: 1.1.1.1#53(1.1.1.1) (UDP)
;; WHEN: Mon Jul 07 22:21:14 EDT 2025
;; MSG SIZE  rcvd: 185
```

## Example Verbose Output

```
$ python -m pydns -d 1.1.1.1 image.google.com -v
Response from 1.1.1.1:
========== HEADER ==========
Transaction ID: 0x4478
Response: Message is a response
Opcode: Standard query (0)
Authoritative: Server is not an authority for domain
Truncated: Message is not truncated
Recursion desired: Do query recursively
Recursion available: Server can do recursive queries
Zero: zero (reserved bit)
Answer authenticated: Answer/authority portion was not authenticated by the server
Non-authenticated data: Unacceptable
Response code: No error (0)
Questions: 1
Answer RRs: 8
Authority RRs: 0
Additional RRs: 0

========== QUERY ==========
Name: image.google.com
Type: A (1)
Class: IN (1)

========== ANSWERS ==========
Name: image.google.com
Type: CNAME (5)
Class: IN (1)
Time to live: 300 seconds
Data length: 9 bytes
CNAME: images.google.com

Name: images.google.com
Type: CNAME (5)
Class: IN (1)
Time to live: 300 seconds
Data length: 11 bytes
CNAME: images.l.google.com

Name: images.l.google.com
Type: A (1)
Class: IN (1)
Time to live: 300 seconds
Data length: 4 bytes
Address: 172.217.215.102

Name: images.l.google.com
Type: A (1)
Class: IN (1)
Time to live: 300 seconds
Data length: 4 bytes
Address: 172.217.215.139

Name: images.l.google.com
Type: A (1)
Class: IN (1)
Time to live: 300 seconds
Data length: 4 bytes
Address: 172.217.215.138

Name: images.l.google.com
Type: A (1)
Class: IN (1)
Time to live: 300 seconds
Data length: 4 bytes
Address: 172.217.215.113

Name: images.l.google.com
Type: A (1)
Class: IN (1)
Time to live: 300 seconds
Data length: 4 bytes
Address: 172.217.215.101

Name: images.l.google.com
Type: A (1)
Class: IN (1)
Time to live: 300 seconds
Data length: 4 bytes
Address: 172.217.215.100
```
