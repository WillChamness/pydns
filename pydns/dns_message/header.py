import random
from enum import Enum
from typing import Literal

from pydns.helpers import DnsConstants, UShort


class Opcode(Enum):
    StandardQuery = 0
    InverseQuery = 1
    StatusRequest = 2
    _Reserved = 3


class ResponseCode(Enum):
    NoError = 0
    QueryFormatError = 1
    ServerFailure = 2
    NameDoesNotExist = 3
    RequestTypeNotImplemented = 4
    QueryRefused = 5


def create_header(
    *,
    transaction_id: UShort,
    is_response: bool,
    op: Opcode,
    authoritative_answer: bool,
    truncated: bool,
    recursion_desired: bool,
    recursion_available: bool,
    rcode: ResponseCode,
    question_count: UShort,
    response_count: UShort,
    authority_responses_count: UShort,
    additional_responses_count: UShort,
) -> bytes:
    # reserved bits
    zero: Literal[False] = False
    nonauthenticated_data_acceptable: Literal[False] = False
    authenticated: Literal[False] = False

    opcodes: list[list[bool]] = [
        [False, False, False, False],
        [False, False, False, True],
        [False, False, True, False],
    ]
    response_codes: list[list[bool]] = [
        [False, False, False, False],
        [False, False, False, True],
        [False, False, True, False],
        [False, False, True, True],
        [False, True, False, False],
        [False, True, False, True],
    ]

    flags: list[bool] = [
        is_response,
        *opcodes[op.value],
        authoritative_answer,
        truncated,
        recursion_desired,
        recursion_available,
        zero,
        authenticated,
        nonauthenticated_data_acceptable,
        *response_codes[rcode.value],
    ]

    tid_value: bytes = transaction_id.val.to_bytes(2, "big")
    flags_value: bytes = sum(
        (1 if bit else 0) * 2**index for index, bit in enumerate(reversed(flags))
    ).to_bytes(2, "big")
    question_count_value: bytes = question_count.val.to_bytes(2, "big")
    response_count_value: bytes = response_count.val.to_bytes(2, "big")
    authority_responses_count_value: bytes = authority_responses_count.val.to_bytes(
        2, "big"
    )
    additional_responses_count_value: bytes = additional_responses_count.val.to_bytes(
        2, "big"
    )

    result: bytes = (
        tid_value
        + flags_value
        + question_count_value
        + response_count_value
        + authority_responses_count_value
        + additional_responses_count_value
    )
    assert len(result) == DnsConstants.HEADER_LENGTH_BYTES
    return result


def create_request_header(payload_size_bytes: int, standard_query: bool) -> tuple[bytes, UShort]:
    tid = UShort(random.randint(1, 65535))
    return (
        create_header(
            transaction_id=tid,
            is_response=False,
            op=Opcode(0 if standard_query else 1),
            authoritative_answer=False,
            truncated=payload_size_bytes
            > DnsConstants.MAX_MESSAGE_LENGTH_BYTES - DnsConstants.HEADER_LENGTH_BYTES,
            recursion_desired=True,
            recursion_available=False,
            rcode=ResponseCode(0),
            question_count=UShort(1),
            response_count=UShort(0),
            authority_responses_count=UShort(0),
            additional_responses_count=UShort(0),
        ),
        tid,
    )


def parse_response_header(header: bytes) -> tuple[UShort, str]:
    if len(header) != DnsConstants.HEADER_LENGTH_BYTES:
        raise ValueError(f"Header is not {DnsConstants.HEADER_LENGTH_BYTES} bytes long")

    transaction_id: UShort = UShort(int.from_bytes(header[0:2], "big", signed=False))
    flags: UShort = UShort(int.from_bytes(header[2:4], "big", signed=False))
    questions: UShort = UShort(int.from_bytes(header[4:6], "big", signed=False))
    responses: UShort = UShort(int.from_bytes(header[6:8], "big", signed=False))
    authority_responses: UShort = UShort(
        int.from_bytes(header[8:10], "big", signed=False)
    )
    additional_responses: UShort = UShort(
        int.from_bytes(header[10:12], "big", signed=False)
    )

    flags_val: int = flags.val
    flag_bits: list[bool] = []

    while flags_val != 0:
        flag_bits.append(flags_val % 2 == 1)
        flags_val //= 2
    flag_bits.reverse()
    assert len(flag_bits) == 16

    response: str = (
        "Response: Message is a response"
        if flag_bits[0]
        else "Response: Message is a query"
    )
    opcode: str = [
        "Opcode: Standard query (0)",
        "Opcode: Inverse query (1)",
        "Opcode: Status request (2)",
    ][
        sum(
            (1 if bit else 0) * 2**index
            for index, bit in enumerate(reversed(flag_bits[1:5]))
        )
    ]
    authoritative_server: str = (
        "Authoritative: Server is an authority for domain"
        if flag_bits[5]
        else "Authoritative: Server is not an authority for domain"
    )
    truncated: str = (
        "Truncated: Message is truncated"
        if flag_bits[6]
        else "Truncated: Message is not truncated"
    )
    recursion_desired: str = (
        "Recursion desired: Do query recursively"
        if flag_bits[7]
        else "Recursion desired: Do not query recursively"
    )
    recursion_available: str = (
        "Recursion available: Server can do recursive queries"
        if flag_bits[8]
        else "Recursion available: Server cannot do recursive queries"
    )
    zero: str = "Zero: one (reserved bit)" if flag_bits[9] else "Zero: zero (reserved bit)"
    answer_authenticated: str = (
        "Answer authenticated: Answer/authority portion was authenticated by the server"
        if flag_bits[10]
        else "Answer authenticated: Answer/authority portion was not authenticated by the server"
    )
    non_authenticated_data: str = (
        "Non-authenticated data: Acceptable"
        if flag_bits[11]
        else "Non-authenticated data: Unacceptable"
    )
    response_code: str = [
        "Response code: No error (0)",
        "Response code: The query was formatted incorrectly (1)",
        "Response code: The server encountered an unknown error (2)",
        "Response code: The queried name does not exist (3)",
        "Response code: The request type is not supported by the server (4)",
        "Response code: The server declined to process the query (5)",
    ][
        sum(
            (1 if bit else 0) * 2**index
            for index, bit in enumerate(reversed(flag_bits[12:]))
        )
    ]

    result: str = "\n".join([
        response,
        opcode,
        authoritative_server,
        truncated,
        recursion_desired,
        recursion_available,
        zero,
        answer_authenticated,
        non_authenticated_data,
        response_code,
        f"Questions: {questions.val}",
        f"Answer RRs: {responses.val}",
        f"Authority RRs: {authority_responses.val}",
        f"Additional RRs: {additional_responses.val}",
    ]) + "\n"

    return (transaction_id, result)
