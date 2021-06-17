from pathlib import Path
import numpy as np
import yaml

from diffpy.structure.parsers.p_cif import _fixIfWindowsPath
from diffpy.utils.parsers.loaddata import loadData
import CifFile
from skbeam.core.utils import twotheta_to_q

from pydatarecognition.powdercif import PowderCif

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
    cache = Path().cwd() / "_cache"
    if not cache.exists():
        cache.mkdir()
    acache = cif_file_path.parent() / f"{cif_file_path.stem}.npy"
    mcache = cif_file_path.parent() / f"{cif_file_path.stem}.yml"
    # cached = cache / "test.npy"
    # with open(cached, "w") as o:
    #     o.write("hello_q")

    cachegen = cache.glob("*.npy")
    index = list(set([file.stem[:-2] for file in cachegen]))
    if cif_file_path.stem in index:
        with open(acache) as o:
            q = np.load(o)[0]
            i = np.load(o)[1]
        with open(mcache) as o:
            meta = yaml.safe_load(o)
        po = PowderCif(meta.get("iucrid"),
                       "invnm", q, i,
                       wavelenth=meta.get("wavelength"),
                       wavel_units="nm"
                       )
    else:
        cifdata = CifFile.ReadCif(_fixIfWindowsPath(str(cif_file_path)))
        cif_twotheta = np.char.split(cifdata[cifdata.keys()[0]]['_pd_proc_2theta_corrected'], '(')
        cif_twotheta = np.array([e[0] for e in cif_twotheta]).astype(np.float64)
        cif_intensity = np.char.split(cifdata[cifdata.keys()[0]]['_pd_proc_intensity_total'], '(')
        cif_intensity = np.array([e[0] for e in cif_intensity]).astype(np.float64)
        for i in range(len(cifdata.keys())):
            try:
                cif_wavelength = cifdata[cifdata.keys()[i]]['_diffrn_radiation_wavelength']
                if type(cif_wavelength) == list:
                    cif_wavelength = np.float64(cif_wavelength[0])
                else:
                    cif_wavelength = np.float64(cif_wavelength)
                break
            except KeyError:
                pass
        po = PowderCif(cif_file_path.stem[0:6],
                       "invnm", np.radians(cif_twotheta), cif_intensity,
                       wavelenth=cif_wavelength,
                       wavel_units="ang"
                       )
        with open(acache, "r") as o:
            np.save(np.array([po.q, po.intensity]))
        with open(mcache, "r") as o:
            yaml.dump({"iucrid": po.iucrid, "wavelength": po.wavelength})

    return po


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
    tablen_print = 4
    tablen_write = 8
    strlen = [len(cif_ranks[i]['IUCrCIF']) for i in range(len(cif_ranks))]
    strlen_max = max(strlen)
    char_max_print = strlen_max - (strlen_max % tablen_print) + tablen_print
    char_max_write = strlen_max - (strlen_max % tablen_write) + tablen_write
    tabs_print = [int(((char_max_print - (strlen[i] - (strlen[i] % tablen_print) + tablen_print)) / tablen_print) + 1)
                  for i in range(len(strlen))]
    tabs_write = [int(((char_max_write - (strlen[i] - (strlen[i] % tablen_write) + tablen_write)) / tablen_write) + 1)
                  for i in range(len(strlen))]
    tab_char = '\t'
    rank_doi_score_txt_print = f"Rank\tScore\tIUCr CIF{tab_char * (int(char_max_print / tablen_print) - 2)}DOI\n"
    rank_doi_score_txt_write = f"Rank\tScore\tIUCr CIF{tab_char * (int(char_max_write / tablen_write) - 1)}DOI\n"
    for i in range(len(cif_ranks)):
        rank_doi_score_txt_write += f"{i+1}\t{cif_ranks[i]['score']:.4f}\t{cif_ranks[i]['IUCrCIF']}" \
                                    f"{tab_char * tabs_write[i]}{cif_ranks[i]['doi']}\n"
        rank_doi_score_txt_print += f"{i+1}{tab_char*2}{cif_ranks[i]['score']:.4f}\t{cif_ranks[i]['IUCrCIF']}" \
                                    f"{tab_char * tabs_print[i]}{cif_ranks[i]['doi']}\n"
    with open(output_path / 'rank_WindowsNotepad.txt', 'w') as output_file:
        output_file.write(rank_doi_score_txt_write)
    with open(output_path / 'rank_PyCharm_Notepad++.txt', 'w') as output_file:
        output_file.write(rank_doi_score_txt_print)

    return rank_doi_score_txt_print


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
