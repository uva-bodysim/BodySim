import QtQuick 2.1
import QtQuick.Controls 1.0
import QtQuick.Window 2.0

ApplicationWindow {
    id: applicationwindow1
    width: 500
    height: 500
    title: qsTr("Kinect")

    menuBar: MenuBar {
        Menu {
            title: qsTr("File")
            MenuItem {
                text: qsTr("Exit")
                onTriggered: Qt.quit();
            }
        }
    }

    Rectangle {
        id: rectangle1
        x: 33
        y: 25
        width: 200
        height: 200
        color: "#b74f4f"
        anchors.horizontalCenterOffset: -117
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenterOffset: -125
        anchors.verticalCenter: parent.verticalCenter
    }

    Rectangle {
        id: rectangle2
        x: 273
        y: 26
        width: 200
        height: 200
        color: "#363f84"
        anchors.horizontalCenterOffset: 123
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenterOffset: -124
        anchors.verticalCenter: parent.verticalCenter
    }

    Rectangle {
        id: rectangle3
        x: 33
        y: 232
        width: 200
        height: 200
        color: "#62c07d"
        anchors.horizontalCenterOffset: -117
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenterOffset: 82
        anchors.verticalCenter: parent.verticalCenter
    }

    Rectangle {
        id: rectangle4
        x: 273
        y: 233
        width: 200
        height: 200
        color: "#dd6bd4"
        anchors.horizontalCenterOffset: 123
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenterOffset: 83
        anchors.verticalCenter: parent.verticalCenter
    }

    Button {
        id: button1
        x: 33
        y: 457
        text: "Preview"
        anchors.verticalCenterOffset: 219
        anchors.horizontalCenterOffset: -179
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
    }

    Button {
        id: button2
        x: 141
        y: 458
        text: "Done"
        anchors.verticalCenterOffset: 220
        anchors.horizontalCenterOffset: -71
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
    }

    Button {
        id: button3
        x: 273
        y: 458
        text: "Capture"
        anchors.verticalCenterOffset: 220
        anchors.horizontalCenterOffset: 61
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.verticalCenter: parent.verticalCenter
    }
}
