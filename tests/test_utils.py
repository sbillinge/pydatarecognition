# from pathlib import Path
# from testfixtures import TempDirectory
import numpy as np
from pydatarecognition.utils import data_sample
from pydatarecognition.utils import pearson_correlate
# from tests.inputs.test_cif_data import cif_data_list
# from tests.inputs.test_data_sample import test_data_sample_list_array

# def test_data_sample():
#     test_cif_data = [[10.0413, 10.0913, 10.1413, 10.1913],
#                      [0.7103365913280906, 0.713864540690652, 0.7173923541434815, 0.720920031014933],
#                      [2037.0, 2212.0, 2155.0, 2130.0],
#                      [],
#                      [0.72, 7.83],
#                      'neutrons']
#     actual = data_sample(test_cif_data)
#     expected = [np.array([0.72, 0.725, 0.73, 0.735]),
#                 np.array([2154.6302703494507, 1964.404846041446, 2184.9624734543636, 2089.112002617548])]
#     assert actual == expected

# def test_pearson_correlate():
#     test_sampled_data = [np.array([0.72, 0.725, 0.73, 0.735]),
#                       np.array([2154.6302703494507, 1964.404846041446, 2184.9624734543636, 2089.112002617548])]
#     actual = -1 <= pearson_correlate(test_sampled_data) <= 1
#     expected = True
#     assert actual == expected
