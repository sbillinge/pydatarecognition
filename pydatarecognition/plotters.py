import sys
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from bg_mpl_stylesheet.bg_mpl_stylesheet import bg_mpl_style

def iq_plot(q, i):
    plt.style.use(bg_mpl_style)
    iq_plot = plt.figure()
    plt.plot(q, i, lw=0.5)
    plt.xlim(np.amin(q), np.amax(q))
    plt.xlabel(r'$Q$ $[\mathrm{\AA}^{-1}]$')
    plt.ylabel(r'$I$ $[\mathrm{counts}]$')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.tight_layout()
    plt.close()

    return iq_plot


def itt_plot(tt, i):
    plt.style.use(bg_mpl_style)
    itt_plot = plt.figure()
    plt.plot(tt, i, lw=0.5)
    plt.xlim(np.amin(tt), np.amax(tt))
    plt.xlabel(r'$2\theta$ $[^{\circ}]$')
    plt.ylabel(r'$I$ $[\mathrm{counts}]$')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.tight_layout()
    plt.close()

    return itt_plot


def iinvd_plot(inv_d, i):
    plt.style.use(bg_mpl_style)
    id_plot = plt.figure()
    plt.plot(inv_d, i, lw=0.5)
    plt.xlim(np.amin(inv_d), np.amax(inv_d))
    plt.xlabel(r'$d^{-1}$ $[\mathrm{\AA}^{-1}]$')
    plt.ylabel(r'$I$ $[\mathrm{counts}]$')
    plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
    plt.tight_layout()
    plt.close()

    return id_plot


def rank_plot(user_dict, cif_dict, cif_rank_coeff, output_dir, ranktype):
    x_user, y_user = user_dict["q"], user_dict["intensity"]
    x_min_user, x_max_user = np.amin(x_user), np.amax(x_user)
    y_min_user, y_max_user = np.amin(y_user), np.amax(y_user)
    x_range_user, y_range_user = x_max_user - x_min_user, y_max_user - y_min_user
    cifdata_q, cifdata_q_reg, cifdata_intensity, cifdata_intensity_resampled = [], [], [], []
    for i in range(0, 5):
        file = cif_rank_coeff[i][0]
        for key in cif_dict:
            if key == file:
                cifdata_q.append(cif_dict[key]['q'])
                cifdata_q_reg.append(cif_dict[key]['q_reg'])
                cifdata_intensity.append(cif_dict[key]['intensity'])
                cifdata_intensity_resampled.append(cif_dict[key]['intensity_resampled'])
    fontsize_labels, fontsize_ticks, fontsize_legend = 20, 16, 16
    legend_frame_lw = 2
    plt.style.use(bg_mpl_style)
    fig, axs = plt.subplots(6, 1, sharex='all', figsize=(8,10), dpi=300, gridspec_kw={'hspace':0})
    fig.add_subplot(111, frameon=False)
    plt.tick_params(labelcolor='none', which='both',
                    top=False, bottom=False, left=False, right=False)
    plt.xlabel(r"$Q$ $[\mathrm{nm}^{-1}]$", fontsize=fontsize_labels)
    plt.ylabel(r"$I$ $[\mathrm{arb.u.}]$", fontsize=fontsize_labels, labelpad=-10)
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    axs[0].plot(x_user, y_user, c=colors[0], label="User Data")
    # white_patch is a workaround, as handle was showed for .pdf files even when handlelength=0
    # whereas handlelength=0 worked for the .png files
    white_patch = mpatches.Patch(color='white', label=f"User data")
    legend = axs[0].legend(handles=[white_patch], loc="upper right", fontsize=fontsize_legend, handletextpad=0,
                           handlelength=0)
    legend.get_frame().set_linewidth(legend_frame_lw)
    axs[0].set_xlim(x_min_user, x_max_user)
    axs[0].set_ylim(y_min_user - 0.1*y_range_user, y_max_user + 0.1*y_range_user)
    axs[0].set_yticks([])
    for i in range(1, 6):
        x, y = cifdata_q_reg[i-1], cifdata_intensity_resampled[i-1]
        y_min, y_max = np.amin(y), np.amax(y)
        y_range = y_max - y_min
        axs[i].plot(x, y, c=colors[i], label=f"Rank {i}")
        axs[i].set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)
        axs[i].set_yticks([])
        white_patch = mpatches.Patch(color='white', label=f"Rank {i}")
        legend = axs[i].legend(handles=[white_patch], loc="upper right", fontsize=fontsize_legend, handletextpad=0,
                               handlelength=0)
        legend.get_frame().set_linewidth(legend_frame_lw)
    axs[-1].tick_params(axis="x", which="major", labelsize=fontsize_ticks)
    plt.savefig(output_dir / f'rank_plot_{ranktype}.png', bbox_inches='tight')
    plt.savefig(output_dir / f'rank_plot_{ranktype}.pdf', bbox_inches='tight')
    plt.close()

    return None
