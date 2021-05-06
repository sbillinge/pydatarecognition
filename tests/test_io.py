from pathlib import Path

import CifFile
import pytest
from testfixtures import TempDirectory

from cifplotting.io import cif_read
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
