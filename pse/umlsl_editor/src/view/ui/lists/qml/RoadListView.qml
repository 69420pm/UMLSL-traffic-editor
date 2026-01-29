import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ListView {
    anchors.fill: parent
    spacing: 12
    model: road_model

    delegate: ListRowDelegate {
        // Connect the button signal
        onEditClicked: road_model.handleButtonClick(index)

        Text {
            text: model.role_name // "R1"
            color: "white"
            font.bold: true
            font.pixelSize: 22
        }

        Image {
            source: "../../../widgets/qt_widgets/icons/add_road.svg"
            sourceSize.width: 24; sourceSize.height: 24
            rotation: model.role_isRotated ? 90 : 0
        }

        Text {
            text: model.role_value // "x = 5"
            color: "white"
            font.pixelSize: 20
        }
    }
}