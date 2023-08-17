import threading


class MultiThreader:
    def __init__(self, n_threads=10):
        self.n_threads = n_threads

    def run(self, func, args_list):
        results = {}
        threads = []

        def worker(*args):
            result = func(*args)
            results[args[0]] = result

        for args in args_list:
            thread = threading.Thread(target=worker, args=args)
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

        return results
