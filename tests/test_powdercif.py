import numpy
import pytest

from pydatarecognition.powdercif import PowderCif, LENGTHS, INVS


rw = [
    (
        (("aa4589", "invang", [1., 2., 3.], [23, 24., 25.]),
         {"wavelength": 1.54, "wavel_units": "angs"}),
        (0.154, "aa4589", numpy.array([10., 20., 30.]),
         numpy.array([0.24571629, 0.49524281, 0.75295707]),
         numpy.array([23, 24., 25.]))
    ),
    (    (("aa4589", "invnm", [1., 2., 3.], [23, 24., 25.]),
         {"wavelength": .154, "wavel_units": "nm"}),
        (0.154, "aa4589", numpy.array([1., 2., 3.]),
         numpy.array([0.02451047, 0.04902463, 0.07354616]),
         numpy.array([23, 24., 25.]))
         ),
    (
        (("aa4589", "rad", [1., 2., 3.], [23, 24., 25.]),
         {"wavelength": 1.54, "wavel_units": "angs"}),
        (0.154, "aa4589", numpy.array([39.12103247, 68.66387179, 81.39540057]),
         numpy.array([1., 2., 3.]),
         numpy.array([23, 24., 25.]))
    ),
    (
        (("aa4589", "deg", [1., 2., 3.], [23, 24., 25.]),
         {"wavelength": 1.54, "wavel_units": "angs"}),
        (0.154, "aa4589", numpy.array([0.71208363, 1.42411304, 2.13603399]),
         numpy.array([0.01745329, 0.03490659, 0.05235988]),
         numpy.array([23, 24., 25.]))
    )
]


@pytest.mark.parametrize("rw", rw)
def test_powdercif_constructor(rw):
    print(rw[1])
    pc = PowderCif(*rw[0][0], **rw[0][1])
    assert pc.wavelength == rw[1][0]
    assert pc.iucrid == rw[1][1]
    assert numpy.allclose(pc.q, rw[1][2])
    assert numpy.allclose(pc.ttheta, rw[1][3])
    assert numpy.allclose(pc.intensity, rw[1][4])

    with pytest.raises(RuntimeError) as erc:
        pc = PowderCif("aa4589", "bad", [1., 2., 3.], [23, 24., 25.])
        assert f"ERROR: Do not recognize units.  Select from {*LENGTHS,}" == erc.value
    with pytest.raises(RuntimeError) as erc:
        pc = PowderCif("aa4589", "invang", [1., 2., 3.], [23, 24., 25.],
                       wavelength=0.154, wavel_units="bad")
        assert f"ERROR: Do not recognize units.  Select from {*INVS,}" == erc.value
    with pytest.raises(RuntimeError):
        pc = PowderCif("aa4589", "invang", [1., 2., 3.], [23, 24., 25.],
                       wavelength=0.154)
        assert f"ERROR: Wavelength supplied without units. Wavelength units are required from {*LENGTHS,}." == erc.value
