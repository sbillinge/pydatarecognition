from pathlib import Path

import CifFile
import numpy
import pytest
from testfixtures import TempDirectory

from pydatarecognition.io import cif_read, user_input_read, _xy_write
from tests.inputs.test_cifs import testciffiles_contents_expecteds


@pytest.mark.parametrize("cm", testciffiles_contents_expecteds)
def test_cif_read(cm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        cif_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_cif.cif",
                cif_bitstream)
        test_cif_path = temp_dir / f"test_cif.cif"
        actual = cif_read(test_cif_path)
    # build a CifFile object with the right stuff in it for comparing with that
    #    built by the cif reader
    expected = CifFile.CifFile()
    expected[cm[1].get('block_name')] = CifFile.CifBlock()
    cb = expected[cm[1].get('block_name')]
    for item in cm[1].get('block_items'):
        cb[item[0]] = item[1]
    for item in cm[1].get('loop_items'):
        cb.AddCifItem(([item['keys']], [item['values']]))
    assert actual[cm[1].get('block_name')].items() == expected[
        cm[1].get('block_name')].items()

testuserdata_contents_expecteds = [
    ("\
10.0413\t2037.0\n\
10.0913\t2212.0\n\
10.1413\t2155.0\n\
",
     numpy.array([[10.0413, 10.0913, 10.1413],
                  [2037.0, 2212.0, 2155.0]
                  ])
     ),
    ("\
10.0413\t2037.0\t55\n\
10.0913\t2212.0\t56\n\
10.1413\t2155.0\t57\n\
",
     numpy.array([[10.0413, 10.0913, 10.1413],
                  [2037.0, 2212.0, 2155.0],
                  [55, 56, 57]
                  ])
     )
]

@pytest.mark.parametrize("cm", testuserdata_contents_expecteds)
def test_user_input_read(cm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        userdata_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_userdata.txt",
                userdata_bitstream)
        test_userdata_path = temp_dir / f"test_userdata.txt"
        actual = user_input_read(test_userdata_path)

    expected = cm[1]
    numpy.testing.assert_array_equal(actual, expected)

pm = [
    (([1.0, 2, 3.2],
      [4, 5.5, 6]),
       '1.000000000000000000e+00\t4.000000000000000000e+00\n' \
       '2.000000000000000000e+00\t5.500000000000000000e+00\n' \
       '3.200000000000000178e+00\t6.000000000000000000e+00\n'),
]
@pytest.mark.parametrize("pm", pm)
def test__xy_write(pm):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        output_file_path = temp_dir / 'swallow.txt'
        x_array, y_array = numpy.array(pm[0][0]), numpy.array(pm[0][1])
        _xy_write(output_file_path, x_array, y_array)
        assert output_file_path.exists()
        expected = pm[1]
        with open(output_file_path) as f:
            actual = f.read()
        assert actual == expected
