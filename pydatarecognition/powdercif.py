import numpy
import numpy as np
from skbeam.core.utils import twotheta_to_q, q_to_twotheta
import sympy.physics.units as spu


class PowderCif:
    '''
    Attributes
    ----------
    wavelength : float
        The wavelength of the radiation, in units of nanometers
    q : numpy array
        The independent variable in quantity Q (wavevector amplitude) in units of
        inverse nanometers
    ttheta : numpy array
        The independent variable in quantity two-theta (scattering angle) in units of
        radians
    intensity : numpy array
        The intensity values
    iucrid string
      the unique identifier of the paper that the is associated with the data
    '''
    def __init__(self, iucrid, x_units, x, y, wavelength=None, wavel_units=None):
        '''
        Powder Cif object constructor

        Parameters
        ----------
        iucrid string
          the unique identifier of the paper that the is associated with the data
        x_units string, from degrees, radians, invang, invnm
          the units of the x-array
        wavel_units string, from ang, angs, nm
          the units of the x-array
        x iterable
          the x-array.
        y iterable
          the intensity array
        wavelength float
          the wavelength.  Default is None
        '''
        ANGS = ["ang", "angs", "angstroms"]
        NMS = ["nm", "nanometers"]
        INVANGS = ["invang", "invangs", "inverse angstroms"]
        INVNMS = ["invnm", "inverse nanometers"]
        DEGS = ["deg", "degs", "degrees"]
        RADS = ["rad", "rads", "radians"]
        self.iucrid = iucrid
        if wavel_units.lower() in ANGS:
            self.wavelength = wavelength/10.
        elif wavel_units.lower() in NMS:
            self.wavelength = wavelength
        else:
            raise RuntimeError(f"ERROR: Do not recognize units.  Select from {ANGS.extend(NMS)}")

        if x_units.lower() in INVANGS:
            self.q = np.array(x)*10.
            self.ttheta = q_to_twotheta(self.q,self.wavelength)
        elif x_units.lower() in INVNMS:
            self.q = np.array(x)
            self.ttheta = q_to_twotheta(self.q,self.wavelength)
        elif x_units in DEGS:
            self.ttheta = np.array(np.radians(x))
            self.q = np.array(twotheta_to_q(self.ttheta, self.wavelength))
        elif x_units in RADS:
            self.ttheta = np.array(x)
            self.q = np.array(twotheta_to_q(self.ttheta, self.wavelength))
        else:
            raise RuntimeError(f"ERROR: Do not recognize units.  Select from {INVANGS.extend(INVNMS)}")
        self.intensity = np.array(y)
