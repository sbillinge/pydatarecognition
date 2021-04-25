def cif_reader(file_path):

    # Open cif file and read lines.
    with open(file_path, 'r') as input_file:
        lines = input_file.readlines()
    input_file.close

    # The the indices for the lines containing the probe and wavelength
    # and the lines where the data starts and ends.
    for i in range(0, len(lines)):
        if '_diffrn_radiation_probe' in lines[i]:
            probe = lines[i].split()[-1]

        elif '_diffrn_radiation_wavelength' in lines[i]:
            wavelength = float(lines[i].split()[-1])

        elif '_pd_proc_intensity_bkg_calc' in lines[i]:
            start = i + 2

        elif '_pd_proc_number_of_points' in lines[i]:
            end = i

    # Append twotheta and intensity values to lists.
    # Calculate q-values and append to list.
    tt, int_exp, q = [], [], []
    for i in range(start, end):
        tt.append(float(lines[i].split()[1]))
        q.append(4 * np.pi * np.sin((np.pi / 180) * float(lines[i].split()[1]) / 2) / wavelength)
        int_exp.append(float(lines[i].split()[2].split('(')[0]))

    # Getting the minimum and maximum q-values, rounded to two digits.
    q_min_round_up = np.ceil(min(q) * 10**2) / 10**2
    q_max_round_down = np.floor(max(q) * 10**2) / 10**2

    # Scale the intensities with respect to the maximum intensity
    # and append to list.
    int_scaled = []
    # int_max = max(int_exp)
    # for i in range(0, len(int_exp)):
    #     int_scaled.append(int_exp[i] / int_max)

    # plt.plot(q, int_scaled)
    # plt.xlabel(r"$Q$ $[\mathrm{\AA^{-1}}]$")
    # plt.ylabel(r"$I$ $[\mathrm{a.u.}]$")
    # plt.show()
    # sys.exit()

    # Append values to be returned to data list that is returned.
    data = []
    data.append(tt)
    data.append(q)
    data.append(int_exp)
    data.append(int_scaled)
    data.append([q_min_round_up, q_max_round_down])
    data.append(probe)

    return data
    # End fo function.

def powdercif_pattern_extractor(file_path, txt_path, data):

    # Unpacking twotheta and intensity lists from data list.
    tt = data[0]
    int_exp = data[2]

    # Appending lines to txt list.
    txt = []
    for i in range(0, len(tt)):
        if len(str(tt[i])) <= 7:
            txt.append(str(tt[i]) + ('\t')*2 + str(int_exp[i]) + '\n')
        elif len(str(tt[i])) > 7:
            txt.append(str(tt[i]) + '\t' + str(int_exp[i]) + '\n')

    # Getting the file name without file extension and setting up txt path.
    file_name = file_path.stem
    txt_file_path = txt_path / file_name

    # Writing txt file.
    with open(str(txt_file_path) + '.txt', 'w') as output_file:
        output_file.writelines(txt)
    output_file.close()

    return powder_pattern
    # End of function.

def user_input_read(user_input_file, wavelength):

    # Opening file and reading lines.
    with open(user_input_file) as input_file:
        lines = input_file.readlines()
    input_file.close()

    # Appending twotheta and intensity values to lists.
    # Calculating q-values and appending to list.
    tt, q, int_exp = [], [], []
    for line in lines:
        tt.append(float(line.split()[0]))
        q.append(float(4 * np.pi * np.sin((np.pi / 180) * float(line.split()[0]) / 2) / wavelength))
        int_exp.append(float(line.split()[1]))

    # Getting minimum and maximum q-values rounded to two digits.
    q_min_round_up = np.ceil(min(q) * 10**2) / 10**2
    q_max_round_down = np.floor(max(q) * 10**2) / 10**2

    # Calculating the scaled intensity with respect to the maximum intensity
    # and appending to list.
    int_scaled = []
    # int_max = max(int_exp)
    # for i in range(0, len(int_exp)):
    #     int_scaled.append(int_exp[i] / int_max)

    # Appending data to be returned to list.
    data_user = []
    data_user.append(tt)
    data_user.append(q)
    data_user.append(int_exp)
    data_user.append(int_scaled)
    data_user.append([q_min_round_up, q_max_round_down])

    return data_user
    # End of function.

def rank_writer(sorted_zipped_list, txt_path):

    # Printing top 10 ranked cif files to terminal
    # and writing to txt file.
    txt = []
    print('-'*80)
    print('Rank\tFile\t\t\t\t\t\tPearson coefficient')
    txt.append('Rank\tFile\t\t\t\t\t\tPearson coefficient\n')
    for i in range(0, 10):
        if len(sorted_zipped_list[i][0]) < 40:
            print(str(i + 1) + '\t' + str(sorted_zipped_list[i][0]) + '\t\t' + "{:.4f}".format(sorted_zipped_list[i][1]))
            txt.append(str(i + 1) + '\t' + str(sorted_zipped_list[i][0]) + '\t\t' + "{:.4f}".format(sorted_zipped_list[i][1]) + '\n')

        elif len(sorted_zipped_list[i][0]) >= 40:
            print(str(i + 1) + '\t' + str(sorted_zipped_list[i][0]) + '\t' + "{:.4f}".format(sorted_zipped_list[i][1]))
            txt.append(str(i + 1) + '\t' + str(sorted_zipped_list[i][0]) + '\t' + "{:.4f}".format(sorted_zipped_list[i][1]) + '\n')

    print('-'*80)

    with open(txt_path / 'rank.txt', 'w') as output_file:
        output_file.writelines(txt)
    output_file.close()

    return None
    # End of function.
