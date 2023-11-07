import os
import logging

import pandas as pd

from SCMeTA.file import SCData
from SCMeTA.method import (
    filter_occ,
    to_mat,
    to_list,
    find_cell,
    merge_cell,
    noise_subtract,
    filter_assem,
    filter_mat,
    normalize,
    round_columns,
)
from SCMeTA.batch import combat_batch_correction
from SCMeTA.method.fill import fill_mat
from SCMeTA.file import load_data, load_from_database
from SCMeTA.config import PARAMETERS
from SCMeTA.accelerate import MultiProcessing

logger = logging.getLogger(__name__)


def _filter_occ(data: SCData, resolution: float, count: int):
    data.process = filter_occ(data.raw.copy(), resolution, count)


class Process:
    def __init__(
        self, ref_mz: float = 760.58, mz1: float = 760.58, mz2: float = 732.55
    ):
        self.data: dict[str, SCData] = {}

        self.__mz1: float = mz1
        self.__mz2: float = mz2
        self.ref_mz: float = ref_mz
        self.__dir = None
        self.__mp = MultiProcessing()
        pass

    def load(
        self,
        path: str,
        file_name: str | None = None,
        data_type: str = "thermo",
    ):
        """
        Add a file to the MSProcess
        Args:
            path: File path or directory path.
            file_name: File Name, cannot work if path is a directory.
            data_type: Data type, thermo_raw file / water wiff file / processed csv file are supported.
        """
        self.data.update(load_data(path, file_name, data_type))
        self.__dir = os.path.dirname(path)

    def load_database(self, file_id: int | list[int]):
        """
        Load data from database.
        Args:
            file_id: File ID in the database.

        Returns:

        """
        data = load_from_database(file_id)
        for key, value in data.items():
            self.data.update(load_data(value, key, "database"))

    def load_processed(self, path, file_name: str | None = None, file_type: str = "cell_mat"):
        """
        Load processed data.
        Args:
            path: File path or directory path.
            file_name: File Name, cannot work if path is a directory.
            file_type:

        Returns:

        """
        if os.path.isdir(path):
            for file in os.listdir(path):
                if file.endswith(".csv"):
                    file_name = os.path.basename(file).split(".")[0]
                    data = pd.read_csv(os.path.join(path, file), index_col=0)
                    data.columns = [float(i) for i in data.columns]
                    self.data[file_name] = SCData(name=file_name, cell_mat=data)
        else:
            data = pd.read_csv(path, index_col=0)
            data.columns = [float(i) for i in data.columns]
            self.data[file_name] = SCData(name=file_name, cell_mat=data)

    def filter_occ(
        self,
        count: int = PARAMETERS.count,
        resolution: float = PARAMETERS.resolution,
        file_name: str | None = None,
    ):
        """
        Filter out the data with low occurrence
        Args:
            count: Minimum occurrence of the data, default 10
            resolution: Resolution of the data, default 0.01
            file_name: File name, if None, all files will be processed.
        """
        if file_name is None:
            # self.__mp.run(self.data, _filter_occ, resolution, count)
            for ms_data in self.data.values():
                ms_data.process = filter_occ(ms_data.raw.copy(), resolution, count)
        else:
            self.data[file_name].process = filter_occ(
                self.data[file_name].raw.copy(), resolution, count
            )
        logger.info("Filter out the data with low occurrence.")

    def gen_mat(self, file_name: str | None = None):
        if file_name is None:
            for ms_data in self.data.values():
                ms_data.mat = to_mat(ms_data.process)
        else:
            self.data[file_name].mat = to_mat(self.data[file_name].process)

    def denoise(self, max_ratio: float = PARAMETERS.maxratio, file_name: str | None = None):
        """
        Find cell and subtract noise.
        Args:
            max_ratio: If the ratio of the max value to the second max value is larger than this value, the cell will be
            file_name: File name, if None, all files will be processed.
        """
        if file_name is None:
            for ms_data in self.data.values():
                ms_data.cell_pos = find_cell(
                    ms_data.mat, self.ref_mz, max_ratio=max_ratio
                )
                ms_data.mat = noise_subtract(ms_data.mat, ms_data.cell_pos)
        else:
            ms_data = self.data[file_name]
            ms_data.cell_pos = find_cell(
                ms_data.mat, self.ref_mz, max_ratio=max_ratio
            )
            ms_data.mat = noise_subtract(ms_data.mat, ms_data.cell_pos)
            self.data[file_name] = ms_data
        logger.info("Noise subtracted!")

    def merge_cell(self, adjacent: int = PARAMETERS.adjacent, file_name: str | None = None):
        """
        Combine the adjacent cells
        Args:
            adjacent: Number of adjacent cells to be combined, default 3.
            If number is larger than the number of cells, the data will be dropped.
            file_name: File name, if None, all files will be processed.
        """
        if file_name is None:
            for ms_data in self.data.values():
                ms_data.cell_mat = merge_cell(
                    ms_data.mat, ms_data.cell_pos, adjacent=adjacent
                )
        else:
            self.data[file_name].cell_mat = merge_cell(
                self.data[file_name].mat,
                self.data[file_name].cell_pos,
                adjacent=adjacent,
            )

    def filter_assem(self, snr: float = PARAMETERS.snr, file_name: str | None = None):
        """
        Filter out the data with Intensity/Noise < snr
        Args:
            snr: Minimum SNR of the data, default 3.0
            file_name: File name, if None, all files will be processed.
        """
        if file_name is None:
            for ms_data in self.data.values():
                ms_data.cell_mat = filter_assem(
                    ms_data.mat, ms_data.cell_mat, ms_data.cell_pos, snr
                )
        else:
            self.data[file_name].cell_mat = filter_assem(
                self.data[file_name].mat,
                self.data[file_name].cell_mat,
                self.data[file_name].cell_pos,
                snr,
            )
        logger.info("Filter out the data with low SNR.")

    def round_mat(
        self, resolution: float = PARAMETERS.resolution, file_name: str | None = None
    ):
        if file_name is None:
            for ms_data in self.data.values():
                ms_data.mat = round_columns(ms_data.mat, resolution)
        else:
            self.data[file_name].mat = round_columns(
                self.data[file_name].mat, resolution
            )

    def gen_process(self, file_name: str | None = None):
        if file_name is None:
            for ms_data in self.data.values():
                ms_data.process = to_list(ms_data.cell_mat, ms_data.cell_pos)
        else:
            self.data[file_name].process = to_list(
                self.data[file_name].cell_mat, self.data[file_name].cell_pos
            )

    def filter_mat(
        self,
        threshold: float = PARAMETERS.threshold,
        name_list: list[str] | None = None,
        lock_mz: bool = PARAMETERS.lock,
        method: str = "all"
    ):
        """
        Filter out the data with low occurrence
        Args:
            threshold: Minimum occurrence rate of the data, default 0.2
            name_list: File name list, if None, all files will be processed.
            lock_mz: If True, the mz you select in lock mz file will be locked, default False.
            method: Method to filter the data, default "all", can be "all", "any", "none".
        """
        if name_list is None:
            name_list = list(self.data.keys())
        mat_list = [self.data[name].cell_mat for name in name_list]
        total_mat = filter_mat(mat_list, threshold, lock_mz, method)
        for index, name in enumerate(name_list):
            self.data[name].cell_mat = total_mat[index]
        logger.info("Filter out the mat data.")

    def normalize(self,
                  data: dict[str, SCData],
                  normalize_method: list[str],
                  file_name: str | None = None):
        if file_name is None:
            for ms_data in data.values():
                ms_data.cell_mat = normalize(
                    ms_data.cell_mat, normalize_method, mz=self.ref_mz
                )
        else:
            data[file_name].cell_mat = normalize(
                data[file_name].cell_mat, normalize_method, mz=self.ref_mz
            )
        logger.info("Normalization finished.")

    def fill(self,
             data: dict[str, SCData],
             file_name: str | None = None,
             fillna_method: str = "knn"
             ):
        if file_name is None:
            for ms_data in data.values():
                ms_data.cell_mat = fill_mat(ms_data.cell_mat, fillna_method)
        else:
            data[file_name].cell_mat = fill_mat(
                data[file_name].cell_mat, fillna_method
            )
        logger.info("Fillna finished.")

    def combat(self, data: dict[str, SCData], tag_list: list[str], file_name: str | None = None):
        data = combat_batch_correction(data)
        return data

    def info(self, file_name: str | None = None):
        """
        Print the information of the MSProcess
        Args:
            file_name: File name, if None, all files' info will be printed.
        """
        if file_name is None:
            for ms_data in self.data.values():
                logger.info(
                    " ".join(
                        [
                            f"File name: {ms_data.name}",
                            f"Cells count: {ms_data.cell_count}",
                            f"Peaks count: {ms_data.cell_mat.shape[1]}",
                        ]
                    )
                )
        else:
            ms_data = self.data[file_name]
            logger.info(
                " ".join(
                    [
                        f"File name: {ms_data.name}",
                        f"Cells count: {ms_data.cell_count}",
                        f"Peaks count: {ms_data.cell_mat.shape[1]}",
                    ]
                )
            )

    def clear_memory(self, file_name: str | None = None):
        """
        Clear the memory of the MSProcess
        Args:
            file_name: File name, if None, all files will be processed.
        """
        if file_name is None:
            for value in self.data.values():
                value.clear()
        else:
            self.data[file_name].clear()
        logger.info("Memory cleared")

    def save(self, file_name: str | None = None, data_type: str = "mat", path: str | None = None):
        """
        Save the MSProcess
        Args:
            file_name: File name, if None, all files will be processed.
            data_type: File type, default "mat", "process" is also available.
            path: Path to save the file, default None,
             which means the file will be saved in the same directory as the data you loaded.
        """
        if path is None:
            dir_path = os.path.join(self.__dir, "Process")
        else:
            dir_path = path

        def get_data_by_type(ms_data, data_type):
            if data_type == "cell_mat":
                return ms_data.cell_mat
            if data_type == "mat":
                return ms_data.mat
            elif data_type == "process":
                return ms_data.process
            else:
                raise ValueError("Type should be 'mat' or 'process'")

        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        if file_name is None:
            for ms_data in self.data.values():
                get_data_by_type(ms_data, data_type).to_csv(
                    os.path.join(dir_path, f"{ms_data.name}_{data_type}.csv")
                )
        else:
            get_data_by_type(self.data[file_name], data_type).to_csv(
                os.path.join(dir_path, f"{file_name}_{data_type}.csv")
            )
        logger.info("Data saved!")

    def pre_process(
        self,
        file_name: str | list[str] | None = None,
        offset: float | None = None,
        cut_range: tuple[int, int] | None = None,
        resolution: float = PARAMETERS.resolution,
        count: int = PARAMETERS.count,
    ):
        """
        Pre-process the data, including offset, cut, and round.
        Args:
            file_name: File name
            offset: Offset of the data, if None, it will ignore the offset step.
            cut_range: Cut range of the data, if None, it will ignore the cut step.
            resolution: Resolution of the data, default 0.01.
            count: Minimum occurrence of the data, default 10.
        Returns:

        """
        if isinstance(file_name, str):
            self.data[file_name].set_offset(offset=offset)
            self.data[file_name].cut(start=cut_range[0], end=cut_range[1])
        elif isinstance(file_name, list):
            for name in file_name:
                offset = float(input(f"Please input the offset of {name}: "))
                cut_range = (
                    int(input(f"Please input the start of cut range of {name}: ")),
                    int(input(f"Please input the end of cut range of {name}: ")),
                )
                self.data[name].set_offset(offset=offset)
                self.data[name].cut(start=cut_range[0], end=cut_range[1])
        elif file_name is None:
            pass
        self.filter_occ(resolution=resolution, count=count)
        logger.info("Pre-process finished.")

    def process(
            self,
            max_ratio: float = PARAMETERS.maxratio,
            adjacent: int = PARAMETERS.adjacent,
            snr: float = PARAMETERS.snr,
            resolution: float = PARAMETERS.resolution,
            threshold: float = PARAMETERS.threshold,
            lock_mz: bool = PARAMETERS.lock,
            filter_method: str = "all"
    ):
        """
        Args:
            max_ratio: If the ratio of the max value to the second max value is larger than this value, the cell will be
            adjacent: The number of adjacent cells to be combined
            snr: Signal to noise ratio
            resolution: Resolution of the data
            threshold: Threshold of the data
            lock_mz: If True, the mz you select in lock mz file will be locked
            filter_method: Method of filtering
        """
        if self.data is None:
            logger.warning("Please check the data carefully!")
            raise ValueError("No data loaded, please load data first")
        self.gen_mat()
        self.round_mat(resolution=resolution)
        self.denoise(max_ratio=max_ratio)
        self.merge_cell(adjacent=adjacent)
        self.filter_assem(snr=snr)
        self.filter_mat(threshold=threshold, lock_mz=lock_mz, method=filter_method)
        self.info()
        self.clear_memory()
        return self.data

    def post_process(
            self,
            data: dict[str, SCData] = None,
            normalize_method=None,
            fillna_method: str = "none",
            tags: list[str] = None,
    ):
        """
        Args:
            data: Dict of MSData
            normalize_method: Method of normalization
            fillna_method: Method of filling nan
            tags: Tags of the data
        Returns:
            Dict of MSData
        """
        if normalize_method is None:
            normalize_method = ["mz"]
        if data is None:
            data = self.data
        self.normalize(data=data, normalize_method=normalize_method)
        self.fill(data=data, fillna_method=fillna_method)
        # self.combat()
        return data
