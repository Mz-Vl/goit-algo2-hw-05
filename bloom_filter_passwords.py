import mmh3
from bitarray import bitarray

class BloomFilter:
    def __init__(self, size: int, num_hashes: int):
        """
        Initialize the Bloom filter.
        :param size: Size of the bit array.
        :param num_hashes: Number of hash functions.
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = bitarray(size)
        self.bit_array.setall(0)

    def _hashes(self, item: str):
        """
        Generate hash values for the given item.
        :param item: The string to hash.
        :return: A generator of hash values.
        """
        for i in range(self.num_hashes):
            yield mmh3.hash(item, i) % self.size

    def add(self, item: str):
        """
        Add an item to the Bloom filter.
        :param item: The string to add.
        """
        for hash_value in self._hashes(item):
            self.bit_array[hash_value] = 1

    def check(self, item: str) -> bool:
        """
        Check if an item is possibly in the Bloom filter.
        :param item: The string to check.
        :return: True if the item is possibly in the filter, False otherwise.
        """
        return all(self.bit_array[hash_value] for hash_value in self._hashes(item))

def check_password_uniqueness(bloom_filter: BloomFilter, passwords: list):
    """
    Check the uniqueness of passwords using the given Bloom filter.
    :param bloom_filter: An instance of BloomFilter.
    :param passwords: A list of passwords to check.
    :return: A dictionary with passwords as keys and their uniqueness status as values.
    """
    results = {}
    for password in passwords:
        if not isinstance(password, str) or not password:
            results[password] = "Некоректний пароль"
            continue

        if bloom_filter.check(password):
            results[password] = "вже використаний"
        else:
            results[password] = "унікальний"
            bloom_filter.add(password)

    return results

if __name__ == "__main__":
    # Ініціалізація фільтра Блума
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Додавання існуючих паролів
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    # Перевірка нових паролів
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Виведення результатів
    for password, status in results.items():
        print(f"Пароль '{password}' — {status}.")
