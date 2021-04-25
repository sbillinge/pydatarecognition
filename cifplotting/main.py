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
from cifplotting.io import cif_read, rank_writer, user_input_read
from cifplotting.plotters import rank_plotter
from cifplotting.utils import data_sampler, pearson_correlator


def cif_plotter(file_path, parent_path, png_path, data):

    # Getting the file name and setting up the plot file name.
    file_name = str(file_path.resolve().stem)
    plot_file_name = file_name + '.png'

    # Unpacking twotheta and intensity lists from data list.
    tt = data[0]
    int_exp = data[1]

    # mpl.rcParams.update(mpl.rcParamsDefault)
    # plt.style.use(os.path.join(parent_path, "utils","billinge.mplstyle"))

    # Plot style used.
    plt.style.use(bg_mpl_style)

    # Making figure using subplots.
    fig, ax = plt.subplots(dpi=300, figsize=(12,4))

    # Plotting twotheta vs. intensity.
    ax.plot(tt, int_exp, linewidth=1)

    # Setting the y-axis to scientific notation.
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

    # Setting labels for the axes.
    ax.set_xlabel(r"2$\theta$ $[^{\circ}]$")#, labelpad=5)
    ax.set_ylabel(r"$I$ $[\mathrm{counts}]$")#, labelpad=5)

    # Setting the limits for the axes.
    plt.xlim(min(tt), max(tt))
    # plt.ylim(min(int), max(int))

    # Saving figure to png file and closing figure.
    plt.savefig(png_path / plot_file_name, bbox_inches='tight')
    plt.close()

    return None
    # End fo function.


def main():
    WAVELENGTH = 1.548
    parent_path = Path.cwd().resolve().parent
    data_path = parent_path / 'data'
    cif_dir = data_path / 'cif'
    output_path = parent_path / '_output'
    powder_data_dir = data_path / 'powder_data'
    cif_file_list = cif_dir.glob("*.cif")
    user_input_file = parent_path / 'sandys_data.txt'
    png_path = output_path / 'png'
    txt_path = output_path / 'txt'
    folders = [txt_path, png_path]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)


    print('-'*80 + '\nInput data file: ' + str(user_input_file.name))
    print('Wavelength: ' + str(WAVELENGTH) + ' Å.')
    # Extracting data from user file.
    user_data = user_input_read(user_input_file, WAVELENGTH)

    # Getting the scaled intensities from the user data.
    int_scaled_user = user_data[2]

    # Sampling the user data on a new grid.
    new_user_grid = data_sampler(user_data)

    # Dictionary for filenames, q-values, and scaled intensities on
    # new grid for cif files.
    data_dict = {}

    # Lists for filenames and Pearson coefficients to be printed.
    file_name_list, r_pearson_list = [], []

    # Printing to terminal.
    print('\nWorking with files:')

    # Looping through list of cif files.
    for file in file_list:
        # Printing the file name.
        print(file)

        # Getting the path for the cif file.
        file_path = Path(file)

        # Extracting data from the cif file.
        data = cif_read(file_path)
        print('Number of data points: ' + str(len(data[0])) + '\n')

        # Sampling Q-values and scaled intensities on new grid.
        new_data_grid = data_sampler(data)

        # Writing .txt file with twotheta and intensity values from cif file.
        # txt = xy_writer(file_path, txt_path, data)

        # Plotting twotheta and intensities from cif file.
        # plot = cif_plotter(file_path, parent_path, png_path, data)

        # Calculating the Pearson coefficient.
        r_pearson = pearson_correlator(new_user_grid, new_data_grid)

        # Appending name of cif file to list of filenames.
        file_name_list.append(file_path.stem)

        # Appending Pearson coefficient to list of of Pearson coefficients.
        r_pearson_list.append(r_pearson)

        # Dictionary with Q-values, scaled intensities, and Pearson coefficient
        # for all cif files.
        data_dict[file.stem] = dict([
                                ('tt', data[0]),
                                ('q', data[1]),
                                ('int_exp', data[2]),
                                ('int_scaled', data[3]),
                                ('q_grid', new_data_grid[0]),
                                ('int_grid', new_data_grid[1]),
                                ('r_pearson', r_pearson)
                                ])

    # Zipping cif filenames and their corresponding Pearson coefficients.
    zipped_list = list(zip(file_name_list, r_pearson_list))

    # Sorting the zipped lists in ascending order with respect to the Pearson
    # coefficient.
    sorted_zipped_list = sorted(zipped_list, key = lambda x: x[1], reverse=True)

    # Writing dictionary with cif data to text file.
    # with open(parent_path / 'cif_dict.txt', 'w') as output_file:
    #     output_file.write(json.dumps(data_dict))
    # output_file.close()

    # Writing top 5 rank to txt file.
    rank_txt = rank_writer(sorted_zipped_list, txt_path)

    # Plotting user data and top five rank and saving to png file.
    rank_plots = rank_plotter(user_data, sorted_zipped_list, data_dict, png_path)
    print('\nA txt file with rankings has been saved into the txt directory, and a plot has been saved into png directory.')

    return None
    # End of function.

if __name__ == "__main__":
    main()

# End of file.
