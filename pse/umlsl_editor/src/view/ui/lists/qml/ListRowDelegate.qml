import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    signal editClicked()
    default property alias content: contentArea.data

    // Styling
    width: ListView.view.width
    height: 48
    color: "#011C27"
    border.color: "#042F40"
    border.width: 2
    radius: 16

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 16
        anchors.rightMargin: 8
        anchors.topMargin: 8
        anchors.bottomMargin: 8
        spacing: 8

        // --- CHANGE 1: Give the Content Area the fillWidth property ---
        RowLayout {
            id: contentArea
            Layout.fillWidth: true  // This makes the content area take all available space up to the button
            spacing: 16
        }

        // --- CHANGE 2: Remove the Spacer Item ---
        // (The Item { Layout.fillWidth: true } that was here is deleted)

        // --- The Fixed Button ---
        Rectangle {
            Layout.preferredWidth: 32
            Layout.preferredHeight: 32
            radius: 16
            color: editMouseArea.pressed ? "#042F40" : (editMouseArea.containsMouse ? "#084D68" : "#042F40")

            // Layout.alignment helps ensure it stays vertically centered if content grows
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter

            Image {
                anchors.centerIn: parent
                source: "../../../widgets/qt_widgets/icons/edit.svg"
                sourceSize.width: 16; sourceSize.height: 16
            }

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