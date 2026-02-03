import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ListView {
    anchors.fill: parent
    spacing: 12
    model: data_model

    delegate: ListRowDelegate {
        // Connect the button signal
        onEditClicked: data_model.handle_button_click(index)

        // 1. The Name (e.g., "R1")
        Text {
            text: model.role_query + " on " + model.role_ego_name + ": " + (model.role_valid ? "Valid" : "Invalid")
            color: "white"
            font.bold: true
            font.pixelSize: 22
            // Keeps its natural width
        }

        Rectangle {
            Layout.preferredWidth: 24
            Layout.preferredHeight: 24
            radius: 16
            color: model.role_ego_color
            Image {
                anchors.centerIn: parent
                source: "../../../widgets/qt_widgets/icons/car.svg"
                sourceSize.width: 16; sourceSize.height: 16
            }
        }
    }
}