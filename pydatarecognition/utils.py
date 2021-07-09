import numpy as np
import scipy.stats
from scipy.interpolate import interp1d

def user_diffraction_data_extract(user_input_lines):
    '''
    given user_input_lines, extract twotheta values and intensity values to individual lists as floats
    Parameters
    ----------
    user_input_lines  list object
      the list containing the lines of the user input file
    Returns
    -------
    twotheta and intensity lists in a tuple
    '''
    twotheta_list, intensity_list = [], []
    for line in user_input_lines:
        twotheta_list.append(float(line.split()[0]))
        intensity_list.append(float(line.split()[1]))
    twotheta_array = np.array(twotheta_list)
    intensity_array = np.array(intensity_list)

    return twotheta_array, intensity_array


def q_calculate(twotheta_list, wavelength):
    '''
    given a list of twotheta values and wavelength, calculates and appends corresponding q values to a list
    Parameters
    ----------
    twotheta_list  list object
      the list containing the twotheta values as floats
    wavelength type string or float
      wavelength in angstroms
    Returns
    -------
    a list of q values as floats
    '''
    wavelength = float(wavelength)
    q_list = []
    for i in range(0, len(twotheta_list)):
        q_list.append(float(4 * np.pi * np.sin((np.pi / 180) * float(twotheta_list[i]) / 2) / wavelength))

    return q_list


def q_extrema_round(q_list):
    '''
    given a list of q values, gets the minimum and maximum q values
    and rounds them up and down to two significant digits, respectively
    Parameters
    ----------
    q_list  list object
      the list of q values as floats
    Returns
    -------
    the minimum q value rounded up to two significant digits as float
    the maximum q value rounded down to two significant digits as float
    '''
    q_min_round_up = float(np.ceil(min(q_list) * 10**2) / 10**2)
    q_max_round_down = float(np.floor(max(q_list) * 10**2) / 10**2)

    return q_min_round_up, q_max_round_down


def data_sample(cif_data):
    tt = cif_data[0]
    q = cif_data[1]
    int_exp = cif_data[2]
    int_scaled = cif_data[3]
    q_min_round_up = cif_data[4][0]
    q_max_round_down = cif_data[4][1]
    int_intpol = interp1d(np.array(q), np.array(int_exp), kind='cubic')
    q_step_grid = 0.005
    q_grid = np.arange(q_min_round_up, q_max_round_down, q_step_grid)
    int_grid = int_intpol(q_grid)
    new_data_grid = [q_grid, int_grid]

    return new_data_grid


def pearson_correlate(new_user_grid, new_data_grid):
    q_user = new_user_grid[0]
    int_user = new_user_grid[1]
    q_data = new_data_grid[0]
    int_data = new_data_grid[1]
    min_q = max(np.amin(q_user), np.amin(q_data))
    max_q = min(np.amax(q_user), np.amax(q_data))
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
    pearson = scipy.stats.pearsonr(np.array(int_user)[min_q_user_index:max_q_user_index],
                                   np.array(int_data)[min_q_data_index:max_q_data_index])
    r_pearson = pearson[0]
    p_pearson = pearson[1]

    return r_pearson


def q_reg_grid(q_user, q_cif, q_step)
    '''
    Given arrays with q-values for user data and cif data, the overlap in q-space is found, 
    and a regular q-grid is calculated for this common q-range using the provided step size.
    Parameters
    ----------
    q_user  array_like 
      q values for user data.
    q_cif  array_like
      q values for cif data.
    q_step  integer or float (non-zero and positive)
      step size for regular q-grid to be calculated.
    Returns
    -------
    q_reg  numpy array
      regular q-grid for the common q-range for user and cif data with the provided step size.
    '''


    return q_reg

# End of file.
