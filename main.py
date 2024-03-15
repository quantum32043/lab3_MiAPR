import sys

from PySide6 import QtCore
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QBrush, QColor, QPen, QPainter
from PySide6.QtWidgets import QApplication, QLineEdit, QWidget, QLabel
import numpy as np
import random


class DrawingWidget(QWidget):
    def __init__(self, parent=None):
        super(DrawingWidget, self).__init__(parent)
        self.points_count = 500000
        self.pc1 = 0.56
        self.pc2 = 0.44
        self._random = random.Random()
        self.points1 = self.get_points(-100, int(self.width() / 1.6))
        self.points2 = self.get_points(100, int(self.width() / 1.6) + 200)
        self.mx1 = np.mean(self.points1)
        self.mx2 = np.mean(self.points2)
        self.sigma1 = np.sqrt(np.sum((self.points1 - self.mx1) ** 2) / len(self.points1))
        self.sigma2 = np.sqrt(np.sum((self.points2 - self.mx2) ** 2) / len(self.points2))
        self.result1 = np.zeros(int(self.width()))
        self.result2 = np.zeros(int(self.width()))
        self.calculate_results()
        self.brushes = [QColor(Qt.GlobalColor.red), QColor(Qt.GlobalColor.blue), QColor(Qt.GlobalColor.white),
                        QColor(Qt.GlobalColor.green)]
        self.intersection_point_index = -1
        self.intersection_threshold = 0.00003
        self.textbox_false_alarm = QLineEdit(self)
        self.textbox_false_alarm.setGeometry(QtCore.QRect(0, 0, 100, 20))
        self.textbox_miss = QLineEdit(self)
        self.textbox_miss.setGeometry(QtCore.QRect(0, 30, 100, 20))
        self.textbox_amount_of_risk = QLineEdit(self)
        self.textbox_amount_of_risk.setGeometry(QtCore.QRect(0, 60, 100, 20))

    def get_points(self, min_value, max_value):
        points = np.zeros(self.points_count)
        for i in range(len(points)):
            points[i] = self._random.randint(min_value, max_value - 50)  # 50?
        return points

    def calculate_results(self):
        for x in range(1, len(self.result1)):
            self.result1[x] = np.exp(-0.5 * ((x - 100 - self.mx1) / self.sigma1) ** 2) / (
                    self.sigma1 * np.sqrt(2 * np.pi)) * self.pc1
            self.result2[x] = np.exp(-0.5 * ((x - 100 - self.mx2) / self.sigma2) ** 2) / (
                    self.sigma2 * np.sqrt(2 * np.pi)) * self.pc2

    def paintEvent(self, event):
        painter = QPainter(self)
        for x in range(1, len(self.result1)):
            painter.setPen(QPen(self.brushes[1], 1))
            painter.drawLine(QPoint(x - 1, self.height() - int(self.result1[x - 1] * self.height() * 470)),
                             QPoint(x, self.height() - int(self.result1[x] * self.height() * 470)))
            painter.setPen(QPen(self.brushes[0], 1))
            painter.drawLine(QPoint(x - 1, self.height() - int(self.result2[x - 1] * self.height() * 470)),
                             QPoint(x, self.height() - int(self.result2[x] * self.height() * 470)))
            difference = abs(self.result1[x] - self.result2[x])
            if difference < self.intersection_threshold:
                self.intersection_point_index = x

        painter.setPen(QPen(self.brushes[2], 1))
        painter.drawLine(QPoint(0, self.height()), QPoint(self.width(), self.height()))
        painter.drawLine(QPoint(self.width(), self.height()), QPoint(self.width() - 15, self.height() - 5))
        painter.drawLine(QPoint(self.width(), self.height()), QPoint(self.width() - 15, self.height() + 5))
        painter.drawLine(QPoint(0, self.height() - 1), QPoint(0, 0))
        painter.drawLine(QPoint(0, 0), QPoint(-5, 15))
        painter.drawLine(QPoint(0, 0), QPoint(5, 15))
        painter.setPen(QPen(self.brushes[3], 2))
        painter.drawLine(QPoint(self.intersection_point_index, 0),
                         QPoint(self.intersection_point_index, self.height()))
        painter.setBrush(QBrush(self.brushes[3]))
        painter.drawEllipse(QPoint(self.intersection_point_index, self.height() - int(
            self.result2[self.intersection_point_index] * self.height() * 470)), 5.5, 5.5)

        error1 = np.sum(self.result2[:self.intersection_point_index])
        error2 = np.sum(self.result1[self.intersection_point_index:])

        self.textbox_false_alarm.setText(f"{error1:.10f}")
        self.textbox_miss.setText(f"{error2:.10f}")
        self.textbox_amount_of_risk.setText(f"{error1 + error2:.10f}")


if __name__ == "__main__":
    app = QApplication()
    widget = DrawingWidget()
    widget.setGeometry(0, 0, 600, 500)
    widget.show()
    sys.exit(app.exec())
