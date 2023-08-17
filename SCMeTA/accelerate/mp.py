import multiprocessing as mp
from functools import reduce

import time


class MultiProcessing:
    def __init__(self, cpu_num=mp.cpu_count()):
        self.cpu_num = cpu_num

    @staticmethod
    def process_sub_dict(args):
        sub_dict, func, args, kwargs = args
        result = []
        for key in sub_dict:
            processed = {key: func(sub_dict[key], *args, **kwargs)}
            result.append(processed)
        return result

    @staticmethod
    def merge_dicts(dict_list):
        result = {}
        for d in dict_list:
            result.update(d)
        return result

    def run(self, data, func, *args, **kwargs):
        num_processes = self.cpu_num

        # 将字典拆分成子字典列表
        data_items = list(data.items())
        sub_dicts = [dict(data_items[i::num_processes]) for i in range(num_processes)]

        with mp.Pool(num_processes) as pool:
            # 使用多进程处理子字典，得到一个包含 {key: value} 的列表
            processed_lists = pool.map(self.process_sub_dict, [(sub_dict, func, args, kwargs) for sub_dict in sub_dicts])

        # 合并处理过的列表
        result_list = []
        for plist in processed_lists:
            result_list.extend(plist)

        # 将包含 {key: value} 的列表合并成一个字典
        result_dict = self.merge_dicts(result_list)
        return result_dict


def key_func(x, num):
    return x * num

if __name__ == "__main__":
    data = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}
    start = time.time()
    mpa = MultiProcessing()
    result = mpa.run(data, key_func, 2)
    print(result)
