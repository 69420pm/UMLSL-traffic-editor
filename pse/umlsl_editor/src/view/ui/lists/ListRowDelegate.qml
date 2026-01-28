import QtQuick 2.15
import QtQuick.Layouts 1.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    // --- 1. Exposed Properties ---
    // This allows you to handle the button click from outside
    signal editClicked()

    // THE MAGIC: Any child items you add when using this component
    // will automatically go into the 'contentArea' layout.
    default property alias content: contentArea.data

    // --- 2. Shared Styling ---
    width: ListView.view.width // Auto-width
    height: 48
    color: "#061523"
    border.color: "#18324B"
    border.width: 1
    radius: 32

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 24
        anchors.rightMargin: 12
        spacing: 20

        // --- 3. The Variable Content Area ---
        RowLayout {
            id: contentArea
            // This grabs all available space, pushing the button to the right
            Layout.fillWidth: true
            spacing: 20
        }

        // --- 4. The Fixed Button (Always on the right) ---
        Rectangle {
            Layout.preferredWidth: 44
            Layout.preferredHeight: 44
            radius: 22
            color: "#112639"

            Text {
                anchors.centerIn: parent
                text: "✎"
                color: "white"
            }

            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: root.editClicked()
            }
        }
    }
}