import os
import sys
import numpy as np
import pandas as pd
import tqdm

from pythonnet import load
load("coreclr")

import clr
from System import String

dir_path = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.join(dir_path, "dll"))


clr.AddReference("ThermoFisher.CommonCore.Data")
clr.AddReference("ThermoFisher.CommonCore.RawFileReader")
import ThermoFisher
from ThermoFisher.CommonCore.Data.Interfaces import IScanEventBase, IScanEvent

'''
rawFile = ThermoFisher.CommonCore.RawFileReader.RawFileReaderAdapter.FileFactory(raw_filename)
var scanStatistics = rawFile.GetScanStatsForScanNumber(1);
var seg = rawFile.GetSegmentedScanFromScanNumber(1, scanStatistics);
var scanEvent = rawFile.GetScanEventForScanNumber(1);
var trailerData = rawFile.GetTrailerExtraInformation(1);
'''


def DotNetArrayToNPArray(arr, dtype):
    return np.array(list(arr), dtype=dtype)


def NpArrayToDataFrame(arr, columns: list[str]):
    return pd.DataFrame(arr.transpose(), columns=columns)


'''
APIs are similar to pymsfilereader(https://github.com/frallain/pymsfilereader), but some APIs have not be implemented yet."
'''


class RawFileReader(object):
    # static class members
    sampleType = {0: 'Unknown',
                  1: 'Blank',
                  2: 'QC',
                  3: 'Standard Clear (None)',
                  4: 'Standard Update (None)',
                  5: 'Standard Bracket (Open)',
                  6: 'Standard Bracket Start (multiple brackets)',
                  7: 'Standard Bracket End (multiple brackets)'}

    controllerType = {-1: 'No device',
                      0: 'MS',
                      1: 'Analog',
                      2: 'A/D card',
                      3: 'PDA',
                      4: 'UV',
                      'No device': -1,
                      'MS': 0,
                      'Analog': 1,
                      'A/D card': 2,
                      'PDA': 3,
                      'UV': 4}

    massAnalyzerType = {'ITMS': 0,
                        'TQMS': 1,
                        'SQMS': 2,
                        'TOFMS': 3,
                        'FTMS': 4,
                        'Sector': 5,
                        0: 'ITMS',
                        1: 'TQMS',
                        2: 'SQMS',
                        3: 'TOFMS',
                        4: 'FTMS',
                        5: 'Sector'}
    activationType = {'CID': 0,
                      'MPD': 1,
                      'ECD': 2,
                      'PQD': 3,
                      'ETD': 4,
                      'HCD': 5,
                      'Any activation type': 6,
                      'SA': 7,
                      'PTR': 8,
                      'NETD': 9,
                      'NPTR': 10,
                      'UVPD': 11,
                      'ETHCD': 12,  # not Thermo's build-in activation types
                      'ETCID': 13,  # not Thermo's build-in activation types
                      0: 'CID',
                      1: 'MPD',
                      2: 'ECD',
                      3: 'PQD',
                      4: 'ETD',
                      5: 'HCD',
                      6: 'Any activation type',
                      7: 'SA',
                      8: 'PTR',
                      9: 'NETD',
                      10: 'NPTR',
                      11: 'UVPD',
                      12: 'ETHCD',  # not Thermo's build-in activation types
                      13: 'ETCID',  # not Thermo's build-in activation types
                      }

    detectorType = {'Valid': 0,
                    'Any': 1,
                    'NotValid': 2,
                    0: 'Valid',
                    1: 'Any',
                    2: 'NotValid',
                    }

    scanDataType = {'Centroid': 0,
                    'Profile': 1,
                    'Any': 2,
                    0: 'Centroid',
                    1: 'Profile',
                    2: 'Any',
                    }

    scanType = {'Full': 0,
                'Zoom': 1,
                'SIM': 2,
                'SRM': 3,
                'CRM': 4,
                'Any': 5,
                'Q1MS': 6,
                'Q3MS': 7,
                0: 'Full',
                1: 'SIM',
                2: 'Zoom',
                3: 'SRM',
                4: 'CRM',
                5: 'Any',
                6: 'Q1MS',
                7: 'Q3MS',
                }

    def __init__(self, filename, **kwargs):
        self.filename = os.path.abspath(filename)
        self.filename = os.path.normpath(self.filename)

        self.source = ThermoFisher.CommonCore.RawFileReader.RawFileReaderAdapter.FileFactory(self.filename)

        if not self.source.IsOpen:
            raise IOError(
                "RAWfile '{0}' could not be opened, is the file accessible ?".format(
                    self.filename))
        self.source.SelectInstrument(ThermoFisher.CommonCore.Data.Business.Device.MS, 1)

        self.StartTime = self.GetStartTime()
        self.EndTime = self.GetEndTime()
        self.FirstSpectrumNumber = self.GetFirstSpectrumNumber()
        self.LastSpectrumNumber = self.GetLastSpectrumNumber()
        self.LowMass = self.GetLowMass()
        self.HighMass = self.GetHighMass()
        self.MassResolution = self.GetMassResolution()
        self.NumSpectra = self.GetNumSpectra()

    def Close(self):
        """Closes a raw file and frees the associated memory."""
        self.source.Dispose()

    def GetFileName(self):
        """Returns the fully qualified path name of an open raw file."""
        return self.source.FileName

    def GetCreatorID(self):
        """Returns the creator ID. The creator ID is the
        logon name of the user when the raw file was acquired."""
        return self.source.CreatorId

    def GetCreationDate(self):
        """Returns the file creation date in DATE format."""
        # https://msdn.microsoft.com/en-us/library/82ab7w69.aspx
        # The DATE type is implemented using an 8-byte floating-point number
        return self.source.CreationDate.ToOADate()

    def IsError(self):
        """Returns the error state flag of the raw file. A return value of TRUE indicates that an error has
        occurred. For information about the error, call the GetErrorCode or GetErrorMessage
        functions."""
        return self.source.IsError

    def IsThereMSData(self):
        """This function checks to see if there is MS data in the raw file. A return value of TRUE means
        that the raw file contains MS data. You must open the raw file before performing this check."""
        return self.source.HasMsData

    def InAcquisition(self):
        """Returns the acquisition state flag of the raw file. A return value of TRUE indicates that the
        raw file is being acquired or that all open handles to the file during acquisition have not been
        closed."""
        return self.source.InAcquisition

    def RefreshViewOfFile(self):
        """Refreshes the view of a file currently being acquired. This function provides a more efficient
        mechanism for gaining access to new data in a raw file during acquisition without closing and
        reopening the raw file. This function has no effect with files that are not being acquired."""
        return self.source.RefreshViewOfFile

    def GetExpectedRunTime(self):
        """Gets the expected acquisition run time for the current controller. The actual acquisition may
        be longer or shorter than this value. This value is intended to allow displays to show the
        expected run time on chromatograms. To obtain an accurate run time value during or after
        acquisition, use the GetEndTime function."""
        return self.source.ExpectedRunTime

    def GetNumTrailerExtra(self):
        """Gets the trailer extra entries recorded for the current controller. Trailer extra entries are only
        supported for MS device controllers and are used to store instrument specific information for
        each scan if used."""
        return self.source.RunHeaderEx.TrailerExtraCount

    def GetMaxIntegratedIntensity(self):
        """Gets the highest integrated intensity of all the scans for the current controller. This value is
        only relevant to MS device controllers."""
        return self.source.RunHeaderEx.MaxIntegratedIntensity

    def GetMaxIntensity(self):
        """Gets the highest base peak of all the scans for the current controller. This value is only relevant
        to MS device controllers."""
        return self.source.RunHeaderEx.MaxIntensity

    def GetComment1(self):
        """Returns the first comment for the current controller. This value is typically only set for raw
        files converted from other file formats."""
        return self.source.RunHeaderEx.Comment1

    def GetComment2(self):
        """Returns the second comment for the current controller. This value is typically only set for raw
        files converted from other file formats."""
        return self.source.RunHeaderEx.Comment2

    def GetFilters(self):
        """Returns the list of unique scan filters for the raw file. This function is only supported for MS
        device controllers."""
        return list(self.source.GetFilters())

    # INSTRUMENT BEGIN
    def GetInstName(self):
        """Returns the instrument name, if available, for the current controller."""
        return String.Join(" -> ", self.source.GetAllInstrumentNamesFromInstrumentMethod())

    # INSTRUMENT END

    def GetScanEventStringForScanNum(self, scanNumber):
        """This function returns scan event information as a string for the specified scan number."""
        return self.source.GetScanEventStringForScanNumber(scanNumber)

    def GetNumberOfMassRangesFromScanNum(self, scanNumber):
        """This function gets the number of MassRange data items in the scan."""
        return IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).MassRangeCount

    def GetMassRangeFromScanNum(self, scanNumber, massRangeIndex):
        """This function retrieves information about the mass range data of a scan (high and low
        masses). You can find the count of mass ranges for the scan by calling
        GetNumberOfMassRangesFromScanNum()."""
        range = IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).GetMassRange(massRangeIndex)
        return range.Low, range.High

    def GetNumberOfSourceFragmentsFromScanNum(self, scanNumber):
        """This function gets the number of source fragments (or compensation voltages) in the scan."""
        return IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).SourceFragmentationInfoCount

    def GetSourceFragmentValueFromScanNum(self, scanNumber, sourceFragmentIndex):
        """This function retrieves information about one of the source fragment values of a scan. It is
        also the same value as the compensation voltage. You can find the count of source fragments
        for the scan by calling GetNumberOfSourceFragmentsFromScanNum ()."""
        return IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).GetSourceFragmentationInfo(
            sourceFragmentIndex)

    def GetIsolationWidthForScanNum(self, scanNumber, MSOrder=0):
        """This function returns the isolation width for the scan specified by scanNumber and the
        transition specified by MSOrder (0 for MS1?) from the scan event structure in the raw file."""
        return IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).GetIsolationWidth(MSOrder)

    def GetCollisionEnergyForScanNum(self, scanNumber, MSOrder=0):
        """This function returns the collision energy for the scan specified by scanNumber and the
        transition specified by MSOrder (0 for MS1?) from the scan event structure in the raw file. """
        return IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).GetEnergy(MSOrder)

    def GetActivationTypeForScanNum(self, scanNumber, MSOrder=0):
        """This function returns the activation type for the scan specified by scanNumber and the
        transition specified by MSOrder from the scan event structure in the RAW file.
        The value returned in the pnActivationType variable is one of the following:
        CID  0
        MPD 1
        ECD  2
        PQD 3
        ETD 4
        HCD 5
        Any activation type 6
        SA 7
        PTR 8
        NETD 9
        NPTR 10
        UVPD 11"""
        return RawFileReader.activationType[
            IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).GetActivation(MSOrder)]

    def GetMassAnalyzerTypeForScanNum(self, scanNumber):
        """This function returns the mass analyzer type for the scan specified by scanNumber from the
        scan event structure in the RAW file. The value of scanNumber must be within the range of
        scans or readings for the current controller. The range of scans or readings for the current
        controller may be obtained by calling GetFirstSpectrumNumber and
        GetLastSpectrumNumber.
        return RawFileReader.massAnalyzerType[IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).MassAnalyzer]"""

    def GetDetectorTypeForScanNum(self, scanNumber):
        """This function returns the detector type for the scan specified by scanNumber from the scan
        event structure in the RAW file."""
        return RawFileReader.detectorType[IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).Detector]

    def GetNumberOfMassCalibratorsFromScanNum(self, scanNumber):
        """This function gets the number of mass calibrators (each of which is a double) in the scan."""
        return IScanEvent(self.source.GetScanEventForScanNumber(scanNumber)).MassCalibratorCount

    def GetMassCalibrationValueFromScanNum(self, scanNumber, massCalibrationIndex):
        """This function retrieves information about one of the mass calibration data values of a scan.
        You can find the count of mass calibrations for the scan by calling
        GetNumberOfMassCalibratorsFromScanNum()."""
        return IScanEvent(self.source.GetScanEventForScanNumber(scanNumber)).GetMassCalibrator(massCalibrationIndex)

    def GetMassResolution(self):
        """Gets the mass resolution value recorded for the current controller. The value is returned as one
        half of the mass resolution. For example, a unit resolution controller returns a value of 0.5.
        This value is only relevant to scanning controllers such as MS."""
        return self.source.RunHeaderEx.MassResolution

    def GetLowMass(self):
        """Gets the lowest mass or wavelength recorded for the current controller. This value is only
        relevant to scanning devices such as MS or PDA."""
        return self.source.RunHeaderEx.LowMass

    def GetHighMass(self):
        """Gets the highest mass or wavelength recorded for the current controller. This value is only
        relevant to scanning devices such as MS or PDA."""
        return self.source.RunHeaderEx.HighMass

    def GetStartTime(self):
        """Gets the start time of the first scan or reading for the current controller. This value is typically
        close to zero unless the device method contains a start delay."""
        return self.source.RunHeaderEx.StartTime

    def GetEndTime(self):
        return self.source.RunHeaderEx.EndTime

    def GetNumSpectra(self):
        """Gets the number of spectra acquired by the current controller. For non-scanning devices like
        UV detectors, the number of readings per channel is returned."""
        return self.source.RunHeaderEx.SpectraCount

    def GetFirstSpectrumNumber(self):
        """Gets the first scan or reading number for the current controller. If data has been acquired, this
        value is always one."""
        return self.source.RunHeaderEx.FirstSpectrum

    def GetLastSpectrumNumber(self):
        """Gets the last scan or reading number for the current controller."""
        return self.source.RunHeaderEx.LastSpectrum

    def ScanNumFromRT(self, RT):
        """Returns the closest matching scan number that corresponds to RT for the current controller.
        For non-scanning devices, such as UV, the closest reading number is returned. The value of
        RT must be within the acquisition run time for the current controller. The acquisition run
        time for the current controller may be obtained by calling GetStartTime and GetEndTime."""
        return self.source.ScanNumberFromRetentionTime(RT)

    def ScanNumFromRTInSeconds(self, RTInSeconds):
        """Returns the closest matching scan number that corresponds to RT for the current controller.
        For non-scanning devices, such as UV, the closest reading number is returned. The value of
        RT must be within the acquisition run time for the current controller. The acquisition run
        time for the current controller may be obtained by calling GetStartTime and GetEndTime."""
        return self.ScanNumFromRT(RTInSeconds / 60)

    def RTFromScanNum(self, scanNumber):
        """Returns the closest matching run time or retention time that corresponds to scanNumber for
        the current controller. For non-scanning devices, such as UV, the scanNumber is the reading
        number."""
        return self.source.RetentionTimeFromScanNumber(scanNumber)

    def RTInSecondsFromScanNum(self, scanNumber):
        """Returns the closest matching run time or retention time that corresponds to scanNumber for
        the current controller. For non-scanning devices, such as UV, the scanNumber is the reading
        number."""
        return self.RTFromScanNum(scanNumber) * 60

    def IsProfileScanForScanNum(self, scanNumber):
        """Returns TRUE if the scan specified by scanNumber is a profile scan, FALSE if the scan is a
        centroid scan."""
        return not self.source.GetScanStatsForScanNumber(scanNumber).IsCentroidScan

    def IsCentroidScanForScanNum(self, scanNumber):
        """Returns TRUE if the scan specified by scanNumber is a centroid scan, FALSE if the scan is a
        profile scan."""
        return self.source.GetScanStatsForScanNumber(scanNumber).IsCentroidScan

    def GetMSOrderForScanNum(self, scanNumber):
        """This function returns the MS order for the scan specified by scanNumber from the scan
        event structure in the raw file.
        The value returned in the pnScanType variable is one of the following:
        Neutral gain -3
        Neutral loss -2
        Parent scan -1
        Any scan order 0
        MS  1
        MS2  2
        MS3  3
        MS4  4
        MS5  5
        MS6  6
        MS7  7
        MS8  8
        MS9  9
        """
        return IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).MSOrder

    def GetNumberOfMSOrdersFromScanNum(self, scanNumber):
        """This function gets the number of MS reaction data items in the scan event for the scan
        specified by scanNumber and the transition specified by MSOrder from the scan event
        structure in the raw file."""
        return IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).MassCount

    def GetPrecursorMassForScanNum(self, scanNumber, MSOrder=0):
        """This function returns the precursor mass for the scan specified by scanNumber and the
        transition specified by MSOrder (0 for precursor in MS1?) from the scan event structure in the RAW file."""
        return IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber)).GetReaction(MSOrder).PrecursorMass

    def GetPrecursorRangeForScanNum(self, scanNumber, MSOrder=0):
        """This function returns the first and last precursor mass values of the range and whether they are
        valid for the scan specified by scanNumber and the transition specified by MSOrder (0 for precursor in MS1?) from the scan event structure in the raw file."""
        scanEvent = IScanEventBase(self.source.GetScanEventForScanNumber(scanNumber))
        firstMass = scanEvent.GetFirstPrecursorMass(MSOrder)
        lastMass = scanEvent.GetLastPrecursorMass(MSOrder)
        return firstMass, lastMass

    def GetBasePeakForScanNum(self, scanNumber):
        """This function returns the base peak mass and intensity of mass spectrum."""
        stat = self.source.GetScanStatsForScanNumber(scanNumber)
        return stat.BasePeakMass, stat.BasePeakIntensity

    # "View/Scan header", lower part
    def GetTrailerExtraForScanNum(self, scanNumber):
        """Returns the recorded trailer extra entry labels and values for the current controller. This
        function is only valid for MS controllers.
        NOTE : XCALIBUR INTERFACE "View/Scan header", lower part
        """
        trailerData = self.source.GetTrailerExtraInformation(scanNumber)
        return dict(zip(trailerData.Labels, trailerData.Values))

    def GetProfileMassListFromScanNum(self, scanNumber):
        scanStatistics = self.source.GetScanStatsForScanNumber(scanNumber)
        segmentedScan = self.source.GetSegmentedScanFromScanNumber(scanNumber, scanStatistics)
        return np.array([DotNetArrayToNPArray(segmentedScan.Positions, float),
                         DotNetArrayToNPArray(segmentedScan.Intensities, float)])

    def GetCentroidMassListFromScanNum(self, scanNumber):
        scan = ThermoFisher.CommonCore.Data.Business.Scan.FromFile(self.source, scanNumber)
        scanStatistics = self.source.GetScanStatsForScanNumber(scanNumber)
        if scanStatistics.IsCentroidScan:
            segmentedScan = self.source.GetSegmentedScanFromScanNumber(scanNumber, scanStatistics)
            scan = pd.DataFrame(np.array([DotNetArrayToNPArray(segmentedScan.Positions, float),
                                          DotNetArrayToNPArray(segmentedScan.Intensities, float)]).transpose(),
                                columns=['Mass', 'Intensity'])
        elif scan.HasCentroidStream:
            stream = self.source.GetCentroidStream(scanNumber, False)
            scan = pd.DataFrame(np.array([DotNetArrayToNPArray(stream.Masses, float),
                                          DotNetArrayToNPArray(stream.Intensities, float)]).transpose(),
                                columns=['Mass', 'Intensity'])
        else:
            print("Profile scan {0} cannot be centroided!".format(scanNumber))
            segmentedScan = self.source.GetSegmentedScanFromScanNumber(scanNumber, scanStatistics)
            scan = pd.DataFrame(np.array([DotNetArrayToNPArray(segmentedScan.Positions, float),
                                          DotNetArrayToNPArray(segmentedScan.Intensities, float)]).transpose(),
                                columns=['Mass', 'Intensity'])
        scan["Scan"] = scanNumber
        return scan

    def GetFullScanMassList(self):
        """This function returns the mass list of full scan."""
        scan_range = range(self.FirstSpectrumNumber, self.LastSpectrumNumber + 1)
        scan_mass_list = [self.GetCentroidMassListFromScanNum(scan) for scan in tqdm.tqdm(scan_range)]
        return pd.concat(scan_mass_list).set_index("Scan")


