"""linfo - Linux distro information CLI.

This package follows a src/ layout as recommended in Arjan Codes' design guidance
for better separation of source code from other project files and to avoid
import shadowing issues during development.

Author: Roy Jensen <g04t@t3chg04t.wtf>
ORCID: https://orcid.org/0009-0001-2601-8028
"""

__version__ = "0.6.0"
__author__ = "Roy Jensen"
__email__ = "g04t@t3chg04t.wtf"
__orcid__ = "https://orcid.org/0009-0001-2601-8028"

from linfo.models import Distro
from linfo.renderer import DistroRenderer
from linfo.data import get_distro_data, normalize_distro_name

__all__ = [
    "Distro",
    "DistroRenderer",
    "get_distro_data",
    "normalize_distro_name",
    "__version__",
]
