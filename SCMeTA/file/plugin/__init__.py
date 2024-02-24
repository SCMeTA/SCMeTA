from SCMeTA.config import SYSTEM

if SYSTEM == 'Darwin':
    from pyRawTools import MSLoader as RawFileReader
else:
    from .thermo_dotnet import MSLoader as RawFileReader


__all__ = ["RawFileReader"]


