import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ListView {
    anchors.fill: parent
    spacing: 8
    model: data_model

    delegate: ListRowDelegate {
        onEditClicked: data_model.handle_button_click(index)
        border_color: model.role_valid ? "#799582" : "#D97855"

        Item {
            id: latexContainer
            Layout.preferredWidth: latexImage.status === Image.Ready ? Math.min(latexImage.implicitWidth + 8, 150) : 150
            Layout.preferredHeight: 28
            Layout.maximumWidth: 150
            Layout.alignment: Qt.AlignVCenter

            Image {
                id: latexImage
                anchors.left: parent.left
                anchors.leftMargin: 4
                anchors.verticalCenter: parent.verticalCenter
                anchors.verticalCenterOffset: 2
                source: model.role_latex_image
                visible: status === Image.Ready
                cache: false
                asynchronous: true
                // Request at desired max size - the provider will scale appropriately
                sourceSize.width: 150
                sourceSize.height: 28
                // Let the image use its natural size from the provider
                fillMode: Image.PreserveAspectFit
            }

            Text {
                anchors.fill: parent
                anchors.leftMargin: 4
                text: model.role_query
                color: "#F9F9F9"
                font.bold: true
                font.pixelSize: 20
                elide: Text.ElideRight
                verticalAlignment: Text.AlignVCenter
                visible: latexImage.status !== Image.Ready
            }
        }


        Text {
            text: model.role_ego_name
            color: model.role_ego_color
            font.bold: false
            font.pixelSize: 20
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            Layout.alignment: Qt.AlignVCenter
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }
    }
}
