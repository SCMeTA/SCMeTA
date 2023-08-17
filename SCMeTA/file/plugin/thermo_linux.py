import clr

clr.AddReference('CyESI/file/plugin/dll/ThermoFisher.CommonCore.Data')
clr.AddReference('CyESI/file/plugin/dll/ThermoFisher.CommonCore.RawFileReader')
clr.AddReference('CyESI/file/plugin/dll/ThermoFisher.CommonCore.BackgroundSubtraction')
clr.AddReference('CyESI/file/plugin/dll/ThermoFisher.CommonCore.MassPrecisionEstimator')

from System import *
from System.Collections.Generic import *

from ThermoFisher.CommonCore.Data import ToleranceUnits
from ThermoFisher.CommonCore.Data import Extensions
from ThermoFisher.CommonCore.Data.Business import ChromatogramSignal, ChromatogramTraceSettings, DataUnits, Device, GenericDataTypes, SampleType, Scan, TraceType
from ThermoFisher.CommonCore.Data.FilterEnums import IonizationModeType, MSOrderType
from ThermoFisher.CommonCore.Data.Interfaces import IChromatogramSettings, IScanEventBase, IScanFilter, RawFileClassification
from ThermoFisher.CommonCore.MassPrecisionEstimator import PrecisionEstimate
from ThermoFisher.CommonCore.RawFileReader import RawFileReaderAdapter


class RawFileReader:
    def __init__(self, file_path: str):
        self.rawFile = self.open_file(file_path)
        self.first_scan = self.rawFile.RunHeaderEx.FirstSpectrum
        self.last_scan = self.rawFile.RunHeaderEx.LastSpectrum

    def open_file(self, file_path: str):
        rawFile = RawFileReaderAdapter.FileFactory(file_path)
        if not rawFile.IsOpen or rawFile.IsError:
            raise Exception("Error opening file.")
        return rawFile

    def ReadAllSpectra(rawFile, firstScanNumber, lastScanNumber, outputData):
        '''Read all spectra in the RAW file.

        Args:
            rawFile (IRawDataPlus): the raw file.
            firstScanNumber (int): the first scan number.
            lastScanNumber (int): the last scan number.
            outputData (bool): the output data flag.
        '''

        for scanNumber in range(firstScanNumber, lastScanNumber):
            try:
                # Get the scan filter for the spectrum
                scanFilter = IScanFilter(rawFile.GetFilterForScanNumber(firstScanNumber))

                if not scanFilter.ToString():
                    continue

                # Get the scan from the RAW file.  This method uses the Scan.FromFile method which returns a
                # Scan object that contains both the segmented and centroid (label) data from an FTMS scan
                # or just the segmented data in non-FTMS scans.  The GetSpectrum method demonstrates an
                # alternative method for reading scans.
                scan = Scan.FromFile(rawFile, scanNumber)

                # If that scan contains FTMS data then Centroid stream
                # will be populated so check to see if it is present.
                if scan.HasCentroidStream:
                    labelSize = scan.CentroidScan.Length
                else:
                    labelSize = 0

                # For non-FTMS data, the preferred data will be populated
                if scan.PreferredMasses is not None:
                    dataSize = scan.PreferredMasses.Length
                else:
                    dataSize = 0

                if outputData:
                    print('Spectrum {} - {}: normal {}, label {} points'.format(
                        scanNumber, scanFilter.ToString(), dataSize, labelSize))

            except Exception as ex:
                print('Error reading spectrum {} - {}'.format(scanNumber, str(ex)))
