def hex_to_int(hex_code):
    return int(hex_code, 16)

def int_to_hex(int_val: str):
    return hex(int_val)[2:].upper().zfill(6)

def isValidHexCode(input_str: str):
    if input_str.startswith('#'):
        input_str = input_str[1:]

    try:
        int(input_str, 16)
        return len(input_str) == 6
    except ValueError:
        return False