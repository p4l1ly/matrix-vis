import QtQuick 2.13
import QtQuick.Controls 2.5
import QtQml 2.13
import QtQml.Models 2.2
import QtQuick.Layouts 1.13

ApplicationWindow {
  visible: true
  id: root

  property var sendToPy: function() {
    console.log('sendToPy')
    // console.log(py.setting)
    // py.update(setting)
  }

  Rectangle {
    anchors { top: parent.top; bottom: footer.top; left: parent.left; right: parent.right }
    GridLayout {
      id: radio_controls
      anchors.top: parent.top
      columns: 2

      Text {
        id: dimLabelDummy
        Layout.fillWidth: true
        text: ' '
        font.pointSize: 20
        Layout.columnSpan: 2
      }

      Text { text: 'x'; font.bold: true; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
      Button { id: xuncheck; text: 'uncheck'; onClicked: xradios.checkState = Qt.Unchecked }
      Text { text: 'y'; font.bold: true; Layout.fillWidth: true; horizontalAlignment: Text.AlignHCenter }
      Button { id: yuncheck; text: 'uncheck'; onClicked: yradios.checkState = Qt.Unchecked }
      Text { text: 'series'; font.bold: true; Layout.fillWidth: true;  horizontalAlignment: Text.AlignHCenter }
      Button { id: zuncheck; text: 'uncheck'; onClicked: zradios.checkState = Qt.Unchecked }
    }

    ButtonGroup { id: xradios }
    ButtonGroup { id: yradios }
    ButtonGroup { id: zradios }

    ListView {
      id: dimList

      anchors.left: radio_controls.right
      anchors.leftMargin: 5
      anchors.top: parent.top
      anchors.bottom: parent.bottom
      anchors.right: parent.right

      orientation: Qt.Horizontal
      spacing: 5

      model: py.dimensions

      delegate: Rectangle {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 200

        Text {
          id: dimLabel
          anchors.left: parent.left
          anchors.right: parent.right
          text: modelData[0]
          font.pointSize: dimLabelDummy.font.pointSize
          horizontalAlignment: Text.AlignHCenter
        }

        RadioButton {
          id: xradio
          ButtonGroup.group: xradios
          checked: modelData[1][0].val
          onCheckedChanged: modelData[1][0].val = checked
          checkable: !yradio.checked && ! zradio.checked
          anchors { left: parent.left; right: parent.right }
          y: xuncheck.y
          height: xuncheck.height
        }
        RadioButton {
          id: yradio
          ButtonGroup.group: yradios
          checked: modelData[1][1].val
          onCheckedChanged: modelData[1][1].val = checked
          checkable: !xradio.checked && ! zradio.checked
          anchors { left: parent.left; right: parent.right }
          y: yuncheck.y
          height: zuncheck.height
        }
        RadioButton {
          id: zradio
          ButtonGroup.group: zradios
          checked: modelData[1][2].val
          onCheckedChanged: modelData[1][2].val = checked
          checkable: !xradio.checked && ! yradio.checked
          anchors { left: parent.left; right: parent.right }
          y: zuncheck.y
          height: zuncheck.height
        }

        GridLayout {
          id: selectionControls
          anchors.right: parent.right
          anchors.left: parent.left
          anchors.top: zradio.bottom
          columnSpacing: 2
          Button {
            text: "clear";
            Layout.fillWidth: true;
            onClicked: py.clear_dimension(index)
          }
          Button {
            text: "invert";
            Layout.fillWidth: true;
            onClicked: py.invert_dimension_filter(index)
          }
        }

        ListView {
          anchors.top: selectionControls.bottom
          anchors.topMargin: 2
          anchors.bottom: parent.bottom
          width: parent.width

          model: DelegateModel {
            id: ticModel
            model: modelData[2]

            delegate: Component {
              Rectangle {
                id: item

                anchors {
                  left: parent.left
                  right: parent.right
                }
                height: 30

                color: modelData[1].val ? 'lightblue' : 'lightgrey'
                border.color: '#dddddd'
                radius: 4

                Rectangle {
                  id: scale
                  anchors {
                    top: parent.top
                    right: parent.right
                    bottom: parent.bottom
                    topMargin: 2
                    bottomMargin: 2
                    rightMargin: 2
                  }
                  width: 40

                  color: 'white'
                  radius: 4

                  TextInput {
                    anchors.fill: parent
                    validator: DoubleValidator {}
                    text: modelData[2].val
                    verticalAlignment: Text.AlignVCenter
                    onEditingFinished: modelData[2].val = text
                  }
                }

                Text {
                  anchors {
                    top: parent.top
                    left: parent.left
                    bottom: parent.bottom
                    right: scale.left
                  }

                  horizontalAlignment: Text.AlignHCenter
                  verticalAlignment: Text.AlignVCenter
                  text: modelData[0]

                  MouseArea {
                    anchors.fill: parent
                    onClicked: modelData[1].val ^= 1
                  }
                }
              }
            }
          }
        }
      }
    }
  }

  Row {
    id: footer
    anchors { bottom: errmsg.top; left: parent.left; right: parent.right; leftMargin: 2 }
    spacing: 4

    Button {
      anchors.bottom: parent.bottom;
      width: parent.width / parent.children.length - 4;
      text: "Load from file";
      Layout.fillWidth: true
      onClicked: py.load_from_file()
    }

    Button {
      anchors.bottom: parent.bottom;
      width: parent.width / parent.children.length - 4;
      text: "Save to file";
      Layout.fillWidth: true
      onClicked: py.save_to_file()
    }

    CheckBox {
      anchors.bottom: parent.bottom;
      width: parent.width / parent.children.length - 4;
      text: "Enable API Read (Not Implemented)";
      Layout.fillWidth: true
    }

    Button {
      anchors.bottom: parent.bottom;
      width: parent.width / parent.children.length - 4;
      text: "Send via API (Not Implemented)";
      Layout.fillWidth: true
    }
  }

  Text {
    id: errmsg
    anchors { bottom: parent.bottom; left: parent.left; right: parent.right }
    text: py.error
  }
}
