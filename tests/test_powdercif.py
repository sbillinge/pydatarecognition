import numpy
import pytest

from pydatarecognition.powdercif import PowderCif
import sympy.physics.units as spu

rw = [
    (
        (("aa4589", "invang", [1., 2., 3.], [23, 24., 25.]),
         {"wavelength": 1.54, "wavel_units": "angs"}),
        (0.154, "aa4589", numpy.array([10., 20., 30.]),
         numpy.array([0.24571629, 0.49524281, 0.75295707]),
         numpy.array([23, 24., 25.]))
    )
]


@pytest.mark.parametrize("rw", rw)
def test_powdercif_constructor(rw):
    print(rw[1])
    pc = PowderCif(*rw[0][0], **rw[0][1])
    assert pc.wavelength == rw[1][0]
    assert pc.iucrid == rw[1][1]
    assert pc.q.all() == rw[1][2].all()
    assert pc.ttheta.all() == rw[1][3].all()
    assert pc.intensity.all() == rw[1][4].all()
