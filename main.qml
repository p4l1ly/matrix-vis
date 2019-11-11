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
  }

  Rectangle {
    anchors { top: parent.top; bottom: footer.top; left: parent.left; right: parent.right }

    GridLayout {
      id: radio_controls
      anchors.top: parent.top
      columns: 2
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
      anchors.left: radio_controls.right
      anchors.top: parent.top
      anchors.bottom: parent.bottom
      anchors.right: parent.right

      orientation: Qt.Horizontal
      spacing: 2

      model: ListModel {
        ListElement { index: 1 }
        ListElement { index: 2 }
        ListElement { index: 3 }
      }

      delegate: Rectangle {
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        width: 300

        RadioButton {
          id: xradio
          ButtonGroup.group: xradios
          checkable: !yradio.checked && ! zradio.checked
          anchors { left: parent.left; right: parent.right }
          y: xuncheck.y
          height: xuncheck.height
          onCheckedChanged: sendToPy()
        }
        RadioButton {
          id: yradio
          ButtonGroup.group: yradios
          checkable: !xradio.checked && ! zradio.checked
          anchors { left: parent.left; right: parent.right }
          y: yuncheck.y
          height: zuncheck.height
          onCheckedChanged: sendToPy()
        }
        RadioButton {
          id: zradio
          ButtonGroup.group: zradios
          checkable: !xradio.checked && ! yradio.checked
          anchors { left: parent.left; right: parent.right }
          y: zuncheck.y
          height: zuncheck.height
          onCheckedChanged: sendToPy()
        }

        GridLayout {
          id: selectionControls
          anchors.right: parent.right
          anchors.left: parent.left
          anchors.top: zradio.bottom
          Button { text: "clear"; Layout.fillWidth: true; }
          Button { text: "invert"; Layout.fillWidth: true; }
        }

        ListView {
          anchors.top: selectionControls.bottom
          anchors.bottom: parent.bottom
          width: parent.width

          model: DelegateModel {
            id: ticModel
            model: ListModel {
              ListElement {txt: "foo"}
              ListElement {txt: "bar"}
              ListElement {txt: "baz"}
            }

            groups: [ DelegateModelGroup {name: "selected"} ]

            delegate: Component {
              Rectangle {
                id: item

                anchors {
                  left: parent.left
                  right: parent.right
                }
                height: 30

                color: DelegateModel.inSelected ? 'lightblue' : 'lightgrey'
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
                    text: "1.0"
                    verticalAlignment: Text.AlignVCenter
                    onEditingFinished: sendToPy()
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
                  text: txt

                  MouseArea {
                    anchors.fill: parent
                    onClicked: {
                      item.DelegateModel.inSelected ^= true;
                      sendToPy()
                    }
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

    Button { anchors.bottom: parent.bottom; width: parent.width / parent.children.length - 4; text: "Load from file"; Layout.fillWidth: true }
    Button { anchors.bottom: parent.bottom; width: parent.width / parent.children.length - 4; text: "Save to file"; Layout.fillWidth: true }
    CheckBox { anchors.bottom: parent.bottom; width: parent.width / parent.children.length - 4; text: "Read from API"; Layout.fillWidth: true }
    Button { anchors.bottom: parent.bottom; width: parent.width / parent.children.length - 4; text: "Send via API"; Layout.fillWidth: true }
  }

  Text {
    id: errmsg
    anchors { bottom: parent.bottom; left: parent.left; right: parent.right }
    text: "foo"
  }
}
