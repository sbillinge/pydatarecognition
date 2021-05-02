from pathlib import Path
from testfixtures import TempDirectory

from cifplotting.utils import data_sample
from tests.inputs.test_cif_data import cif_data_list
from tests.inputs.test_data_sample import test_data_sample_list_array

def test_data_sample():
    cif_data_list_bitstream = bytearray(cif_data_list, 'utf8')
    # with TempDirectory() as d:
    #     d.write('cif_data_list.py',
    #             cif_data_list_bitstream)
    #     temp_dir = Path(d.path)
    #     test_data_sample_path = temp_dir / 'cif_data_list.py'
    #     actual = data_sample(test_data_sample_path)
    actual = data_sample(cif_data_list)
    expected = test_data_sample_list_array
    assert actual == expected
