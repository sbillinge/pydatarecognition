from pathlib import Path

from cifplotting.io import cif_read


def test_cif_read():
    expected = something
    test_cif = Path('../inputs/test_cif.cif')
    actual = cif_read(test_cif)
    assert actual == expected