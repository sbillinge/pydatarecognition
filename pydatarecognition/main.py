import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from pydatarecognition.io import cif_read, rank_write, terminal_print
from pydatarecognition.plotters import iq_plot, itt_plot, iinvd_plot, rank_plot
from pydatarecognition.utils import data_sample, pearson_correlate
from skbeam.core.utils import twotheta_to_q, d_to_q, q_to_twotheta, q_to_d
from diffpy.utils.parsers.loaddata import loadData
from scipy.interpolate import interp1d
import scipy.stats

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

def main():
    inputdir_path = Path.cwd().parent / '_input'
    cifdir_path = inputdir_path / 'cif'
    doifilepath = inputdir_path / 'doi/dois.txt'
    outputdir_path = Path.cwd().parent / '_output'
    powderdatadir_path = inputdir_path / 'powder_data'
    user_input_file_path = powderdatadir_path / USER_INPUT_FILE
    pngdir_path = outputdir_path / 'png'
    txtdir_path = outputdir_path / 'txt'
    ciffile_list = cifdir_path.glob("*.cif")
    folders = [outputdir_path, txtdir_path, pngdir_path]
    for folder in folders:
        if not folder.exists():
            folder.mkdir()
    dois = np.genfromtxt(doifilepath, dtype='str')
    doi_dict = {}
    for i in range(len(dois)):
        doi_dict[dois[i][0]] = dois[i][1]
    frame_dashchars = '-'*112
    newline_char = '\n'
    tab_char = '\t'
    print(f'{frame_dashchars}{newline_char}Input data file: {user_input_file_path.name}{newline_char}'
          f'Wavelengt: {WAVELENGTH} Å.{newline_char}{frame_dashchars}')
    userdata = loadData(user_input_file_path)
    if XTYPE == 'twotheta':
        user_twotheta = userdata[:,0]
        user_q = twotheta_to_q(np.radians(user_twotheta), WAVELENGTH)
        user_intensity = np.array(userdata[:,1])
    user_qmin, user_qmax = np.amin(user_q), np.amax(user_q)
    cifname_list, r_pearson_list, doi_list = [], [], []
    user_dict, cif_dict = {}, {}
    print('Working with CIFs:')
    for ciffile in ciffile_list:
        print(ciffile.name)
        ciffile_path = Path(ciffile)
        cifdata = cif_read(ciffile_path)
        # move this two utils and write functions for getting twotheta and intensities from cifs
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
        cifname_list.append(ciffile.stem)
        r_pearson_list.append(r_pearson)
        doi = doi_dict[str(ciffile.stem)[0:6]]
        doi_list.append(doi)
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
    cif_rank_pearson_list = sorted(list(zip(cifname_list, r_pearson_list, doi_list)), key = lambda x: x[1], reverse=True)
    ranks = [{'IUCrCIF': cif_rank_pearson_list[i][0],
              'score': cif_rank_pearson_list[i][1],
              'doi': cif_rank_pearson_list[i][2]} for i in range(len(cif_rank_pearson_list))]
    rank_txt = rank_write(ranks, txtdir_path)
    print(f'{frame_dashchars}{newline_char}{rank_txt}{frame_dashchars}')
    rank_plots = rank_plot(q_reg, userdata_resampled[:, 1], cif_rank_pearson_list, cif_dict, pngdir_path)
    print(f'A txt file with rankings has been saved into the txt directory,'
          f'and a plot has been saved into the png directory.{newline_char}{frame_dashchars}')
    return None

if __name__ == "__main__":
    main()

# End of file.
