from pydatarecognition.io import cif_read, rank_write
from pydatarecognition.plotters import rank_plot
from pathlib import Path
import numpy as np
from skbeam.core.utils import twotheta_to_q
from diffpy.utils.parsers.loaddata import loadData
from scipy.interpolate import interp1d
import scipy.stats

import sys

############################################################################################
TESTFILE = 1
if TESTFILE == 0:
    # first test cif, which IS NOT present within the test set
    WAVELENGTH = 1.548
    XTYPE = 'twotheta'
    USER_INPUT_FILE = 'sandys_data.txt'
elif TESTFILE == 1:
    # second test cif, which IS present within the test set
    WAVELENGTH = 1.540598
    USER_INPUT_FILE = 'sandys_data_1.txt'
    XTYPE = 'twotheta'
elif TESTFILE == 2:
    # third test cif, which IS present within the test set
    WAVELENGTH = 0
    USER_INPUT_FILE = ''
    XTYPE = 'twotheta'

STEPSIZE_REGULAR_QGRID = 10**-3
############################################################################################

PARENT_DIR = Path.cwd()
INPUT_DIR = PARENT_DIR / 'powder_data'
CIF_DIR = PARENT_DIR / 'cifs'
OUTPUT_DIR = PARENT_DIR / '_output'

def main():
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
    tab_char = '\t'
    print(f'{frame_dashchars}{newline_char}Input data file: {user_input.name}{newline_char}'
          f'Wavelength: {WAVELENGTH} Å.{newline_char}{frame_dashchars}')
    userdata = loadData(user_input)
    if XTYPE == 'twotheta':
        user_twotheta = userdata[:,0]
        user_q = twotheta_to_q(np.radians(user_twotheta), WAVELENGTH)
        user_intensity = np.array(userdata[:,1])
    user_qmin, user_qmax = np.amin(user_q), np.amax(user_q)
    cifname_ranks, r_pearson_ranks, doi_ranks = [], [], []
    user_dict, cif_dict = {}, {}
    print('Working with CIFs:')
    for ciffile in ciffiles:
        print(ciffile.name)
        cifdata = cif_read(ciffile)
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
        cif_q = np.array(twotheta_to_q(np.radians(cif_twotheta), cif_wavelength))
        cif_qmin, cif_qmax = np.amin(cif_q), np.amax(cif_q)
        user_interpol = interp1d(user_q, user_intensity, kind='linear')
        cif_interpol = interp1d(cif_q, cif_intensity, kind='linear')
        q_min_common, q_max_common = max(user_qmin, cif_qmin), min(user_qmax, cif_qmax)
        q_reg = np.arange(q_min_common, q_max_common, STEPSIZE_REGULAR_QGRID)
        userdata_resampled = np.column_stack((q_reg, user_interpol(q_reg)))
        cifdata_resampled = np.column_stack((q_reg, cif_interpol(q_reg)))
        pearson = scipy.stats.pearsonr(userdata_resampled[:,1], cifdata_resampled[:,1])
        r_pearson = pearson[0]
        p_pearson = pearson[1]
        cifname_ranks.append(ciffile.stem)
        r_pearson_ranks.append(r_pearson)
        doi = doi_dict[str(ciffile.stem)[0:6]]
        doi_ranks.append(doi)
        # user_iq_plot = iq_plot(user_q, userdata[:,1])
        # user_itt_plot = itt_plot(userdata[:, 0], userdata[:, 1])
        # cif_iq_plot = iq_plot(cif_q, cif_intensity)
        # cif_itt_plot = itt_plot(cif_twotheta, cif_intensity)
        # try:
        #     user_dict[str(user_input_file_path.stem)]
        # except KeyError:
        #     user_dict[str(user_input_file_path.stem)] = dict([
        #         ('twotheta', userdata[:, 0]),
        #         ('intensity', userdata[:, 1]),
        #         ('q', user_q),
        #         ('q_min', user_qmin),
        #         ('q_max', user_qmax),
        #         ('q_reg', np.arange(user_qmin, user_qmax, STEPSIZE_REGULAR_QGRID)),
        #         ('intensity_resampled', userdata_resampled[:, 1]),
        #         ('iq_plot', user_iq_plot),
        #         ('itt_plot', user_itt_plot),
        #     ])
        cif_dict[str(ciffile.stem)] = dict([
        #     ('twotheta', cif_twotheta),
        #     ('intensity', cif_intensity),
        #     ('q', cif_q),
        #     ('qmin', cif_qmin),
        #     ('qmax', cif_qmax),
        #     ('q_reg', np.arange(cif_qmin, cif_qmax, STEPSIZE_REGULAR_QGRID)),
            ('intensity_resampled', cifdata_resampled[:,1]),
        #     ('r_pearson', r_pearson),
        #     ('p_pearson', p_pearson),
        #     ('doi', doi),
        #     ('iq_plot', cif_iq_plot),
        #     ('itt_plot', cif_itt_plot),
        ])
    cif_rank_pearson = sorted(list(zip(cifname_ranks,
                                            r_pearson_ranks, doi_ranks)), key = lambda x: x[1], reverse=True)
    ranks = [{'IUCrCIF': cif_rank_pearson[i][0],
              'score': cif_rank_pearson[i][1],
              'doi': cif_rank_pearson[i][2]} for i in range(len(cif_rank_pearson))]
    rank_txt = rank_write(ranks, OUTPUT_DIR)
    print(f'{frame_dashchars}{newline_char}{rank_txt}{frame_dashchars}')
    rank_plots = rank_plot(q_reg, userdata_resampled[:, 1], cif_rank_pearson, cif_dict, OUTPUT_DIR)
    print(f'A txt file with rankings has been saved to the txt directory,{newline_char}'
          f'and a plot has been saved to the png directory.{newline_char}{frame_dashchars}')
    return None

if __name__ == "__main__":
    main()

# End of file.
