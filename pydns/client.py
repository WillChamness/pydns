import socket
from pydns.dns_message import header, query, response
from pydns.dns_message.dns_data import DnsType, DnsClass
from pydns.helpers import UShort, DnsConstants

def run(name_to_query: str, dns_server: str) -> None:
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(2)

    dns_query: bytes = query.create_query(name_to_query, DnsType.A, DnsClass.IN)
    dns_header: bytes 
    transaction_id: UShort
    dns_header, transaction_id = header.create_request_header(len(dns_query), standard_query=True)

    client.sendto(dns_header + dns_query, (dns_server, DnsConstants.PORT))

    response_transaction_id: UShort = UShort(0)
    parsed_header: str = ""
    parsed_query: str = ""
    answers: list[list[str]] = []
    try:
        while transaction_id != response_transaction_id:
            data, _ = client.recvfrom(DnsConstants.MAX_MESSAGE_LENGTH_BYTES)

            response_header: bytes = data[:DnsConstants.HEADER_LENGTH_BYTES]
            response_transaction_id, parsed_header = header.parse_response_header(response_header)

            parsed_query, response_start_index = query.parse_query(data)

            answers = response.parse_response(data, response_start_index)

    except socket.timeout:
        print(f"No response from {dns_server}")
        return

    print(f"Response from {dns_server}:")
    print("="*10, "HEADER", "="*10)
    print(parsed_header)
    print("="*10, "QUERY", "="*10)
    print(parsed_query)
    print("="*10, "ANSWERS", "="*10)
    for answer in answers:
        print("\n".join(answer) + "\n")
    
    
