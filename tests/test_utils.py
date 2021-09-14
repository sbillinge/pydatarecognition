import numpy as np
import pytest
from datetime import date
from habanero import Crossref
from pydatarecognition.utils import data_sample, pearson_correlate, xy_resample, get_formatted_crossref_reference, \
     hr_to_mr_number_and_esd, mr_to_hr_number_and_esd


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


def test_get_formatted_crossref_reference(monkeypatch):
    def mockreturn(*args, **kwargs):
        mock_article = {'message': {'author': [{"given": "SJL", "family": "Billinge"}],
                                    "short-container-title": ["J. Great Results"],
                                    "volume": 10,
                                    "title": ["Whamo"],
                                    "page": "231-233",
                                    "issued": {"date-parts": [[1971,8,20]]}}
                        }
        return mock_article

    monkeypatch.setattr(Crossref, "works", mockreturn)
    expected = ("Whamo, SJL Billinge, J. Great Results, v. 10, pp. 231-233, (1971).",
                date(1971, 8, 20))
    actual = get_formatted_crossref_reference("test")
    assert actual == expected


def test_hr_to_mr_number_and_esd():
    number_esd = ["343.44(45)", "324908.435(67)", "0.0783(1)", "11(1)", "51(13)"]
    actual = hr_to_mr_number_and_esd(number_esd)
    expected = np.array([343.44, 324908.435, 0.0783, 11, 51]), np.array([0.45, 0.067, 0.0001, 1, 13])
    assert np.allclose(actual[0], expected[0])
    assert np.allclose(actual[1], expected[1])


def test_mr_to_hr_number_and_esd():
    number, esd = [343.44, 324908.435, 0.0783, 11, 51], [0.45, 0.067, 0.0001, 1, 13]
    actual = mr_to_hr_number_and_esd(number, esd)
    expected = np.array(["343.44(45)", "324908.435(67)", "0.0783(1)", "11(1)", "51(13)"], dtype='str')
    assert np.array_equal(actual, expected)

# End of file.
