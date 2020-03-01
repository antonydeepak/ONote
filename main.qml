import QtQuick 2.0
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtQuick.Controls.Material 2.12

ApplicationWindow {
    id: page
    width: 800
    height: 400
    visible: true

    TreeView {
        anchors.fill: parent
        model: itemModel
        
        TableViewColumn {
                title: "Name"
                role: "name"
                width: 300
            }
    }
}