import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from pydatarecognition.io import cif_read, rank_write, user_input_read
from pydatarecognition.plotters import rank_plot
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

def main():
    inputdir_path = Path.cwd().parent / '_input'
    cifdir_path = inputdir_path / 'cif'
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
    frame_dashchars = '-'*80
    newline_char = '\n'
    tab_char = '\t'
    print(f'{frame_dashchars}{newline_char}Input data file: {user_input_file_path.name}{newline_char}'
          f'Wavelengt: {WAVELENGTH} Å.{newline_char}{frame_dashchars}')
    userdata = loadData(user_input_file_path)
    if XTYPE == 'twotheta':
        user_q = twotheta_to_q(np.radians(userdata[:,0]), WAVELENGTH)
        user_intensity = np.array(userdata[:,1])
    user_qmin, user_qmax = np.amin(user_q), np.amax(user_q)
    cifname_list, r_pearson_list = [], []
    user_dict, cif_dict = {}, {}
    print('\nWorking with CIFs:')
    for ciffile in ciffile_list:
        print(ciffile.name)
        ciffile_path = Path(ciffile)
        cifdata = cif_read(ciffile_path)
        ############################################################################################
        # Q keys from jsons.
        #
        # qkeys = (
        #     '_pdcifplot_pd_proc_2theta_corrected,Q',
        #     '_pdcifplot_pd_proc_d_spacing,Q',
        #     '_pdcifplot_pd_meas_2theta_range_,Q',
        #     '_pdcifplot_pd_proc_2theta_range_,Q',
        #     '_pdcifplot_pd_meas_2theta_scan,Q',
        #     '_pdcifplot_pd_meas_2theta_corrected,Q'
        # )
        ############################################################################################
        # possible twotheta keys that we want two browse through, when generalizing the code.
        # ttkeys = (
        #     '_pd_proc_2theta_corrected',
            # '_pd_meas_2theta_scan',
            # '_pdcifplot_pd_meas_2theta_range_',
            # '_pd_meas_2theta_range_, Q',
            # '_pd_meas_2theta_range_, d',
            # '_pd_proc_2theta_range_',
            # '_pd_proc_2theta_range_, Q',
            # '_pd_proc_2theta_range_, d',
            # '_pd_meas_2theta_scan, Q',
            # '_pd_meas_2theta_corrected',
            # '_pd_meas_2theta_corrected, Q'
        # )
        ############################################################################################
        # possible twotheta keys that we want two browse through, when generalizing the code.
        # ikeys = (
        #     '_pd_proc_intensity_total',
            # '_pd_proc_intensity_total_su',
            # '_pd_calc_intensity_total',
            # '_pd_proc_intensity_bkg_calc',
            # '_pd_proc_intensity_net',
            # '_pd_calc_intensity_net',
            # '_pd_meas_intensity_total',
            # '_pd_meas_intensity_total_su',
            # '_pd_proc_intensity_bkg_fix',
            # '_pd_proc_intensity_net_su',
            # '_pd_meas_intensity_net'
        # )
        ############################################################################################
        # move this two utils and write functions for getting twotheta and intensities from cifs
        cif_twotheta = np.char.split(cifdata[cifdata.keys()[0]]['_pd_proc_2theta_corrected'], '(')
        cif_twotheta = np.array([e[0] for e in cif_twotheta]).astype(np.float64)
        cif_intensity = np.char.split(cifdata[cifdata.keys()[0]]['_pd_proc_intensity_total'], '(')
        cif_intensity = np.array([e[0] for e in cif_intensity]).astype(np.float64)
        # plt.plot(cif_twotheta, cif_intensity)
        # plt.show()
        # sys.exit()
        ############################################################################################
        # move this to utils and write function for getting wavelength from cifs
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
        ############################################################################################
        cif_q = np.array(twotheta_to_q(np.radians(cif_twotheta), cif_wavelength))
        cif_qmin, cif_qmax = np.amin(cif_q), np.amax(cif_q)
        # plt.plot(cif_q, cif_intensity)
        # plt.show()
        # sys.exit()
        ############################################################################################
        # CONTINUE FROM HERE TOMORROW
        # do interpolations
        user_interpol = interp1d(user_q, user_intensity, kind='linear')
        cif_interpol = interp1d(cif_q, cif_intensity, kind='linear')
        # get common q range
        q_min_common, q_max_common = max(user_qmin, cif_qmin), min(user_qmax, cif_qmax)
        # print(user_qmin, user_qmax)
        # print(cif_qmin, cif_qmax)
        # sys.exit()
        # get regular q grid
        q_reg = np.arange(q_min_common, q_max_common, STEPSIZE_REGULAR_QGRID)
        # use interpols to calc ints on regular q grid
        userdata_resampled = np.column_stack((q_reg, user_interpol(q_reg)))
        cifdata_resampled = np.column_stack((q_reg, cif_interpol(q_reg)))
        # plt.plot(userdata_resampled[:,0], userdata_resampled[:,1])
        # plt.plot(cifdata_resampled[:, 0], cifdata_resampled[:, 1])
        # plt.plot(q_reg, cifdata_resampled[:, 1] - userdata_resampled[:, 1])
        # plt.show()
        # sys.exit()
        # do pearson correlation for the common q range when sampled on the same regular q grid
        pearson = scipy.stats.pearsonr(userdata_resampled[:,1], cifdata_resampled[:,1])
        r_pearson = pearson[0]
        p_pearson = pearson[1]
        cifname_list.append(ciffile.stem)
        r_pearson_list.append(r_pearson)
        # print(pearson_r, pearson_p)
        # sys.exit()
        # do ranking

        # store things in dictionary
        # try to include dois
        # print and write results
        # provide plots
        ############################################################################################
    #     new_data_grid = data_sample(cif_data)
    #     # txt = xy_writer(file_path, txt_path, data)
    #     # plot = cif_plotter(file_path, parent_path, png_path, data)
    #     r_pearson = pearson_correlate(new_user_grid, new_data_grid)
    #     cif_file_name_list.append(cif_file_path.stem)
    #     r_pearson_list.append(r_pearson)
        try:
            user_dict[user_input_file_path.stem]
        except KeyError:
            user_dict[user_input_file_path.stem] = dict([
                ('twotheta', userdata[:, 0]),
                ('intensity', userdata[:, 1]),
                ('q', user_q),
                ('q_min', user_qmin),
                ('q_max', user_qmax),
                ('q_reg', np.arange(user_qmin, user_qmax, STEPSIZE_REGULAR_QGRID)),
                ('intensity_resampled', userdata_resampled[:, 1]),
            ])
        cif_dict[ciffile.stem] = dict([
            ('twotheta', cif_twotheta),
            ('intensity', cif_intensity),
            ('q', cif_q),
            ('qmin', cif_qmin),
            ('qmax', cif_qmax),
            ('q_reg', np.arange(cif_qmin, cif_qmax, STEPSIZE_REGULAR_QGRID)),
            ('intensity_resampled', cifdata_resampled[:,1]),
            ('r_pearson', r_pearson),
            ('p_pearson', p_pearson),
        ])
    cif_rank_pearson_list = sorted(list(zip(cifname_list, r_pearson_list)), key = lambda x: x[1], reverse=True)
    ranks = [{'IUCrCIF': cif_rank_pearson_list[i][0],
              'score': cif_rank_pearson_list[i][1],
              'doi': 'dummy'} for i in range(len(cif_rank_pearson_list))]
    # cif_pearson_list = sorted(cif_pearson_list, key = lambda x: x[1], reverse=True)
    rank_txt = rank_write(ranks, txtdir_path)
    # rank_plots = rank_plot(user_data, cif_rank_pearson_list, data_dict, png_path)
    # print('\nA txt file with rankings has been saved into the txt directory, and a plot has been saved into png directory.')

    return None
    # End of function.

if __name__ == "__main__":
    main()

# End of file.
