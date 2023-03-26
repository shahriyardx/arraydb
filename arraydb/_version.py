from collections import namedtuple

__version__ = "0.1.1"
__release__ = "stable"

_VersionInfo = namedtuple("VersionInfo", "major minor macro release")


def conv(v):
    try:
        return int(v)
    except ValueError:
        return v


version_info = _VersionInfo(*map(conv, f"{__version__}.{__release__}".split(".")))
