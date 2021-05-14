import numpy as np
from CifFile import StarError

from diffpy.structure.parsers.p_cif import P_cif, _fixIfWindowsPath
from diffpy.utils.parsers.loaddata import loadData
import CifFile

def cif_read(cif_file_path):
    '''
    given a cif file-path, reads the cif and returns the cif data
    
    Parameters
    ----------
    cif_file_path  pathlib.Path object
      the path to a valid cif file

    Returns
    -------
    the cif data as a CifFile object
    '''
    cf = CifFile.ReadCif(_fixIfWindowsPath(str(cif_file_path)))

    return cf


def powdercif_pattern_write(output_file_path, x_array, y_array):
    '''
    given an output file path, x- and y-arrays, a two-column .txt file with x- and y-values is written.

    Parameters
    ----------
    output_file_path pathlib.Path object
      the path for the output file
    x_array numpy array
      numpy array containing x values
    y_array numpy array
      numpy array containing y values

    Returns
    -------
    None
    '''
    xy_array = np.column_stack((x_array, y_array))
    np.savetxt(output_file_path, xy_array, delimiter='\t', newline='\n', encoding='utf8')

    return None


def user_input_read(user_input_file_path):
    '''
    given a user input file path, reads the user data into ndarrays.

    Parameters
    ----------
    user_input_file_path pathlib.Path object
      the path to a user input file containing diffraction data

    Returns
    -------
    user_data  ndarray object
      ndarray with the columns of the user input input file. Dimensions will depend on the number of columns.
    '''
    user_data = loadData(user_input_file_path)

    return user_data


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


def rank_write(cif_rank_list, output_path):
    '''
    given a list of ranked cif files and a path to the output directory, writes a .txt file with ranked file names

    Parameters
    ----------
    cif_rank_list  list object
      a list of ranked cif files ranked according to their pearson coefficient
    output_path  pathlib.Path object
      path to output directory of the .txt file that will be written as rank.txt

    Returns
    -------
    None
    '''
    txt = []
    print('-'*80)
    print('Rank\tFile\t\t\t\t\t\t\t\t\t\tPearson coefficient')
    txt.append('Rank\tFile\t\t\t\t\t\t\t\t\t\tPearson coefficient\n')
    for i in range(0, 10):
        # print(len(str(cif_rank_pearson_list[i][0])))
        if len(cif_rank_list[i][0]) < 36:
            print(str(i + 1) + '\t\t' + str(cif_rank_list[i][0]) + '\t\t\t'
                  + "{:.4f}".format(cif_rank_list[i][1]))
            txt.append(str(i + 1) + '\t\t' + str(cif_rank_list[i][0]) + '\t\t\t'
                       + "{:.4f}".format(cif_rank_list[i][1]) + '\n')
        if 36 <= len(cif_rank_list[i][0]) < 40:
            print(str(i + 1) + '\t\t' + str(cif_rank_list[i][0]) + '\t\t'
                  + "{:.4f}".format(cif_rank_list[i][1]))
            txt.append(str(i + 1) + '\t\t' + str(cif_rank_list[i][0]) + '\t\t'
                       + "{:.4f}".format(cif_rank_list[i][1]) + '\n')
        elif len(cif_rank_list[i][0]) >= 40:
            print(str(i + 1) + '\t\t' + str(cif_rank_list[i][0]) + '\t'
                  + "{:.4f}".format(cif_rank_list[i][1]))
            txt.append(str(i + 1) + '\t\t' + str(cif_rank_list[i][0]) + '\t'
                       + "{:.4f}".format(cif_rank_list[i][1]) + '\n')
    print('-'*80)

    with open(output_path / 'rank.txt', 'w') as output_file:
        output_file.writelines(txt)

    return None

