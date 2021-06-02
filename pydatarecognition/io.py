import numpy as np

from diffpy.structure.parsers.p_cif import _fixIfWindowsPath
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


def _xy_write(output_file_path, x_vals, y_vals):
    '''
    given an output file path, x- and y-arrays, a two-column text file with x- and y-values is written.

    Parameters
    ----------
    output_file_path pathlib.Path object
      the path for the output file
    x_vals iterable
      iterable containing x values as floats or integers
    y_vals iterable
      iterable containing y values as floats or integers

    Returns
    -------
    None
    '''
    xy_array = np.column_stack((np.array(x_vals), np.array(y_vals)))
    np.savetxt(output_file_path, xy_array, delimiter='\t', newline='\n', encoding='utf8')

    return


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
    user_data = loadData(user_input_file_path).T

    return user_data


def rank_write(cif_ranks, output_path):
    '''
    given a list of dicts of IUCr CIFs, scores, and DOIs together with a path to the output dir,
    writes a .txt file with ranks, scores, IUCr CIFs, and DOIs.

    Parameters
    ----------
    cif_ranks  list object
      a list of dicts of IUCr CIF names, scores, and DOIs, ranked according to their score
    output_path  pathlib.Path object
      path to output directory of the .txt file that will be written as rank.txt

    -------
    rank_doi_score_txt string object
      a string containing ranks, scores, IUCr CIFs, and DOIs that are written to a txt file.
      the string is returned, so that it can e.g. be printed to the terminal.
    '''
    strlen = [len(cif_ranks[i]['IUCrCIF']) for i in range(len(cif_ranks))]
    strlen_max = max(strlen)
    char_max = strlen_max - (strlen_max % 8) + 8
    tabs = [int(((char_max - (strlen[i] - (strlen[i] % 8) + 8)) / 8) + 1) for i in range(len(strlen))]
    tab_char = '\t'
    rank_doi_score_txt = f"Rank\tScore\tIUCr CIF{tab_char * (int(char_max / 8) - 1)}DOI\n"
    for i in range(0, 10):
        rank_doi_score_txt += f"{i + 1}\t{cif_ranks[i]['score']:.4f}\t{cif_ranks[i]['IUCrCIF']}{tab_char * tabs[i]}{cif_ranks[i]['doi']}\n"
    with open(output_path / 'rank.txt', 'w') as output_file:
        output_file.write(rank_doi_score_txt)

    return rank_doi_score_txt


def terminal_print(rank_doi_score_txt):
    '''
    given an iterable object, the object is printed to the terminal, encapsulated by 80 dashes before and after.
    
    Parameters
    ----------
    iterable_object  iterable object
      e.g. a list of strings

    Returns
    -------
    None
    '''
    print('-' * 81)
    for e in rank_doi_score_txt:
        print(e)
    print('-' * 81)

    return None
