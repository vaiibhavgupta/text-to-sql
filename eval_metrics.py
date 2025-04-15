def get_error_distribution(output_list):
    error_type = {
        'syntax': 0,
        'column': 0,
        'table': 0,
        'misc': 0,
    }

    for output in output_list:
        if output[1] != -1:
            continue
        elif 'syntax' in output[0]:
            error_type['syntax'] += 1
        elif 'no such column' in output[0]:
            error_type['column'] += 1
        elif 'no such table' in output[0]:
            error_type['table'] += 1
        else:
            print(output)
            error_type['misc'] += 1
    return error_type

def get_output_accuracy(predicted_output, gold_output):
    assert len(predicted_output) == len(gold_output)

    correct_output = 0
    for pred, true in zip(predicted_output, gold_output):
        if pred[0] == true[0] and pred[1] != -1:
            correct_output += 1
    return str(round(100 * correct_output / len(predicted_output), 2)) + "% Accuracy"