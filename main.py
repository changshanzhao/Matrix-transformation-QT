import sys
import torch
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSlot, QEvent, QPointF
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mainwindow import Ui_MainWindow
from PyQt6.QtGui import QMouseEvent

class Transformations:
    def __init__(self):
        self.scale_factor = 1.0
        self.angle = 0.0
        self.translation = torch.tensor([0, 0], dtype=torch.float32)

    def translate(self, dx, dy):
        self.translation += torch.tensor([dx, dy], dtype=torch.float32)

    def rotate(self, angle):
        self.angle += angle

    def set_scale(self, sx, sy):
        t = self.scale_factor * (sx + sy) / 2
        if 0.3 < t < 5.0:
            self.scale_factor = t

    def get_transformed_matrix(self):
        angle_tensor = torch.tensor(self.angle, dtype=torch.float32)
        c, s = torch.cos(torch.deg2rad(angle_tensor)), torch.sin(torch.deg2rad(angle_tensor))
        rotation_matrix = torch.tensor([[c, -s], [s, c]], dtype=torch.float32)
        scale_matrix = torch.tensor([[self.scale_factor, 0], [0, self.scale_factor]], dtype=torch.float32)
        return torch.matmul(scale_matrix, rotation_matrix), self.translation


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class GraphicsView(QWidget):
    def __init__(self, *args, **kwargs):
        super(GraphicsView, self).__init__(*args, **kwargs)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.transformations = Transformations()
        self.rect = None
        self.mouse_pos = (0, 0)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.draw_axes_and_rect()
        self.last_mouse_pos = None
        self.center_point = torch.tensor([384, 251], dtype=torch.float32)
        self.setMouseTracking(True)
        self.canvas.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self.canvas and event.type() == QEvent.Type.MouseMove:
            # 从事件中获取位置信息
            position = event.position().toPoint()
            # 重新发布鼠标移动事件给GraphicsView
            new_event = QMouseEvent(
                QEvent.Type.MouseMove,
                QPointF(position),
                event.button(),
                event.buttons(),
                event.modifiers()
            )
            # 调用GraphicsView的mouseMoveEvent处理方法
            self.mouseMoveEvent(new_event)
            return True
        return super().eventFilter(obj, event)

    def calculate_transforms(self, current_pos):
        # 计算平移
        if self.parent().current_mode == "translate":
            if self.last_mouse_pos is not None:
                dx = current_pos[0] - self.last_mouse_pos[0]
                dy = current_pos[1] - self.last_mouse_pos[1]
                self.transformations.translate(dx / 10, -dy / 10)
        # 计算旋转
        elif self.parent().current_mode == "rotate":
            angle = (current_pos[0] - self.center_point[0]) * 0.1
            self.transformations.rotate(angle)
        # 计算缩放
        elif self.parent().current_mode == "scale":
            distance = ((current_pos[0] - self.center_point[0]) ** 2 + (
                        current_pos[1] - self.center_point[1]) ** 2) ** 0.5
            scale = 1.0
            if 0.5 < distance / 100.0 < 1.5:
                scale = distance / 100.0
            elif distance / 100.0 < 0.5:
                scale = 0.5
            elif distance / 100.0 > 1.5:
                scale = 1.5
            self.transformations.set_scale(scale, scale)

        elif self.parent().current_mode == "translate_rotate":
            if self.last_mouse_pos is not None:
                dx = current_pos[0] - self.last_mouse_pos[0]
                dy = current_pos[1] - self.last_mouse_pos[1]
                self.transformations.translate(dx / 10, -dy / 10)
            angle = (current_pos[0] - self.center_point[0]) * 0.1
            self.transformations.rotate(angle)

        elif self.parent().current_mode == "translate_scale":

            if self.last_mouse_pos is not None:
                dx = current_pos[0] - self.last_mouse_pos[0]
                dy = current_pos[1] - self.last_mouse_pos[1]
                self.transformations.translate(dx / 10, -dy / 10)
            distance = ((current_pos[0] - self.center_point[0]) ** 2 + (
                        current_pos[1] - self.center_point[1]) ** 2) ** 0.5
            scale = 1.0
            if 0.5 < distance / 100.0 < 1.5:
                scale = distance / 100.0
            elif distance / 100.0 < 0.5:
                scale = 0.5
            elif distance / 100.0 > 1.5:
                scale = 1.5
            self.transformations.set_scale(scale, scale)

        elif self.parent().current_mode == "rotate_scale":
            angle = (current_pos[0] - self.center_point[0]) * 0.1
            self.transformations.rotate(angle)
            distance = ((current_pos[0] - self.center_point[0]) ** 2 + (
                        current_pos[1] - self.center_point[1]) ** 2) ** 0.5
            scale = 1.0
            if 0.5 < distance / 100.0 < 1.5:
                scale = distance / 100.0
            elif distance / 100.0 < 0.5:
                scale = 0.5
            elif distance / 100.0 > 1.5:
                scale = 1.5
            self.transformations.set_scale(scale, scale)

        elif self.parent().current_mode == "translate_rotate_scale":
            if self.last_mouse_pos is not None:
                dx = current_pos[0] - self.last_mouse_pos[0]
                dy = current_pos[1] - self.last_mouse_pos[1]
                self.transformations.translate(dx / 10, -dy / 10)
            angle = (current_pos[0] - self.center_point[0]) * 0.1
            self.transformations.rotate(angle)
            distance = ((current_pos[0] - self.center_point[0]) ** 2 + (
                    current_pos[1] - self.center_point[1]) ** 2) ** 0.5
            scale = 1.0
            if 0.5 < distance / 100.0 < 1.5:
                scale = distance / 100.0
            elif distance / 100.0 < 0.5:
                scale = 0.5
            elif distance / 100.0 > 1.5:
                scale = 1.5

            self.transformations.set_scale(scale, scale)

        self.update_rect()

    def draw_axes_and_rect(self):
        self.canvas.axes.clear()
        # 绘制坐标轴
        self.canvas.axes.axhline(y=0, color='black', linewidth=0.5)
        self.canvas.axes.axvline(x=0, color='black', linewidth=0.5)
        # 设置坐标轴的显示范围
        self.canvas.axes.set_xlim(-200, 200)
        self.canvas.axes.set_ylim(-200, 200)
        # 定义初始矩形的四个顶点
        points = torch.tensor([
            [-25, -25],
            [25, -25],
            [25, 25],
            [-25, 25]
        ], dtype=torch.float32)
        # 将顶点添加到图形中
        self.rect = self.canvas.axes.add_patch(
            plt.Polygon(points.tolist(), closed=True, edgecolor='red', facecolor='none')

        )
        self.canvas.draw()

    def update_rect(self):
        if self.rect is not None:
            rotation_matrix, translation = self.transformations.get_transformed_matrix()
            # 获取矩形的四个顶点
            points = torch.tensor([
                [-25, -25, 1],
                [25, -25, 1],
                [25, 25, 1],
                [-25, 25, 1]
            ], dtype=torch.float32)
            # 应用变换矩阵
            transformed_points = torch.matmul(points, torch.cat((rotation_matrix, translation.unsqueeze(1)), dim=1).t())
            # 只取前两列作为新的点坐标
            transformed_points = transformed_points[:, :2]
            # 更新多边形的顶点
            self.rect.set_xy(transformed_points.tolist())
            self.canvas.draw()


    def mouseMoveEvent(self, event):
        self.calculate_transforms((event.position().x(), event.position().y()))
        self.update_rect()
        self.last_mouse_pos = (event.position().x(), event.position().y())



class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.graphics_view = GraphicsView(self)
        self.graphics_view.setGeometry(QtCore.QRect(20, 70, 750, 500))
        self.init_buttons()
        self.current_mode = "translate"
        self.setMouseTracking(True)

    def init_buttons(self):
        self.pushButton.clicked.connect(lambda: self.set_current_mode("translate"))
        self.pushButton_2.clicked.connect(lambda: self.set_current_mode("rotate"))
        self.pushButton_3.clicked.connect(lambda: self.set_current_mode("scale"))
        self.pushButton_4.clicked.connect(lambda: self.set_current_mode("translate_rotate"))
        self.pushButton_5.clicked.connect(lambda: self.set_current_mode("translate_scale"))
        self.pushButton_6.clicked.connect(lambda: self.set_current_mode("rotate_scale"))
        self.pushButton_7.clicked.connect(lambda: self.set_current_mode("translate_rotate_scale"))

    def set_current_mode(self, mode):
        self.current_mode = mode


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())