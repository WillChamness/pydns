from enum import Enum

class DnsType(Enum):
    A = 1
    CNAME = 5
    AAAA = 28

class DnsClass(Enum):
    IN = 1
