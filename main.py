import sys
from os.path import abspath, dirname, join
from onenotelinux import onenote
from PySide2.QtGui import QGuiApplication, QStandardItemModel, QStandardItem
from PySide2.QtQml import QQmlApplicationEngine


class OneNoteTreeModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setColumnCount(0)

        root = self.invisibleRootItem()
        for notebook in onenote.get_notebooks():
            root.appendRow(QStandardItem(notebook.name))

        self.destroyed.connect(lambda o: print('destroyed', o))


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()
    qmlFile = join(dirname(__file__), 'main.qml')
    onenoteModel = OneNoteTreeModel()
    engine.rootContext().setContextProperty("onenoteModel", onenoteModel)
    engine.load(abspath(qmlFile))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
