import numpy as np
import scipy.stats
from scipy.interpolate import interp1d
from requests import HTTPError
from habanero import Crossref
from datetime import date


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


def xy_resample(x1, y1, x2, y2, x_step=None):
    '''
    Given arrays with x and y values for two datasets, the common x-range is found. 
    A regular x-grid is calculated for this common x-range using the provided step size.
    For each of the two y arrays, linear interpolations are done.
    The interpolations are used to resample the data sets onto the regular x-grid.

    Parameters
    ----------
    x1  array_like 
      x values for data set 1.
    y1  array_like
      y values for data set 1.
    x2  array_like 
      x values for data set 2.
    y2  array_like
      y values for data set 2.      
    x_step  integer or float (non-zero and positive, optional)
      step size for regular x-grid to be calculated.
    Returns
    -------
    xy1_reg  numpy array
      data set 1 resampled onto the regular x-grid. 
    xy2_reg  numpy array
      data set 2 resampled onto the regular x-grid. 
    '''
    if not x_step:
        x_step = 10**-3
    x1, y1, x2, y2 = np.array(x1), np.array(y1), np.array(x2), np.array(y2)
    if not x2.any():
        raise AttributeError('Reciprocal space axis (3rd argument) missing (NoneType Provided)')
    xmin, xmax = max(np.amin(x1), np.amin(x2)), min(np.amax(x1), np.amax(x2))
    nox = int(((xmax - xmin) / x_step) + 1)
    x_reg = np.linspace(xmin, xmax, nox, endpoint=True)
    xy1_interpol, xy2_interpol = interp1d(x1, y1, kind='linear'), interp1d(x2, y2, kind='linear')
    xy1_reg, xy2_reg = np.column_stack((x_reg, xy1_interpol(x_reg))), np.column_stack((x_reg, xy2_interpol(x_reg)))

    return xy1_reg, xy2_reg


def get_formatted_crossref_reference(doi):
    '''
    given a doi, return the full reference and the date of the reference from Crossref REST-API

    parameters
    ----------
    doi str
      the doi of the digital object to pull from Crossref

    return
    ------
    ref str
      the nicely formatted reference including title
    ref_date datetime.date
      the date of the reference
    returns None None in the article cannot be found given the doi

    '''

    cr = Crossref()
    try:
        article = cr.works(ids=str(doi))
    except HTTPError:
        return None, None

    authorlist = [
        "{} {}".format(a['given'].strip(), a['family'].strip())
        for a in article.get('message').get('author')]
    try:
        journal = \
            article.get('message').get('short-container-title')[0]
    except IndexError:
        journal = article.get('message').get('container-title')[
            0]
    if article.get('message').get('volume'):
        if len(authorlist) > 1:
            authorlist[-1] = "and {}".format(authorlist[-1])
        sauthorlist = ", ".join(authorlist)
        ref_date_list = article.get('message').get('issued').get('date-parts')
        ref = "{}, {}, {}, v. {}, pp. {}, ({}).".format(
            article.get('message').get('title')[0],
            sauthorlist,
            journal,
            article.get('message').get('volume'),
            article.get('message').get('page'),
            ref_date_list[0][0],
        )
    else:
        if len(authorlist) > 1:
            authorlist[-1] = "and {}".format(authorlist[-1])
        sauthorlist = ", ".join(authorlist)
        ref_date_list = article.get('message').get('issued').get('date-parts')
        ref = "{}, {}, {}, pp.{}, ({}).".format(
            article.get('message').get('title')[0],
            sauthorlist,
            journal,
            article.get('message').get('page'),
            ref_date_list[0][0],
        )
    ref_date_list = ref_date_list[0]
    ref_date_list += [6] * (3 - len(ref_date_list))
    ref_date = date(*ref_date_list)

    return ref, ref_date


def hr_to_mr_number_and_esd(number_esd):
    '''
    splits human readable numbers with estimated standard deviations (e.g. 343.44(45)) into machine readable numbers and
    estimated standard deviations (e.g. 343.44 and 0.45).

    Parameters
    ----------
    number_esd : array_like
      The array-like object that contains numbers with their estimated standard deviations as strings
      in the following format: ["343.44(45)", "324908.435(67)", "0.0783(1)"]

    Returns
    -------
    numpy array
      The array with the numbers as floats

    numpy array
      The array with estimated standard deviations as floats

    '''
    number = [e.split("(")[0] for e in number_esd]
    esd = np.array([e.split("(")[1].split(")")[0] for e in number_esd], dtype="float")
    esd_oom = []
    for i in range(len(number)):
        if len(number[i].split(".")) == 1:
            esd_oom.append(1)
        else:
            esd_oom.append(10**-len(number[i].split(".")[1]))
    esd_oom = np.array(esd_oom, dtype='float')
    number, esd = np.array(number, dtype='float'), np.array(esd * esd_oom, dtype='float')

    return number, esd


def mr_to_hr_number_and_esd(number, esd):
    '''
    merges machine readable numbers and estimated standard deviations (e.g. 343.44 and 0.45) into human readable
    numbers with estimated standard deviations (e.g. 343.44(45)).

    Parameters
    ----------
    number : array_like
      The array-like object that contains numbers in the following format: [343.44, 324908.435, 0.0783] or

    esd : array_like
      The array-like object that contains estimated standard deviations in the following format:
      [0.45, 0.067, 0.0001]

    Returns
    -------
    list
      The list of strings that contains the rounded numbers with estimated standard deviations
      in the following format: ["343.4(5)", "324908.44(7)", "0.0783(1)" ]

    '''
    #number, esd = np.array(number, dtype='float').astype('str'), np.array(esd, dtype='float').astype('str')
    number, esd = [str(e) for e in number], [str(e) for e in esd]
    number_hr, esd_hr = [], []
    for i in range(len(number)):
        if len(number[i].split(".")) == 1:
            number_hr.append(number[i])
            esd_hr.append(esd[i].split(".")[0])
        else:
            number_hr.append(number[i])
            esd_hr.append(str(int(esd[i].split(".")[1])))
    number_esd = [f'{number_hr[i]}({esd_hr[i]})' for i in range(len(esd_hr))]

    return number_esd

def round_number_esd(number, esd):
    '''
    Rounds each element in number and each element in esd (estimated standard deviation) arrays.

    Esd is rounded to one significant figure if esd > 1.44E**x.(NB: 1.45E**x will become 2E**x)
    If esd <= 1.44E**x the esd is rounded to two significant figures.
    Number is rounded to the order of the rounded esd.

    Parameters
    ----------
    number : array-like
        The array containing numbers to be rounded.
    esd : array-like
        The array containing esds to be rounded.

    Returns
    -------
    list
        The list containing rounded numbers as floats and/or integers.
    list
        The list containing rounded esds as floats and/or integers.

    '''

# End of file.
