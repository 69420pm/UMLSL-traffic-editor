import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ListView {
    anchors.fill: parent
    spacing: 12
    model: data_model

    delegate: ListRowDelegate {
        onEditClicked: data_model.handle_button_click(index)

        Text {
            text: model.role_name
            color: "white"
            font.bold: true
            font.pixelSize: 22
            // Keep this fixed or auto-sized based on content
        }

        Rectangle {
            Layout.preferredWidth: 24
            Layout.preferredHeight: 24
            radius: 16
            color: model.role_color
            Image {
                anchors.centerIn: parent
                source: "../../../widgets/qt_widgets/icons/car.svg"
                sourceSize.width: 16; sourceSize.height: 16
            }
        }

        // --- CRITICAL CHANGE HERE ---
        Text {
            text: model.role_value // "R: 6287d... L: 0"
            color: "white"
            font.pixelSize: 20

            // 1. Force this text to take whatever space is left
            Layout.fillWidth: true

            // 2. Cut off text on the right side with "..."
            elide: Text.ElideRight

            // 3. Optional: Vertical alignment to keep it pretty
            verticalAlignment: Text.AlignVCenter
        }
    }
}