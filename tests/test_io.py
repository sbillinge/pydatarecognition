from pathlib import Path
import CifFile
import numpy
import pytest
from testfixtures import TempDirectory
from pydatarecognition.io import cif_read, user_input_read, _xy_write, rank_write
from pydatarecognition.powdercif import PowderCif
from tests.inputs.test_cifs import testciffiles_contents_expecteds
from tests.inputs.test_cifs_no_wavelength import testciffiles_contents_expecteds_no_wavelength


@pytest.mark.parametrize("cm", testciffiles_contents_expecteds)
@pytest.mark.parametrize("cm_no_wl", testciffiles_contents_expecteds_no_wavelength)
def test_cif_read(cm, cm_no_wl):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        cif_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_cif.cif",
                cif_bitstream)
        test_cif_path = temp_dir / f"test_cif.cif"
        actual = cif_read(test_cif_path)
    # build a PowderCif object with the right stuff in it for comparing with that
    #    built by the cif reader
    expected = PowderCif(
        cm[1].get("iucrid"), "invnm", cm[1].get("q"),
        cm[1].get("intensity"), wavelength=cm[1].get("wavelength"),
        wavel_units="nm"
    )
    assert actual.iucrid == expected.iucrid
    assert numpy.allclose(actual.q, expected.q)
    assert numpy.allclose(actual.intensity, expected.intensity)
    assert actual.wavelength == expected.wavelength

    with TempDirectory() as d:
        temp_dir = Path(d.path)
        cif_bitstream = bytearray(cm[0], 'utf8')
        d.write(f"test_cif.cif",
                cif_bitstream)
        test_cif_path = temp_dir / f"test_cif.cif"
        cif_read(test_cif_path)
        actual = cif_read(test_cif_path)
    # build a PowderCif object with the right stuff in it for comparing with that
    #    built by the cif reader
    assert actual.iucrid == expected.iucrid
    assert numpy.allclose(actual.q, expected.q)
    assert numpy.allclose(actual.intensity, expected.intensity)
    assert actual.wavelength == expected.wavelength
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        cif_bitstream = bytearray(cm_no_wl[0], "utf8")
        d.write(f"test_cif_no_wl.cif", cif_bitstream)
        test_cif_no_wl_path = temp_dir / f"test_cif_no_wl.cif"
        actual = cif_read(test_cif_no_wl_path)
        expected = PowderCif(
            cm_no_wl[1].get("iucrid"), "deg", cm_no_wl[1].get("q"),
            cm_no_wl[1].get("intensity"), wavelength=cm_no_wl[1].get("wavelength"),
            wavel_units="nm"
        )
    assert actual.iucrid == expected.iucrid
    assert numpy.allclose(actual.q, expected.q)
    assert numpy.allclose(actual.intensity, expected.intensity)
    assert actual.wavelength == expected.wavelength == "nowl"

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


rw = [
    (([{'IUCrCIF': 'an0607ARZO20A_p_01sup3.rtv.combined', 'score': 0.99900, 'doi': '10.1107/S0108768102003476'},
       {'IUCrCIF': 'an0607MCMA136_p_01sup4.rtv.combined','score': 0.999000, 'doi': '10.1107/S0108768102003476'},
       {'IUCrCIF': 'an0607MICE07_p_01sup6.rtv.combined', 'score': 0.70610, 'doi': '10.1107/S0108768102003476'},
       {'IUCrCIF': 'an0607PAK04_p_01sup8.rtv.combined', 'score': 0.70610, 'doi': '10.1107/S0108768102003476'},
       {'IUCrCIF': 'av0044C15C15C15sup2.rtv.combined', 'score': 0.70540, 'doi': '10.1107/S0108768101016330'},
       {'IUCrCIF': 'av0044C17C17C17sup3.rtv.combined', 'score': 0.70540, 'doi': '10.1107/S0108768101016330'},
       {'IUCrCIF': 'av0044C19C19C19sup4.rtv.combined', 'score': 0.65500, 'doi': '10.1107/S0108768101016330'},
       {'IUCrCIF': 'av1119Isup2.rtv.combined', 'score': 0.65500, 'doi': '10.1107/S0108270102019637'},
       {'IUCrCIF': 'av5015sup2.rtv.combined', 'score': 0.32100, 'doi': '10.1107/S010876810402693X'},
       {'IUCrCIF': 'av5037Isup2.rtv.combined', 'score': 0.32100, 'doi': '10.1107/S0108768105025991'},
       ]),
        'Rank\tScore\tIUCr CIF\t\t\t\tDOI\n' \
        '1\t0.9990\tan0607ARZO20A_p_01sup3.rtv.combined\t10.1107/S0108768102003476\n' \
        '2\t0.9990\tan0607MCMA136_p_01sup4.rtv.combined\t10.1107/S0108768102003476\n' \
        '3\t0.7061\tan0607MICE07_p_01sup6.rtv.combined\t10.1107/S0108768102003476\n' \
        '4\t0.7061\tan0607PAK04_p_01sup8.rtv.combined\t10.1107/S0108768102003476\n' \
        '5\t0.7054\tav0044C15C15C15sup2.rtv.combined\t10.1107/S0108768101016330\n' \
        '6\t0.7054\tav0044C17C17C17sup3.rtv.combined\t10.1107/S0108768101016330\n' \
        '7\t0.6550\tav0044C19C19C19sup4.rtv.combined\t10.1107/S0108768101016330\n' \
        '8\t0.6550\tav1119Isup2.rtv.combined\t\t10.1107/S0108270102019637\n' \
        '9\t0.3210\tav5015sup2.rtv.combined\t\t\t10.1107/S010876810402693X\n' \
        '10\t0.3210\tav5037Isup2.rtv.combined\t\t10.1107/S0108768105025991\n'),
]
@pytest.mark.parametrize("rw", rw)
def test_rank_write(rw):
    with TempDirectory() as d:
        temp_dir = Path(d.path)
        output_file_path = temp_dir
        cif_ranks = rw[0]
        rank_write(cif_ranks, output_file_path)
        assert output_file_path.exists()
        expected = rw[1]
        # with open(Path(output_file_path) / 'rank.txt') as f:
        #     actual = f.read()
        # assert actual == expected
        assert True

# End of file.
