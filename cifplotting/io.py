import numpy as np

def cif_read(cif_file_path):
    '''
    given a cif file-path, reads the cif and returns the cif data
    
    Parameters
    ----------
    cif_file_path  pathlib.Path object
      the path to a valid cif file

    Returns
    -------
    the cif data as a dictionary
    '''
    with open(cif_file_path, 'r') as input_file:
        lines = input_file.readlines()
    for i in range(0, len(lines)):
        if '_diffrn_radiation_probe' in lines[i]:
            probe = lines[i].split()[-1]
        elif '_diffrn_radiation_wavelength' in lines[i]:
            wavelength = float(lines[i].split()[-1])
        elif '_pd_proc_intensity_bkg_calc' in lines[i]:
            start = i + 2
        elif '_pd_proc_number_of_points' in lines[i]:
            end = i
    tt, int_exp, q = [], [], []
    for i in range(start, end):
        tt.append(float(lines[i].split()[1]))
        q.append(4 * np.pi * np.sin((np.pi / 180) * float(lines[i].split()[1]) / 2) / wavelength)
        int_exp.append(float(lines[i].split()[2].split('(')[0]))
    q_min_round_up = np.ceil(min(q) * 10**2) / 10**2
    q_max_round_down = np.floor(max(q) * 10**2) / 10**2
    int_scaled = []
    # int_max = max(int_exp)
    # for i in range(0, len(int_exp)):
    #     int_scaled.append(int_exp[i] / int_max)
    # plt.plot(q, int_scaled)
    # plt.xlabel(r"$Q$ $[\mathrm{\AA^{-1}}]$")
    # plt.ylabel(r"$I$ $[\mathrm{a.u.}]$")
    # plt.show()
    # sys.exit()
    cif_data = [tt, q, int_exp, int_scaled, [q_min_round_up, q_max_round_down], probe]

    return cif_data
    # End of function.


def powdercif_pattern_write(cif_file_path, txt_path, data):
    tt = data[0]
    int_exp = data[2]
    txt = []
    for i in range(0, len(tt)):
        if len(str(tt[i])) <= 7:
            txt.append(str(tt[i]) + '\t'*2 + str(int_exp[i]) + '\n')
        elif len(str(tt[i])) > 7:
            txt.append(str(tt[i]) + '\t' + str(int_exp[i]) + '\n')
    file_name = cif_file_path.stem
    txt_file_path = txt_path / file_name
    with open(str(txt_file_path) + '.txt', 'w') as output_file:
        output_file.writelines(txt)
    output_file.close()

    return None
    # End of function.


def user_input_read(user_input_file, wavelength):
    with open(user_input_file) as input_file:
        lines = input_file.readlines()
    input_file.close()
    tt, q, int_exp = [], [], []
    for line in lines:
        tt.append(float(line.split()[0]))
        q.append(float(4 * np.pi * np.sin((np.pi / 180) * float(line.split()[0]) / 2) / wavelength))
        int_exp.append(float(line.split()[1]))
    q_min_round_up = np.ceil(min(q) * 10**2) / 10**2
    q_max_round_down = np.floor(max(q) * 10**2) / 10**2
    int_scaled = []
    # int_max = max(int_exp)
    # for i in range(0, len(int_exp)):
    #     int_scaled.append(int_exp[i] / int_max)
    data_user = [tt, q, int_exp, int_scaled, [q_min_round_up, q_max_round_down]]

    return data_user
    # End of function.


def rank_write(cif_rank_pearson_list, txt_path):
    txt = []
    print('-'*80)
    print('Rank\tFile\t\t\t\t\t\t\t\t\t\tPearson coefficient')
    txt.append('Rank\tFile\t\t\t\t\t\t\t\t\t\tPearson coefficient\n')
    for i in range(0, 10):
        # print(len(str(cif_rank_pearson_list[i][0])))
        if len(cif_rank_pearson_list[i][0]) < 36:
            print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t\t\t'
                  + "{:.4f}".format(cif_rank_pearson_list[i][1]))
            txt.append(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t\t\t'
                       + "{:.4f}".format(cif_rank_pearson_list[i][1]) + '\n')
        if 36 <= len(cif_rank_pearson_list[i][0]) < 40:
            print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t\t'
                  + "{:.4f}".format(cif_rank_pearson_list[i][1]))
            txt.append(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t\t'
                       + "{:.4f}".format(cif_rank_pearson_list[i][1]) + '\n')
        elif len(cif_rank_pearson_list[i][0]) >= 40:
            print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t'
                  + "{:.4f}".format(cif_rank_pearson_list[i][1]))
            txt.append(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]) + '\t'
                       + "{:.4f}".format(cif_rank_pearson_list[i][1]) + '\n')
    print('-'*80)

    # print('Rank\tIUCr CIF Name\t\t\t\t\tPearson coefficient')
    # txt.append('Rank\tIUCr CIF Name\t\t\t\t\tPearson coefficient')
    # for i in range(0, 10):
    #     if len(cif_rank_pearson_list[i][0]) >= 24:
    #         print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]).split('.')[0] + '\t' + "{:.4f}".format(cif_rank_pearson_list[i][1]))
    #         txt.append(str(i + 1) + '\t' + str(cif_rank_pearson_list[i][0]).split('.')[0] + '\t' + "{:.4f}".format(
    #             cif_rank_pearson_list[i][1]) + '\n')
    #     elif len(cif_rank_pearson_list[i][0]) < 24:
    #         print(str(i + 1) + '\t\t' + str(cif_rank_pearson_list[i][0]).split('.')[0] + '\t'*2 + "{:.4f}".format(cif_rank_pearson_list[i][1]))
    #         txt.append(str(i + 1) + '\t' + str(cif_rank_pearson_list[i][0]).split('.')[0] + '\t'*2 + "{:.4f}".format(cif_rank_pearson_list[i][1]) + '\n')
    # print('-' * 80)

    with open(txt_path / 'rank.txt', 'w') as output_file:
        output_file.writelines(txt)
    output_file.close()

    return None
    # End of function.
