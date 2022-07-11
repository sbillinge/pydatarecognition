import sys
import os
from pathlib import Path
import numpy as np
from skbeam.core.utils import twotheta_to_q
from pydatarecognition.cif_io import cif_read, rank_write, user_input_read, cif_read_ext, json_dump
from pydatarecognition.utils import xy_resample, correlate, get_iucr_doi, get_formatted_crossref_reference, rank_returns
from pydatarecognition.plotters import rank_plot
import argparse
import json

STEPSIZE_REGULAR_QGRID = 10**-3
RETURNS_MIN = 5
RETURNS_MAX = 20
SIMILARITY_THRESHOLD = 0.8

def main(verbose=True):
    XCHOICES = ['Q','twotheta','d']
    XUNITS = ["inv-A", "inv-nm", "deg", "rad", "A", "nm"]
    parser = argparse.ArgumentParser()
    parser.add_argument('-i','--input', required=True, help="path to the input data-file. Path can be relative from the"
                                             " current location, e.g., ./my_data_dir/my_data_filename.xy")
    parser.add_argument('--xquantity', required=True, choices=XCHOICES,
                        help=f"Independent variable quantity of the input data, from {*XCHOICES,}. By default units "
                             f"are {*XUNITS,}, respectively")
    parser.add_argument('--xunit', required=True, choices=XUNITS,
                        help=f"Units for the independent variable quantity of the input data if different from the "
                             f"default, from {*XUNITS,}")
    parser.add_argument('-o','--output', help="path to output files. Path can be relative from the current "
                                             "location, e.g., ./my_data_dir/")
    parser.add_argument('-w','--wavelength', help="wavelength of the radiation in angstrom units. Required if "
                                                  "xquantity is twotheta")
    parser.add_argument('--jsonify', action='store_true', help="dumps cifs into jsons")

    args = parser.parse_args()
    if args.xquantity == 'twotheta' and not args.wavelength:
        parser.error('--wavelength is required when --xquantity is twotheta')
    # These need to be inside main for this to run from an IDE like PyCharm
    # and still find the example files.
    parent_dir = Path.cwd()
    cif_dir = parent_dir / 'cifs'
    user_input = Path(args.input).resolve()
    ciffiles = cif_dir.glob("*.cif")
    # iucrid_doi_ref_file = cif_dir / 'iucrid_doi_ref_mapping.json'
    # with iucrid_doi_ref_file.open() as f:
    #     iucrid_doi_ref_dict = json.loads(f.read())
    if isinstance(args.output, type(None)):
        user_output = Path.cwd()
    else:
        user_output = Path(args.output).resolve()
    output_dir = user_output / '_output'
    folders = [output_dir]
    for folder in folders:
        if not folder.exists():
            folder.mkdir()
    frame_dashchars = '-'*80
    print(f'{frame_dashchars}\nInput data file: {user_input.name}\n'
          f'Wavelength: {args.wavelength} Å.\n{frame_dashchars}')
    userdata = user_input_read(user_input)
    if args.xquantity == 'twotheta':
        user_twotheta, user_intensity = userdata[0,:], userdata[1:,][0]
        user_q = twotheta_to_q(np.radians(user_twotheta), float(args.wavelength)/10)
        user_qmin, user_qmax = np.amin(user_q), np.amax(user_q)
    cifname_ranks, iucrid_ranks, corr_coeff_ranks, = [], [], []
    cif_dict = {}
    log = 'pydatarecognition log\nThe following files were skipped:\n'
    if args.jsonify:
        for ciffile in ciffiles:
            print(ciffile.name)
            ciffile_path = Path(ciffile)
            json_data = cif_read_ext(ciffile_path, 'json')
            pre = Path(ciffile).stem
            json_dump(json_data, str(output_dir/pre) + ".json")
    else:
        if verbose:
            print('Working with CIFs:')
        for ciffile in ciffiles:
            if verbose:
                print(f"\t{ciffile.name}")
            ciffile_path = Path(ciffile)
            pcd = cif_read(ciffile_path)
            try:
                data_resampled = xy_resample(user_q, user_intensity, pcd.q, pcd.intensity, STEPSIZE_REGULAR_QGRID)
                corr_coeff = correlate(data_resampled[0][:, 1], data_resampled[1][:, 1])
                cifname_ranks.append(ciffile.stem)
                iucrid_ranks.append(ciffile.stem[0:6])
                corr_coeff_ranks.append(corr_coeff)
                cif_dict[str(ciffile.stem)] = dict([
                            ('cifname', str(ciffile.stem)),
                            ('iucrid', str(ciffile.stem)[0:6]),
                            ('intensity', pcd.intensity),
                            ('q', pcd.q),
                            ('qmin', np.amin(pcd.q)),
                            ('qmax', np.amax(pcd.q)),
                            ('q_reg', data_resampled[1][:,0]),
                            ('intensity_resampled', data_resampled[1][:,1]),
                            ('corr_coeff', corr_coeff),
                        ])
            except (AttributeError, ValueError):
                if verbose:
                    print(f"{ciffile.name} was skipped.")
                log += f"{ciffile.name}\n"
        if verbose:
            print(f'Done working with cifs.\n{frame_dashchars}\nGetting references...')
        user_dict= dict([
            ('twotheta', user_twotheta),
            ('intensity', user_intensity),
            ('q', user_q),
            ('q_min', user_qmin),
            ('q_max', user_qmax),
        ])
        cif_rank_coeff_all = sorted(list(zip(cifname_ranks, corr_coeff_ranks)), key = lambda x: x[1], reverse=True)
        cif_rank_dict, paper_rank_dict = {}, {}
        for i in range(len(cif_rank_coeff_all)):
            cif_rank_dict[i] = cif_dict[cif_rank_coeff_all[i][0]]
        cif_returns = rank_returns(cif_rank_dict, RETURNS_MIN, RETURNS_MAX, SIMILARITY_THRESHOLD)
        for i in range(cif_returns):
            cif_rank_dict[i]['doi'] = get_iucr_doi(cif_rank_dict[i]['iucrid'])
            cif_rank_dict[i]['ref'] = get_formatted_crossref_reference(cif_rank_dict[i]['doi'])[0]
        cif_rank_coeff_requested = [[cif_rank_dict[i]['cifname'],
                                     cif_rank_dict[i]['corr_coeff'],
                                     cif_rank_dict[i]['doi'],
                                     cif_rank_dict[i]['ref'],
                                     ] for i in range(cif_returns)]
        paper_rank_counter, paper_all = 0, []
        for i in range(len(cif_rank_dict.keys())):
            if not cif_rank_dict[i]['iucrid'] in paper_all:
                paper_all.append(cif_rank_dict[i]['iucrid'])
                paper_rank_dict[paper_rank_counter] = cif_rank_dict[i]
                paper_rank_counter += 1
        paper_returns = rank_returns(paper_rank_dict, RETURNS_MIN, RETURNS_MAX, SIMILARITY_THRESHOLD)
        for i in range(paper_returns):
            if verbose:
                print(f"\t{paper_rank_dict[i]['cifname']}")
            paper_rank_dict[i]['doi'] = get_iucr_doi(paper_rank_dict[i]['iucrid'])
            paper_rank_dict[i]['ref'] = get_formatted_crossref_reference(paper_rank_dict[i]['doi'])[0]
        paper_rank_coeff_requested = [[paper_rank_dict[i]['cifname'],
                                       paper_rank_dict[i]['corr_coeff'],
                                       paper_rank_dict[i]['doi'],
                                       paper_rank_dict[i]['ref']]
                                      for i in range(paper_returns)]
        cif_ranks = [{'IUCrCIF':cif_rank_dict[i]['cifname'],
                      'score':cif_rank_dict[i]['corr_coeff'],
                      'doi':cif_rank_dict[i]['doi'],
                      'ref':cif_rank_dict[i]['ref'],
                      } for i in range(cif_returns)]
        ranks_papers = [{'IUCrCIF':paper_rank_dict[i]['cifname'],
                         'score':paper_rank_dict[i]['corr_coeff'],
                         'doi':paper_rank_dict[i]['doi'],
                         'ref':paper_rank_dict[i]['ref']
                         } for i in range(paper_returns)]
        if verbose:
            print(f'Done getting references...\n{frame_dashchars}')
        rank_txt = rank_write(cif_ranks, output_dir, "cifs")
        print(f'CIF ranking\n{frame_dashchars}\n{rank_txt}{frame_dashchars}')
        rank_papers_txt = rank_write(ranks_papers, output_dir, "papers")
        print(f'Paper ranking\n{frame_dashchars}\n{rank_papers_txt}{frame_dashchars}')
        if verbose:
            print('Plotting...\n\tCIF rank plot...')
        rank_plot(user_dict, cif_dict, cif_rank_coeff_requested, output_dir, "cifs")
        if verbose:
            print('\tPaper rank plot...')
        rank_plot(user_dict, cif_dict, paper_rank_coeff_requested, output_dir, "papers")
        if verbose:
            print('Done plotting.')
        print(f'{frame_dashchars}\n.txt, .pdf, and .png files have been saved to the output '
              f'diretory.')
        with open((output_dir / "pydatarecognition.log"), "w") as o:
            o.write(log)

    return None


if __name__ == "__main__":
    # in Pycharm (and probably other IDEs) it runs main in place, so if so
    # detect this and move to the examples folder where it can find the data
    cwd = Path().cwd()
    relpath = cwd / ".." / "docs" / "examples"
    if cwd.parent.name == "pydatarecognition" and cwd.parent.parent.name != "pydatarecognition":
        os.chdir(relpath)
    main()

# End of file.
