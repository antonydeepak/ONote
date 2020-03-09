import QtQuick 2.0
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Controls 1.4 as OldControls
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12

ApplicationWindow {
    id: onenotelinux
    title: qsTr("Onenote For Linux")
    width: 800
    height: 400
    visible: true

    OldControls.TreeView {
        anchors.fill: parent
        model: onenoteModel
        OldControls.TableViewColumn {
            role: "display"
            title: "Notebooks"
            width: 100
        }
    }
}
