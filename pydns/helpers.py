class UShort:
    def __init__(self, val: int) -> None:
        if val < 0 or 65535 < val:
            raise ValueError("UShort must be a non-negative integer less than 65536")

        self.val = val

    def __eq__(self, other) -> bool:
        if not isinstance(other, UShort):
            return False
        else:
            return self.val == other.val

    def __str__(self) -> str:
        return str(self.val)


class DnsConstants:
    PORT = 53
    MAX_MESSAGE_LENGTH_BYTES = 512
    HEADER_LENGTH_BYTES = 12


def is_ipv4(ip: str) -> bool:
    octets: list[str] = ip.split(".")
    if len(octets) != 4:
        return False

    for octet in octets:
        try:
            byte: int = int(octet)
            if byte < 0 or 255 < byte:
                return False
        except ValueError:
            return False
    
    return True


