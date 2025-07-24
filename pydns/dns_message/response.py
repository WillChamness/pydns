from pydns.dns_message.dns_data import DnsClass, DnsType


def parse_response(
    data: bytes, start_index: int, current_count: int = 0
) -> list[list[str]]:
    number_of_answers: int = int.from_bytes(data[6:10], "big", signed=False)
    if start_index >= len(data) or current_count >= number_of_answers:
        return []

    POINTER_TO_NAME_INDICATOR = 0xC0
    name: str
    pointer_to_type: int
    name, pointer_to_type = (
        _get_name_from_pointer(data, start_index)
        if data[start_index] == POINTER_TO_NAME_INDICATOR
        else _parse_name(data, start_index)
    )
    dns_type: DnsType = DnsType(
        int.from_bytes(data[pointer_to_type : pointer_to_type + 2], "big", signed=False)
    )
    dns_class: DnsClass = DnsClass(
        int.from_bytes(
            data[pointer_to_type + 2 : pointer_to_type + 4], "big", signed=False
        )
    )
    ttl: int = int.from_bytes(
        data[pointer_to_type + 4 : pointer_to_type + 8], "big", signed=False
    )
    data_length: int = int.from_bytes(
        data[pointer_to_type + 8 : pointer_to_type + 10], "big", signed=False
    )
    answer: str
    pointer_to_next_answer: int
    if dns_type == DnsType.A:
        answer, pointer_to_next_answer = _get_ipv4(data, pointer_to_type + 10)
    elif dns_type == DnsType.CNAME:
        if data[pointer_to_type + 10 + (data_length - 1)] == 0:
            answer, pointer_to_next_answer = _parse_name(data, pointer_to_type + 10)
        else:
            answer, pointer_to_next_answer = _get_name_from_pointer(
                data, pointer_to_type + 10
            )
    elif dns_type == DnsType.SOA:
        answer, pointer_to_next_answer = _get_name_from_pointer(data, pointer_to_type + 10)
    else:
        answer, pointer_to_next_answer = "Unsupported DNS type", len(data)

    result = [
        f"Name: {name}",
        f"Type: {str(dns_type)[len('DnsType.'):]} ({dns_type.value})",
        f"Class: {str(dns_class)[len('DnsClass.'):]} ({dns_class.value})",
        f"Time to live: {ttl} seconds",
        f"Data length: {data_length} bytes",
    ]
    if dns_type == DnsType.A:
        result.append("Address: " + answer)
    elif dns_type == DnsType.CNAME:
        result.append("CNAME: " + answer)
    else:
        result.append("Response: " + answer)

    return [result, *parse_response(data, pointer_to_next_answer, current_count + 1)]


def _get_name_from_pointer(data: bytes, start_index: int) -> tuple[str, int]:
    def go(data: bytes, current_index: int) -> tuple[str, int]:
        POINTER_TO_NAME_INDICATOR = 0xC0
        if data[current_index] == 0:
            return ("", 0)
        elif data[current_index] == POINTER_TO_NAME_INDICATOR:
            pointer_to_name: int = data[current_index + 1]
            name, _ = go(data, pointer_to_name)
            return (name, 2)
        else:
            subdomain_length: int = data[current_index]
            subdomain: str = data[
                current_index + 1 : current_index + 1 + subdomain_length
            ].decode("ascii")
            name, offset = go(data, current_index + 1 + subdomain_length)
            return (subdomain + "." + name, 1 + subdomain_length + offset)

    name, offset = go(data, start_index)
    return (name[: len(name) - 1], start_index + offset)


def _get_ipv4(data: bytes, start_index: int) -> tuple[str, int]:
    octet1: int = data[start_index]
    octet2: int = data[start_index + 1]
    octet3: int = data[start_index + 2]
    octet4: int = data[start_index + 3]

    return (f"{octet1}.{octet2}.{octet3}.{octet4}", start_index + 4)


def _parse_name(data: bytes, start_index: int) -> tuple[str, int]:
    stop_index: int = start_index
    while data[stop_index] != 0:
        stop_index += 1

    index: int = start_index
    subdomains: list[str] = []
    while index < stop_index:
        subdomain_length: int = data[index]
        subdomain: str = data[index + 1 : index + 1 + subdomain_length].decode("ascii")
        subdomains.append(subdomain)
        index += 1 + subdomain_length

    return (".".join(subdomains), stop_index + 1)
