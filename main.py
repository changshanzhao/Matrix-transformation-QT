import sys
import torch
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt, pyqtSlot
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mainwindow import Ui_MainWindow

class Transformations:
    def __init__(self):
        self.translation_matrix = torch.tensor([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=torch.float32)
        self.rotation_matrix = torch.tensor([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=torch.float32)
        self.scale_matrix = torch.tensor([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=torch.float32)
        self.combined_matrix = torch.tensor([[1, 0, 0], [0, 1, 0], [0, 0, 1]], dtype=torch.float32)

    def translate(self, dx, dy):
        self.translation_matrix = torch.tensor([[1, 0, dx], [0, 1, dy], [0, 0, 1]], dtype=torch.float32)
        self.update_combined_matrix()

    def rotate(self, angle):
        radian = torch.deg2rad(torch.tensor(angle, dtype=torch.float32))
        self.rotation_matrix = torch.tensor([
            [torch.cos(radian), -torch.sin(radian), 0],
            [torch.sin(radian), torch.cos(radian), 0],
            [0, 0, 1]
        ], dtype=torch.float32)
        self.update_combined_matrix()

    def scale(self, sx, sy):
        self.scale_matrix = torch.tensor([[sx, 0, 0], [0, sy, 0], [0, 0, 1]], dtype=torch.float32)
        self.update_combined_matrix()

    def update_combined_matrix(self):
        self.combined_matrix = torch.matmul(self.scale_matrix,
                                            torch.matmul(self.rotation_matrix, self.translation_matrix))

    def get_transformed_matrix(self):
        return self.combined_matrix


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
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.draw_axes_and_rect()

    def draw_axes_and_rect(self):
        self.canvas.axes.clear()
        # 绘制坐标轴
        self.canvas.axes.axhline(y=0, color='black', linewidth=0.5)
        self.canvas.axes.axvline(x=0, color='black', linewidth=0.5)

        # 设置坐标轴的显示范围
        self.canvas.axes.set_xlim(-200, 200)
        self.canvas.axes.set_ylim(-200, 200)

        # 绘制初始矩形
        self.rect = self.canvas.axes.add_patch(
            plt.Rectangle((-25, -25), 50, 50, edgecolor='red', facecolor='none')
        )
        self.canvas.draw()

    def update_rect(self):
        if self.rect is not None:
            # 获取矩形的四个顶点
            points = torch.tensor([
                [-50, -50, 1],
                [50, -50, 1],
                [-50, 50, 1],
                [50, 50, 1]
            ], dtype=torch.float32)
            # 应用变换矩阵
            transformed_points = torch.mm(self.transformations.get_transformed_matrix(), points.t()).t()
            # 更新矩形的位置
            x_min = transformed_points[:, 0].min().item()
            y_min = transformed_points[:, 1].min().item()
            width = (transformed_points[:, 0].max() - transformed_points[:, 0].min()).item()
            height = (transformed_points[:, 1].max() - transformed_points[:, 1].min()).item()
            self.rect.set_xy((x_min, y_min))
            self.rect.set_width(width)
            self.rect.set_height(height)
            self.canvas.draw()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.graphics_view = GraphicsView(self)
        self.graphics_view.setGeometry(QtCore.QRect(20, 70, 750, 500))
        self.init_buttons()

    def init_buttons(self):
        self.pushButton.clicked.connect(lambda: self.apply_transform("translate"))
        self.pushButton_2.clicked.connect(lambda: self.apply_transform("rotate"))
        self.pushButton_3.clicked.connect(lambda: self.apply_transform("scale"))
        self.pushButton_4.clicked.connect(lambda: self.apply_transform("translate_rotate"))
        self.pushButton_5.clicked.connect(lambda: self.apply_transform("translate_scale"))
        self.pushButton_6.clicked.connect(lambda: self.apply_transform("rotate_scale"))
        self.pushButton_7.clicked.connect(lambda: self.apply_transform("translate_rotate_scale"))

    @pyqtSlot(str)
    def apply_transform(self, mode):
        if mode == "translate":
            self.graphics_view.transformations.translate(50, 50)
        elif mode == "rotate":
            self.graphics_view.transformations.rotate(30)
        elif mode == "scale":
            self.graphics_view.transformations.scale(1.5, 1.5)
        elif mode == "translate_rotate":
            self.graphics_view.transformations.translate(50, 50)
            self.graphics_view.transformations.rotate(30)
        elif mode == "translate_scale":
            self.graphics_view.transformations.translate(50, 50)
            self.graphics_view.transformations.scale(1.5, 1.5)
        elif mode == "rotate_scale":
            self.graphics_view.transformations.rotate(30)
            self.graphics_view.transformations.scale(1.5, 1.5)
        elif mode == "translate_rotate_scale":
            self.graphics_view.transformations.translate(50, 50)
            self.graphics_view.transformations.rotate(30)
            self.graphics_view.transformations.scale(1.5, 1.5)
        self.graphics_view.update_rect()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())