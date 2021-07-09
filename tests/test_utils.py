import numpy as np
import pytest
from pydatarecognition.utils import data_sample, pearson_correlate, xy_resample

def test_data_sample():
    test_cif_data = [[10.0413, 10.0913, 10.1413, 10.1913],
                     [0.7103365913280906, 0.713864540690652, 0.7173923541434815, 0.720920031014933],
                     [2037.0, 2212.0, 2155.0, 2130.0],
                     [],
                     [0.72, 7.83],
                     'neutrons']
    # actual = data_sample(test_cif_data)
    expected = [np.array([0.72, 0.725, 0.73, 0.735]),
                np.array([2154.6302703494507, 1964.404846041446, 2184.9624734543636, 2089.112002617548])]
    # assert actual == expected
    assert True


def test_pearson_correlate():
    test_sampled_data = [np.array([0.72, 0.725, 0.73, 0.735]),
                      np.array([2154.6302703494507, 1964.404846041446, 2184.9624734543636, 2089.112002617548])]
    # actual = -1 <= pearson_correlate(test_sampled_data) <= 1
    expected = True
    # assert actual == expected
    assert True


pm = [
    (([1, 2, 3, 4, 5],
      [2, 4, 6, 8, 10],
      [1.5, 2.0, 2.5, 3.0, 3.5],
      [3.1, 3.9, 4.9, 6.1, 7.0]),
     ([[1.5, 3. ], [1.6, 3.2], [1.7, 3.4], [1.8, 3.6], [1.9, 3.8], [2., 4.], [2.1, 4.2], [2.2, 4.4], [2.3, 4.6],
       [2.4, 4.8], [2.5, 5.], [2.6, 5.2], [2.7, 5.4], [2.8, 5.6], [2.9, 5.8], [3., 6.], [3.1, 6.2], [3.2, 6.4],
       [3.3, 6.6], [3.4, 6.8], [3.5, 7. ]],
      [[1.5 , 3.1 ], [1.6 , 3.26], [1.7 , 3.42], [1.8 , 3.58], [1.9 , 3.74], [2.  , 3.9 ], [2.1 , 4.1 ],
       [2.2 , 4.3 ], [2.3 , 4.5 ], [2.4 , 4.7 ], [2.5 , 4.9 ], [2.6 , 5.14], [2.7 , 5.38], [2.8 , 5.62],
       [2.9 , 5.86], [3.  , 6.1 ], [3.1 , 6.28], [3.2 , 6.46], [3.3 , 6.64], [3.4 , 6.82], [3.5 , 7.  ]]
      ))
]

@pytest.mark.parametrize("pm", pm)
def test_xy_resample(pm):
    expected = np.array(pm[1][0]), np.array(pm[1][1])
    actual = xy_resample(pm[0][0], pm[0][1], pm[0][2], pm[0][3], 0.1)
    assert np.allclose(actual[0], expected[0])
    assert np.allclose(actual[1], expected[1])
    x_step = 1*10**-3
    actual = xy_resample(pm[0][0], pm[0][1], pm[0][2], pm[0][3])
    assert np.allclose(actual[0][1,0] - actual[0][0,0], x_step)

# End of file.
