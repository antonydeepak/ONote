import sys
from os.path import abspath, dirname, join

from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import (
    QAbstractItemModel
)


class TreeModel(QAbstractItemModel):
    pass


if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
