def create_percentage_bar(choices: dict, bar_length=10):
    total = sum(choices.values())
    bars = {}
    percentages = {}
    
    if total == 0:
        for choice in choices:
            bars[choice] = '░' * bar_length
            percentages[choice] = '[0 • 0%]'
    else:
        for choice, count in choices.items():
            choice_percentage = count / total
            filled_length = int(bar_length * choice_percentage)
            empty_length = bar_length - filled_length
            bars[choice] = '█' * filled_length + '░' * empty_length
            percentages[choice] = f'[{count} • {choice_percentage:.0%}]'

    result = ''
    for choice in choices.keys():
        result += f'{choice} {bars[choice]} {percentages[choice]}\n'

    return result

# Example usage
# choices = {
#     '👍': 2,
#     '👎': 0,
#     '🤷': 1
# }
# percentage_bar = create_percentage_bar(choices)

# print(percentage_bar)
