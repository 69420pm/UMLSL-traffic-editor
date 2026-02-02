import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    signal editClicked()

    default property alias content: contentArea.data

    width: ListView.view.width
    height: 48

    // --- 1. Selection State Color ---
    // If the row is selected, show lighter blue; otherwise dark.
    color: role_is_selected ? "#084D68" : "#011C27"

    border.color: "#042F40"
    border.width: 2
    radius: 16

    // --- 2. Background Selection Handler ---
    // This sits at the bottom of the stack (defined first).
    // Any click NOT caught by a button on top will fall through to here.
    MouseArea {
        anchors.fill: parent
        onClicked: {
            // Helper function to handle selection via the C++ model
            root.ListView.view.model.select_row(index)
        }
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 8
        anchors.topMargin: 8
        anchors.bottomMargin: 8
        spacing: 8

        // REMOVED: inputDriven: false (This line caused the error)

        RowLayout {
            id: contentArea
            Layout.fillWidth: true
            spacing: 16
        }

        // --- 3. The Edit Button ---
        Rectangle {
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32
            radius: 16

            // Button visual states
            color: editMouseArea.pressed ? "#042F40" : (editMouseArea.containsMouse ? "#084D68" : "#042F40")
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter

            Image {
                anchors.centerIn: parent
                source: "../../../widgets/qt_widgets/icons/edit.svg"
                sourceSize.width: 16; sourceSize.height: 16
            }

            // This MouseArea sits ON TOP of the background one.
            // It swallows the click event, so the row is NOT selected when you click edit.
            MouseArea {
                id: editMouseArea
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                hoverEnabled: true
                onClicked: root.editClicked()
            }
        }
    }
}