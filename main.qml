import QtQuick 2.0
import QtQuick.Controls 2.5
import QtCharts 2.13
import QtQml 2.13
import QtDataVisualization 1.2

ApplicationWindow {
  visible: true
  id: root

  Button {
    anchors.fill: parent
    text: "fire"
    onClicked: {
      py.fire(0, 1);
    }
  }
}
