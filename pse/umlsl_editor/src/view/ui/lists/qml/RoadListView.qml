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
            text: model.role_name
            color: "white"
            font.bold: true
            font.pixelSize: 22
            // Keeps its natural width
        }

        // 2. The Road Icon
        Image {
            source: "../../../widgets/qt_widgets/icons/add_road.svg"
            sourceSize.width: 16; sourceSize.height: 16
            rotation: model.role_isRotated ? 90 : 0

            // Good practice: Ensure the layout knows the size and alignment
            Layout.preferredWidth: 16
            Layout.preferredHeight: 16
            Layout.alignment: Qt.AlignVCenter
        }

        // 3. The Value (e.g., "x = 5") - THIS GETS THE FIX
        Text {
            text: model.role_value
            color: "white"
            font.pixelSize: 20

            // --- The Logic to cut off text ---
            Layout.fillWidth: true        // 1. Grab all remaining space up to the edit button
            elide: Text.ElideRight        // 2. Cut off with "..." if it's too long
            verticalAlignment: Text.AlignVCenter // 3. Keep it centered vertically
        }
    }
}