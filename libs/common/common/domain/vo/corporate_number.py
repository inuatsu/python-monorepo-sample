from re import fullmatch
from typing import Annotated, Any

from pydantic import BeforeValidator


def validate_type_and_length(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("Type of value should be str")
    if not value.isdigit():
        raise ValueError("Value should be digit")
    if len(value) < 12 or len(value) > 13:
        raise ValueError("Length of given value should be 12 or 13")
    return value


def validate_corporate_registration_number(value: str) -> str:
    corporate_registration_number = value[-12:]
    government_institutions = "00001[123]"
    municipalities = "0000[23]0"
    registration_office_codes = [
        "0100",
        "0101",
        "0104",
        "0105",
        "0106",
        "0107",
        "0108",
        "0109",
        "0110",
        "0111",
        "0112",
        "0113",
        "0114",
        "0115",
        "0116",
        "0117",
        "0118",
        "0123",
        "0124",
        "0127",
        "0128",
        "0131",
        "0132",
        "0133",
        "0134",
        "0200",
        "0210",
        "0300",
        "0400",
        "0500",
        "0600",
        "0700",
        "0800",
        "0801",
        "0804",
        "0900",
        "1000",
        "1100",
        "1200",
        "1201",
        "1209",
        "1220",
        "1300",
        "1400",
        "1500",
        "1600",
        "1700",
        "1800",
        "1803",
        "1900",
        "2000",
        "2100",
        "2200",
        "2300",
        "2400",
        "2500",
        "2600",
        "2700",
        "2800",
        "2900",
        "2908",
        "3000",
        "3100",
        "3200",
        "3202",
        "3300",
        "3400",
        "3500",
        "3600",
        "3700",
        "3701",
        "3702",
        "3703",
        "3704",
        "3705",
        "3706",
        "3708",
        "3800",
        "3900",
        "4000",
        "4005",
        "4006",
        "4027",
        "4100",
        "4200",
        "4300",
        "4400",
        "4500",
        "4600",
        "4601",
        "4603",
        "4604",
        "4625",
        "4700",
        "4800",
        "4900",
        "5000",
    ]
    corporate_type_codes = ["01", "02", "03", "04", "05"]
    corporations_with_establishment_registration = (
        rf"({'|'.join(registration_office_codes)})({'|'.join(corporate_type_codes)})"
    )
    corporations_without_establishment_registration = r"7\d{5}"
    match = fullmatch(
        rf"({government_institutions}|{municipalities}|{corporations_with_establishment_registration}|{corporations_without_establishment_registration})\d{{6}}",
        corporate_registration_number,
    )
    if match:
        return value
    else:
        raise ValueError("Given value is not valid corporate number")


def validate_check_digit(value: str) -> str:
    corporate_registration_number = value[-12:]
    even_digit_sum = (
        int(corporate_registration_number[0])
        + int(corporate_registration_number[2])
        + int(corporate_registration_number[4])
        + int(corporate_registration_number[6])
        + int(corporate_registration_number[8])
        + int(corporate_registration_number[10])
    )
    odd_digit_sum = (
        int(corporate_registration_number[1])
        + int(corporate_registration_number[3])
        + int(corporate_registration_number[5])
        + int(corporate_registration_number[7])
        + int(corporate_registration_number[9])
        + int(corporate_registration_number[11])
    )
    check_digit = 9 - (even_digit_sum * 2 + odd_digit_sum) % 9
    corporate_number = f"{check_digit}{corporate_registration_number}"
    if len(value) == 13:
        assert corporate_number == value, "Check digit is invalid"
    return corporate_number


CorporateNumber = Annotated[
    str,
    BeforeValidator(validate_check_digit),
    BeforeValidator(validate_corporate_registration_number),
    BeforeValidator(validate_type_and_length),
]
