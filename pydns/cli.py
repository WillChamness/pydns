import argparse
import re
from pydns import client
from pydns.helpers import is_ipv4 

def parse_args() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument("query", type=str, metavar="NAME", help="the name to query")
    parser.add_argument("-d", "--dns-server", type=str, required=False, metavar="IPADDR", help="the DNS server to be queried (default: use the first nameserver in /etc/resolv.conf)")
    parser.add_argument("-v", "--verbose", action="store_true", help="be as verbose as possible")

    args = parser.parse_args()
    
    nameserver: str|None = args.dns_server
    if nameserver is None:
        default_nameserver: str|None = _get_default_nameserver()
        if default_nameserver is None:
            print("Cannot find a valid nameserver in `/etc/resolv.conf`")
            exit(1)
        else:
            nameserver = default_nameserver

    client.run(args.query, nameserver, args.verbose)


def _get_default_nameserver() -> str|None:
    nameservers: list[str] = []
    with open("/etc/resolv.conf", "r") as f:
        nameserver_pattern: re.Pattern = re.compile("^nameserver")
        nameservers = [line for line in f if re.match(nameserver_pattern, line)]

    if len(nameservers) == 0:
        return None

    default_nameserver: list[str] = nameservers[0].split()

    if len(default_nameserver) < 2:
        return None

    if not is_ipv4(default_nameserver[1]):
        return None
    else:
        return default_nameserver[1]



if __name__ == "__main__":
    parse_args()
