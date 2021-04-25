def rank_plotter(user_data, sorted_zipped_list, data_dict, png_path):

    # Getting the top 5 ranked cif data from dictionary and appending to lists.
    q, int_exp = [], []
    for i in range(0, 5):
        file = sorted_zipped_list[i][0]
        for key in data_dict:
            if key == file:
                q.append(data_dict[key]['q'])
                int_exp.append(data_dict[key]['int_exp'])

    # Making figure using subplots.
    fig, axs = plt.subplots(6, 1, sharex=True, sharey=True, figsize=(8,4), dpi=300)

    # Setting x-limit.
    plt.xlim(min(user_data[1]), max(user_data[1]))

    # Setting y-ticks.
    plt.yticks([])

    # Add a big axis, hide frame.
    fig.add_subplot(111, frameon=False)

    # Hide ticks and tick labels on the big axis.
    plt.tick_params(labelcolor='none', which='both', top=False, bottom=False, left=False, right=False)

    # Setting axis labels.
    plt.xlabel(r"$Q$ $[\mathrm{\AA}^{-1}]$", fontsize=16)
    plt.ylabel(r"$I$ $[\mathrm{arb.u.}]$", fontsize=16, labelpad=-10)

    # plt.style.use(bg_mpl_style)
    colors = ["#0B3C5D", "#B82601", "#1c6b0a", "#328CC1", "#062F4F", "#D9B310",
              "#984B43", "#76323F", "#626E60", "#AB987A", "#C09F80"
              ]
    # Plotting user data topmost, and then ranked data in descending order.
    axs[0].plot(user_data[1], user_data[2], c=colors[0], lw=0.5)
    axs[0].text(0.89*max(user_data[1]), 0.7, 'User data')
    for i in range(1, 6):
        axs[i].plot(q[i-1], int_exp[i-1], c=colors[i], lw=0.5)
        axs[i].text(0.89*max(user_data[1]), 0.7, 'Rank: ' + str(i))
        # axs[i].set_xlim(min(user_data[1]), max(user_data[1]))

    # Saving figure as png file and closing plot.
    plt.savefig(png_path / 'rank_plot.png', bbox_inches='tight')
    plt.close()

    return None
    # End of function.
