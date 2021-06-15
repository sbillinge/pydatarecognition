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

WAVELENGTH = 1.548
XTYPE = 'twotheta'
USER_INPUT_FILE = 'sandys_data.txt'

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
        user_qgrid = twotheta_to_q(userdata[:,0], WAVELENGTH)
        user_interpol = interp1d(np.array(user_qgrid), np.array(userdata[:,1]), kind='linear')
    user_qmin, user_qmax = np.amin(user_qgrid), np.amax(user_qgrid)
    cif_file_name_list, r_pearson_list = [], []
    data_dict = {}
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
        cif_twotheta = np.array([e[0] for e in cif_twotheta]).astype(np.float)
        cif_intensity = np.char.split(cifdata[cifdata.keys()[0]]['_pd_proc_intensity_total'], '(')
        cif_twotheta = np.array([e[0] for e in cif_intensity]).astype(np.float)
        # plt.plot(cif_twotheta, cif_intensity)
        # plt.show()
        # sys.exit()
        ############################################################################################
        # move this to utils and write function for getting wavelength from cifs
        for i in range(len(cifdata.keys())):
            try:
                cif_wavelength = cifdata[cifdata.keys()[i]]['_diffrn_radiation_wavelength']
                if type(cif_wavelength) == list:
                    cif_wavelength = np.float(cif_wavelength[0])
                else:
                    cif_wavelength = np.float(cif_wavelength)
                break
            except KeyError:
                pass
        ############################################################################################
        cif_q = np.array(twotheta_to_q(np.radians(cif_twotheta), cif_wavelength))
        # plt.plot(cif_q, cif_intensity)
        # plt.show()
        # sys.exit()
        ############################################################################################
        # CONTINUE FROM HERE TOMORROW
        # do interpolations
        # use interpols to calc ints on regular q grid
        # get common q range
        # do pearson correlation for the common q range when sampled on the same regular q grid
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
        data_dict[ciffile.stem] = dict([
                                ('twotheta', cif_twotheta),
                                ('q', cif_q),
                                ('intensity', cif_intensity),
    #                             ('q_regular', new_data_grid[0]),
    #                             ('int_grid', new_data_grid[1]),
    #                             ('r_pearson', r_pearson)])
        ])
    # cif_pearson_list = list(zip(cif_file_name_list, r_pearson_list))
    # cif_rank_pearson_list = sorted(cif_pearson_list, key = lambda x: x[1], reverse=True)
    # rank_txt = rank_write(cif_rank_pearson_list, txt_path)
    # rank_plots = rank_plot(user_data, cif_rank_pearson_list, data_dict, png_path)
    # print('\nA txt file with rankings has been saved into the txt directory, and a plot has been saved into png directory.')

    return None
    # End of function.

if __name__ == "__main__":
    main()

# End of file.
