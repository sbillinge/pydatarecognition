from pathlib import Path
from testfixtures import TempDirectory
from cifplotting.io import cif_read


def test_cif_read():
    with TempDirectory() as d:
        d.write('test_cif.cif',
                b'_diffrn_radiation_probe                neutrons\n_diffrn_radiation_wavelength            1.5482')
        temp_dir = Path(d.path)
        test_cif_path = temp_dir / 'test_cif.cif'
        actual = cif_read(test_cif_path)
    expected = {"_diffrn_radiation_wavelength": 1.5482, 
                "_diffrn_radiation_probe": "neutrons"}
    assert actual == expected