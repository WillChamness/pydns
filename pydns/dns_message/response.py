from pydns.dns_message.dns_data import DnsClass, DnsType

def parse_response(data: bytes, start_index: int) -> list[list[str]]:
    name: str
    dns_type: DnsType
    dns_class: DnsClass
    ttl: int
    data_length: int
    answer: bytes
    next_answer: int

    POINTER_TO_NAME_FLAG = 0xC0
    if start_index >= len(data) or data[start_index] == 0:
        return []
    elif data[start_index] == POINTER_TO_NAME_FLAG:
        pointer_to_name: int = data[start_index + 1]
        name, _ = _get_name(data, pointer_to_name)
        dns_type = DnsType(
            int.from_bytes(data[start_index + 2 : start_index + 4], "big", signed=False)
        )
        dns_class = DnsClass(
            int.from_bytes(data[start_index + 4 : start_index + 6], "big", signed=False)
        )
        ttl = int.from_bytes(
            data[start_index + 6 : start_index + 10], "big", signed=False
        )
        data_length = int.from_bytes(
            data[start_index + 10 : start_index + 12], "big", signed=False
        )
        answer = data[start_index + 12 : start_index + 12 + data_length]
        next_answer = start_index + 12 + data_length
    else:
        name, pointer_to_dns_type = _get_name(data, start_index)
        dns_type = DnsType(
            int.from_bytes(
                data[pointer_to_dns_type : pointer_to_dns_type + 2], "big", signed=False
            )
        )
        dns_class = DnsClass(
            int.from_bytes(
                data[pointer_to_dns_type + 2 : pointer_to_dns_type + 4],
                "big",
                signed=False,
            )
        )
        ttl = int.from_bytes(
            data[pointer_to_dns_type + 4 : pointer_to_dns_type + 8], "big", signed=False
        )
        data_length = int.from_bytes(
            data[pointer_to_dns_type + 8 : pointer_to_dns_type + 10],
            "big",
            signed=False,
        )
        answer = data[pointer_to_dns_type + 10 : pointer_to_dns_type + 10 + data_length]
        next_answer = start_index + 10 + data_length

    parsed_answer: str
    if dns_type == DnsType.A:
        assert len(answer) == 4
        octet1: int = answer[0]
        octet2: int = answer[1]
        octet3: int = answer[2]
        octet4: int = answer[3]
        parsed_answer = f"{octet1}.{octet2}.{octet3}.{octet4}"
    elif dns_type == DnsType.CNAME:
        parsed_answer, _ = _get_name(answer, 0)
    else:
        parsed_answer = "Unsupported DNS type"

    result: list[str] = [
        f"Name: {name}",
        f"Type: {str(dns_type)[len('DnsType.'):]} ({dns_type.value})",
        f"Class: {str(dns_class)[len('DnsClass.'):]} ({dns_class.value})",
        f"Time to live: {ttl} seconds",
        f"Data length: {data_length} bytes",
        ("Address: " if dns_type == DnsType.A else "CNAME: ") + parsed_answer,
    ]

    return [result, *parse_response(data, next_answer)]


def _get_name(data: bytes, start_index: int) -> tuple[str, int]:
    stop_index: int = start_index
    while data[stop_index] != 0:
        stop_index += 1

    subdomains: list[str] = []
    index: int = start_index

    while index < stop_index:
        subdomain_size: int = data[index]
        subdomains.append(data[index + 1 : index + 1 + subdomain_size].decode("ascii"))
        index += 1 + subdomain_size

    name: str = ".".join(subdomains)
    return (name, stop_index + 1)

