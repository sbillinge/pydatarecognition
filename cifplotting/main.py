# Import section
import sys
import os
from pathlib import Path
import matplotlib.pyplot as plt
# import matplotlib as mpl
# from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style
import numpy as np
import scipy.stats
from scipy.interpolate import interp1d
# import json

# Data section
from cifplotting.io import cif_read, rank_write, user_input_read
from cifplotting.plotters import rank_plot
from cifplotting.utils import data_sampler, pearson_correlator

def main():
    WAVELENGTH = 1.548
    parent_path = Path.cwd().resolve().parent
    cif_data_path = parent_path / 'data'
    cif_dir = cif_data_path / 'cif'
    output_path = parent_path / '_output'
    powder_data_dir = cif_data_path / 'powder_data'
    cif_file_list = cif_dir.glob("*.cif")
    user_input_file = powder_data_dir / 'sandys_data.txt'
    png_path = output_path / 'png'
    txt_path = output_path / 'txt'
    folders = [txt_path, png_path]
    for folder in folders:
        if not folder.exists():
            folder.mkdir()
    print('-'*80 + '\nInput data file: ' + str(user_input_file.name))
    print('Wavelength: ' + str(WAVELENGTH) + ' Å.')
    user_data = user_input_read(user_input_file, WAVELENGTH)
    # int_scaled_user = user_data[2]
    new_user_grid = data_sampler(user_data)
    file_name_list, r_pearson_list = [], []
    data_dict = {}
    print('\nWorking with files:')
    for file in file_list:
        print(file)
        file_path = Path(file)
        cif_data = cif_read(file_path)
        print('Number of data points: ' + str(len(cif_data[0])) + '\n')
        new_data_grid = data_sampler(cif_data)
        # txt = xy_writer(file_path, txt_path, data)
        # plot = cif_plotter(file_path, parent_path, png_path, data)
        r_pearson = pearson_correlator(new_user_grid, new_data_grid)
        file_name_list.append(file_path.stem)
        r_pearson_list.append(r_pearson)
        data_dict[file.stem] = dict([
                                ('tt', cif_data[0]),
                                ('q', cif_data[1]),
                                ('int_exp', cif_data[2]),
                                ('int_scaled', cif_data[3]),
                                ('q_grid', new_data_grid[0]),
                                ('int_grid', new_data_grid[1]),
                                ('r_pearson', r_pearson)])
    cif_pearson_list = list(zip(file_name_list, r_pearson_list))
    cif_rank_pearson_list = sorted(cif_pearson_list, key = lambda x: x[1], reverse=True)
    rank_txt = rank_write(cif_rank_pearson_list, txt_path)
    rank_plots = rank_plot(user_data, cif_rank_pearson_list, data_dict, png_path)
    print('\nA txt file with rankings has been saved into the txt directory, and a plot has been saved into png directory.')

    return None
    # End of function.

if __name__ == "__main__":
    main()

# End of file.
