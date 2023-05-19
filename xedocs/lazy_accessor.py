from rframe.data_accessor import DataAccessor


class LazyDataAccessor(DataAccessor):
    _storage = None

    @property
    def storage(self):
        if self._storage is None:
            self._storage = self.get_storage()
        return self._storage

    @storage.setter
    def storage(self, value):
        if not callable(value):
            raise ValueError('storage must be callable')
        self.get_storage = value
