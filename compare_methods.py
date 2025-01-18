import time
import re
import pandas as pd
import hashlib

LOG_FILE = "lms-stage-access.log"

def load_log_file(file_path):
    """
    Load log file and extract valid IP addresses.
    :param file_path: Path to the log file.
    :return: List of extracted IP addresses.
    """
    ip_pattern = re.compile(r"(?:\d{1,3}\.){3}\d{1,3}")
    ip_addresses = []
    with open(file_path, "r") as file:
        for line in file:
            match = ip_pattern.search(line)
            if match:
                ip_addresses.append(match.group())
    return ip_addresses

def count_unique_exact(ip_addresses):
    """
    Count unique IP addresses exactly.
    :param ip_addresses: List of IP addresses.
    :return: Number of unique IP addresses.
    """
    return len(set(ip_addresses))

class HyperLogLog:
    def __init__(self, b):
        """
        Initialize HyperLogLog with b bits for buckets.
        :param b: Number of bits used for bucket indexing.
        """
        self.b = b
        self.m = 1 << b  # Number of buckets (2^b)
        self.buckets = [0] * self.m

    def _hash(self, value):
        """
        Generate a hash for the given value.
        :param value: Input value.
        :return: Integer hash value.
        """
        return int(hashlib.md5(value.encode('utf8')).hexdigest(), 16)

    def add(self, value):
        """
        Add a value to the HyperLogLog.
        :param value: Input value.
        """
        x = self._hash(value)
        j = x & (self.m - 1)  # Bucket index
        w = x >> self.b  # Remaining bits
        self.buckets[j] = max(self.buckets[j], self._rho(w))

    def _rho(self, w):
        """
        Count the leading zeroes in the binary representation of w.
        :param w: Input value.
        :return: Number of leading zeroes.
        """
        return (w.bit_length() - len(bin(w).lstrip('-0b'))) + 1

    def count(self):
        """
        Estimate the cardinality using HyperLogLog.
        :return: Estimated cardinality.
        """
        Z = sum(2 ** -bucket for bucket in self.buckets)
        E = (0.7213 / (1 + 1.079 / self.m)) * (self.m ** 2) / Z
        return E

# Метод підрахунку за допомогою HyperLogLog
def count_unique_hyperloglog(ip_addresses, b=10):
    """
    Estimate unique IP addresses using HyperLogLog.
    :param ip_addresses: List of IP addresses.
    :param b: Number of bits used for bucket indexing.
    :return: Estimated number of unique IP addresses.
    """
    hll = HyperLogLog(b)
    for ip in ip_addresses:
        hll.add(ip)
    return hll.count()

if __name__ == "__main__":
    ip_addresses = load_log_file(LOG_FILE)

    start_exact = time.time()
    exact_count = count_unique_exact(ip_addresses)
    exact_time = time.time() - start_exact

    start_hll = time.time()
    hll_count = count_unique_hyperloglog(ip_addresses)
    hll_time = time.time() - start_hll

    results = pd.DataFrame({
        "": ["Точний підрахунок", "HyperLogLog"],
        "Унікальні елементи": [exact_count, hll_count],
        "Час виконання (сек.)": [exact_time, hll_time]
    })

    print("Результати порівняння:")
    print(results)