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
                        the DNS server to be queried (default: use the first nameserver in /etc/resolv.conf)
  -v, --verbose         be as verbose as possible
```


