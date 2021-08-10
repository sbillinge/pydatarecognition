import os
from pathlib import Path
import numpy as np
import scipy.stats
from scipy.interpolate import interp1d
from skbeam.core.utils import twotheta_to_q
from pydatarecognition.cif_io import cif_read, rank_write, user_input_read
from pydatarecognition.utils import xy_resample
from pydatarecognition.plotters import rank_plot

############################################################################################
TESTFILE = 3 # FIXME Use cli to parse this information instead.
if TESTFILE == 1:
    # test cif, which IS present within the test set
    # together with cifs from same paper
    # x-ray data
    # bm5088150212-01-betaTCPsup2.rtv.combined.cif
    WAVELENGTH = 0.1540598
    USER_INPUT_FILE = 'sandys_data_1.txt'
    XTYPE = 'twotheta'
elif TESTFILE == 2:
    # test cif, which IS present within the test set
    # no other cifs from the same paper
    # x-ray data
    # br2109Isup2.rtv.combined.cif
    WAVELENGTH = 0.154175
    USER_INPUT_FILE = 'sandys_data_2.txt'
    XTYPE = 'twotheta'
elif TESTFILE == 3:
    # test cif, which is NOT present within the test set
    # no other cifs from the same paper
    # neutron data
    # aj5301cubic_1_NDsup19.rtv.combined.cif
    WAVELENGTH = 0.15482
    USER_INPUT_FILE = 'sandys_data_3.txt'
    XTYPE = 'twotheta'
STEPSIZE_REGULAR_QGRID = 10**-3
############################################################################################


def main():
    # These need to be inside main for this to run from an IDE like PyCharm
    # and still find the example files.
    PARENT_DIR = Path.cwd()
    INPUT_DIR = PARENT_DIR / 'powder_data'
    CIF_DIR = PARENT_DIR / 'cifs'
    OUTPUT_DIR = PARENT_DIR / '_output'
    user_input = INPUT_DIR / USER_INPUT_FILE
    ciffiles = CIF_DIR.glob("*.cif")
    doifile = CIF_DIR / 'iucrid_doi_mapping.txt'
    folders = [OUTPUT_DIR]
    for folder in folders:
        if not folder.exists():
            folder.mkdir()
    dois = np.genfromtxt(doifile, dtype='str')
    doi_dict = {}
    for i in range(len(dois)):
        doi_dict[dois[i][0]] = dois[i][1]
    frame_dashchars = '-'*85
    newline_char = '\n'
    print(f'{frame_dashchars}{newline_char}Input data file: {user_input.name}{newline_char}'
          f'Wavelength: {WAVELENGTH} Å.{newline_char}{frame_dashchars}')
    userdata = user_input_read(user_input)
    if XTYPE == 'twotheta':
        user_twotheta, user_intensity = userdata[0,:], userdata[1:,][0]
        user_q = twotheta_to_q(np.radians(user_twotheta), WAVELENGTH)
        user_qmin, user_qmax = np.amin(user_q), np.amax(user_q)
    cifname_ranks, r_pearson_ranks, doi_ranks = [], [], []
    user_dict, cif_dict = {}, {}
    print('Working with CIFs:')
    for ciffile in ciffiles:
        print(ciffile.name)
        ciffile_path = Path(ciffile)
        pcd = cif_read(ciffile_path)
        try:
            data_resampled = xy_resample(user_q, user_intensity, pcd.q, pcd.intensity, STEPSIZE_REGULAR_QGRID)
            pearson = scipy.stats.pearsonr(data_resampled[0][:,1], data_resampled[1][:,1])
            r_pearson = pearson[0]
            p_pearson = pearson[1]
            cifname_ranks.append(ciffile.stem)
            r_pearson_ranks.append(r_pearson)
            doi = doi_dict[pcd.iucrid]
            doi_ranks.append(doi)
            cif_dict[str(ciffile.stem)] = dict([
                        ('intensity', pcd.intensity),
                        ('q', pcd.q),
                        ('qmin', np.amin(pcd.q)),
                        ('qmax', np.amax(pcd.q)),
                        ('q_reg', data_resampled[1][:,0]),
                        ('intensity_resampled', data_resampled[1][:,1]),
                        ('r_pearson', r_pearson),
                        ('p_pearson', p_pearson),
                        ('doi', doi),
                    ])
        except AttributeError:
            print(f"{ciffile.name} was skipped.")
    user_dict[str(user_input.stem)] = dict([
        ('twotheta', userdata[:, 0]),
        ('intensity', userdata[:, 1]),
        ('q', user_q),
        ('q_min', user_qmin),
        ('q_max', user_qmax),
    ])
    cif_rank_pearson = sorted(list(zip(cifname_ranks, r_pearson_ranks, doi_ranks)), key = lambda x: x[1], reverse=True)
    ranks = [{'IUCrCIF': cif_rank_pearson[i][0],
              'score': cif_rank_pearson[i][1],
              'doi': cif_rank_pearson[i][2]} for i in range(len(cif_rank_pearson))]
    rank_txt = rank_write(ranks, OUTPUT_DIR)
    print(f'{frame_dashchars}{newline_char}{rank_txt}{frame_dashchars}')
    rank_plots = rank_plot(data_resampled[0][:,0], data_resampled[0][:, 1], cif_rank_pearson, cif_dict, OUTPUT_DIR)
    print(f'A txt file with rankings has been saved to the txt directory,{newline_char}'
          f'and a plot has been saved to the png directory.{newline_char}{frame_dashchars}')
    return None

if __name__ == "__main__":
    # in Pycharm (and probably other IDEs) it runs main in place, so if so
    # detect this and move to the examples folder where it can find the data
    cwd = Path().cwd()
    relpath = cwd / ".." / "docs" / "examples"
    if cwd.parent.name == "pydatarecognition" and cwd.parent.parent.name != "pydatarecognition":
        os.chdir(relpath)

    main()

# End of file.
