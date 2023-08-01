from typing import Union, Optional, Dict, List

import astropy.units as u
import numpy as np

from .component import Component
from .parameter import Parameter
from .options import OPTIONS
from .utils import get_binned_dimension


class Model:
    """This class hold a model made of one or more components.

    Parameters
    ----------
    *components : list of Component
       The components of the model.

    Attributes
    ----------
    components : list of Component
       The components of the model.
    params : dict of Parameter
    free_params : dict of Parameter
    """

    def __init__(self, *components: List[Component]) -> None:
        """Constructor of the class"""
        if len(components) == 1 and isinstance(components[0], list):
            self.components = components[0]
        else:
            self.components = components

    @property
    def params(self) -> Dict[str, Parameter]:
        """Get the Model parameters.

        Parameters
        ----------
        free : bool, optional
            If True retrieve the free parameters of the models only.
            The default is False.

        Returns
        -------
        params : dict of Parameter
            Dictionary of the model's parameters.
        """
        params = {}
        for index, component in enumerate(self.components):
            for name, parameter in component.params.items():
                if parameter not in params.values():
                    params[f"c{index+1}_{component.shortname.replace(' ', '_')}_{name}"] = parameter
        return params

    @property
    def free_params(self) -> Dict[str, Parameter]:
        """Get the Model free paramters

        Returns
        -------
        free_parameters : dict of Parameter
            A Dictionary of the model's free parameters.
        """
        return {key: value for key, value in self.params.items() if value.free}

    def calculate_complex_visibility(self,
                                     wavelength: Optional[u.m] = None
                                     ) -> np.ndarray:
        """Compute and return the complex coherent flux for an array of u,v
        (and optionally wavelength and time) coordinates.

        Parameters
        ----------
        wavelength : astropy.units.m, optional
            Wavelength(s) in meter.

        Returns
        -------
        complex_visibility_function : numpy.ndarray
            The complex coherent flux. The same size as u & v.
        """
        res = complex(0, 0)
        for component in self.components:
            res += component.calculate_complex_visibility(wavelength)
        return res

    def calculate_image(self, dim: int, pixel_size: float,
                        wavelength: Optional[u.m] = None) -> np.ndarray:
        """Compute and return an image.

        The returned image as the x,y dimension dim in pixel with
        an angular pixel size pixel_size in rad. Image is returned as a numpy
        array unless the keyword fits is set to True. In that case the image is
        returned as an astropy.io.fits hdu.

        Parameters
        ----------
        dim : int
            Image x & y dimension in pixels.
        pixel_size : float
            Pixel angular size in mas.
        wavelength : u.m, optional
            Wavelength(s) in meter. The default is None.

        Returns
        -------
        numpy.ndarray
             A numpy 2D array (or 3D array if wl is given).
        """
        if OPTIONS["fourier.binning"] is not None:
            img_dim = get_binned_dimension(dim, OPTIONS["fourier.binning"])
        else:
            img_dim = dim
        image = np.zeros((img_dim, img_dim))
        for component in self.components:
            image += component.calculate_image(dim, pixel_size, wavelength)
        return image
