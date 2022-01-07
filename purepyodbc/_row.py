class Row:
    def __getitem__(self, item):
        if isinstance(item, int):
            return list(self.__dict__.values())[item]
        return self.__dict__[item]
