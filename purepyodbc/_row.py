class Row:
    def __getitem__(self, item):
        return self.__dict__[item]
