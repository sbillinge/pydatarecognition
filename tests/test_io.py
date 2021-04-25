from pathlib import Path
from testfixtures import TempDirectory

from cifplotting.io import cif_read
from tests.inputs.test_cif_contents import cif_contents_string


def test_cif_read():
    cif_bitstream = bytearray(cif_contents_string, 'utf8')
    with TempDirectory() as d:
        d.write('test_cif.cif',
                cif_bitstream)
        temp_dir = Path(d.path)
        test_cif_path = temp_dir / 'test_cif.cif'
        actual = cif_read(test_cif_path)
    expected = {"_diffrn_radiation_wavelength": 1.5482, 
                "_diffrn_radiation_probe": "neutrons"}
    assert actual == expected
