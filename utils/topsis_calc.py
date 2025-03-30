import numpy as np
import pandas as pd

def validate_weights_impacts(weights, impacts, num_columns):
    try:
        weights_list = list(map(float, weights.split(',')))
    except ValueError:
        return False

    impacts_list = impacts.split(',')

    if len(weights_list) != num_columns - 1 or len(impacts_list) != num_columns - 1:
        return False

    if not all(impact in ['+', '-'] for impact in impacts_list):
        return False

    return True


def calculate_custom_score(data, weights_str, impacts_str):
    weights = list(map(float, weights_str.split(',')))
    impacts = impacts_str.split(',')

    # Step 1: Normalize the data (excluding first column)
    normalized_data = data.iloc[:, 1:].apply(lambda x: x / np.sqrt(np.sum(x**2)), axis=0)

    # Step 2: Apply weights
    weighted_data = normalized_data * weights

    # Step 3: Identify ideal best and worst
    ideal_best = []
    ideal_worst = []
    for i, impact in enumerate(impacts):
        if impact == '+':
            ideal_best.append(weighted_data.iloc[:, i].max())
            ideal_worst.append(weighted_data.iloc[:, i].min())
        else:
            ideal_best.append(weighted_data.iloc[:, i].min())
            ideal_worst.append(weighted_data.iloc[:, i].max())

    # Step 4: Calculate TOPSIS score
    score = np.sqrt(np.sum((weighted_data - ideal_worst)**2, axis=1)) / (
            np.sqrt(np.sum((weighted_data - ideal_worst)**2, axis=1)) +
            np.sqrt(np.sum((weighted_data - ideal_best)**2, axis=1))
    )

    return score
