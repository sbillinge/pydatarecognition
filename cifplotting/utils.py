import scipy
import numpy as np
from scipy.interpolate import interp1d


def data_sampler(data):

    # Unpacking data and minimum and maximum q-values.
    tt = data[0]
    q = data[1]
    int_exp = data[2]
    int_scaled = data[3]
    q_min_round_up = data[4][0]
    q_max_round_down = data[4][1]
    # Interpolation of data using cubic kind.
    int_intpol = interp1d(np.array(q), np.array(int_exp), kind='cubic')

    # Step size for the new q-grid.
    q_step_grid = 0.005

    # Making new q-grid.
    q_grid = np.arange(q_min_round_up, q_max_round_down, q_step_grid)

    # Getting the intensity values corresponding to the new q-grid.
    int_grid = int_intpol(q_grid)

    # Appending new q and intensity values to be returned.
    new_data_grid = []
    new_data_grid.append(q_grid)
    new_data_grid.append(int_grid)

    return new_data_grid
    # End of function.

def pearson_correlator(new_user_grid, new_data_grid):

    # Unpacking user data on new grid.
    q_user = new_user_grid[0]
    int_user = new_user_grid[1]

    # Unpacking cif data on new grid.
    q_data = new_data_grid[0]
    int_data = new_data_grid[1]

    # Getting the minimum and maximum q-values.
    min_q = max(np.amin(q_user), np.amin(q_data))
    max_q = min(np.amax(q_user), np.amax(q_data))

    # Getting the indices for the minimum and maximum q-values
    # for the user and cif data.
    for i in range(0, len(q_user)):
        if q_user[i] <= min_q:
            min_q_user_index = i

        elif q_user[i] <= max_q:
            max_q_user_index = i + 1

    for i in range(0, len(q_data)):
        if q_data[i] <= min_q:
            min_q_data_index = i

        elif q_data[i] <= max_q:
            max_q_data_index = i + 1

    # Estimating the Pearson correlation coefficient and the p-value.
    pearson = scipy.stats.pearsonr(np.array(int_user)[min_q_user_index:max_q_user_index],
                                   np.array(int_data)[min_q_data_index:max_q_data_index]
                                   )

    # Pearson coefficient and p-value.
    r_pearson = pearson[0]
    p_pearson = pearson[1]

    return r_pearson
    # End of function.
