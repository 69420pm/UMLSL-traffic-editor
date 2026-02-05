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


        Text {
            text: model.role_query
            color: "#F9F9F9"
            font.bold: true
            font.pixelSize: 20
            Layout.minimumWidth: 0
            Layout.maximumWidth: 150
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }


        Text {
            text: "Ego: " + model.role_ego_name
            color: "#F9F9F9"
            font.bold: false
            font.pixelSize: 20
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            elide: Text.ElideRight
            verticalAlignment: Text.AlignVCenter
        }
    }
}