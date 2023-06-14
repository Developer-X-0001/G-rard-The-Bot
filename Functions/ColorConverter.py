def hex_to_int(hex_code):
    return int(hex_code, 16)

def int_to_hex(int_val: str):
    return hex(int_val)[2:].upper().zfill(6)