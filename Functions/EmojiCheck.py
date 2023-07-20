import emoji

def isUnicodeEmoji(character):
    return character in emoji.unicode_codes.data_dict.EMOJI_DATA