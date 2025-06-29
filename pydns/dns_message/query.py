from pydns.dns_message.dns_data import DnsClass, DnsType
from pydns.helpers import DnsConstants


def create_query(name_to_query: str, dns_type: DnsType, dns_class: DnsClass) -> bytes:
    subdomains: list[str] = name_to_query.split(".")
    query: bytes = b""
    for subdomain in subdomains:
        query += len(subdomain).to_bytes(1, "big") + subdomain.encode("ascii")

    null_byte = int(0).to_bytes(1, "big")

    return (
        query
        + null_byte
        + dns_type.value.to_bytes(2, "big")
        + dns_class.value.to_bytes(2, "big")
    )


def parse_query(data: bytes) -> tuple[str, int]:
    stop_index: int = DnsConstants.HEADER_LENGTH_BYTES
    while data[stop_index] != 0:
        stop_index += 1

    subdomains: list[str] = []
    index: int = DnsConstants.HEADER_LENGTH_BYTES
    while index < stop_index:
        subdomain_size: int = data[index]
        subdomains.append(data[index + 1 : index + 1 + subdomain_size].decode("ascii"))
        index += 1 + subdomain_size

    query_name: str = ".".join(subdomains)

    dns_type: DnsType = DnsType(
        int.from_bytes(data[stop_index + 1 : stop_index + 3], "big", signed=False)
    )
    dns_class: DnsClass = DnsClass(
        int.from_bytes(data[stop_index + 3 : stop_index + 5], "big", signed=False)
    )

    result: str = (
        f"Name: {query_name}" + "\n"
        + f"Type: {str(dns_type)[len('DnsType.'):]} ({dns_type.value})" + "\n"
        + f"Class: {str(dns_class)[len('DnsClass.'):]} ({dns_class.value})" + "\n"
    )

    return (result, stop_index + 5)
