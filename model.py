class Notebooks(object):
    def __init__(self):
        self.notebooks = []

    def add_notebook(self, notebook):
        self.notebooks.append(notebook)


class Notebook(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Section(object):
    pass