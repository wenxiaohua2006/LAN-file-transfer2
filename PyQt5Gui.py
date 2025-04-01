import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QHBoxLayout, QPushButton, QSpacerItem, QSizePolicy)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QPoint


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(40)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        
        self.title = QPushButton("Fille Transfer Login")
        self.title.setStyleSheet("font-weight: bold; border: none; background: transparent;")
        self.title.setFlat(True)
        self.title.setDisabled(True)
        
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        
        self.fullscreen_btn = QPushButton("□")
        self.fullscreen_btn.setFixedSize(20, 20)
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(self.parent.close)
        
        layout.addWidget(self.title)
        layout.addSpacerItem(spacer)
        layout.addWidget(self.fullscreen_btn)
        layout.addWidget(self.close_btn)
        self.setLayout(layout)
    
    def toggle_fullscreen(self):
        if self.parent.isFullScreen():
            self.parent.showNormal()
            self.fullscreen_btn.setText("□")
        else:
            self.parent.showFullScreen()
            self.fullscreen_btn.setText("◻")

class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 关键设置：允许无边框窗口调整大小
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowMinMaxButtonsHint)
        self.setAttribute(Qt.WA_Hover)  # 启用悬停事件检测
        
        self.setWindowTitle("Fille Transfer Login")
        self.resize(1400, 900)
        
        self.title_bar = TitleBar(self)
        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("http://127.0.0.1:5000/log"))
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(self.browser)
        
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
        # 窗口拖动相关
        self.drag_start_position = None
        self.drag_edge = None  # 当前拖动的边缘（None表示拖动窗口）

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos()
            self.drag_edge = self.get_edge(event.pos())
    
    def mouseMoveEvent(self, event):
        if not self.drag_start_position:
            return
            
        if self.drag_edge is None:  # 拖动窗口
            delta = event.globalPos() - self.drag_start_position
            self.move(self.pos() + delta)
            self.drag_start_position = event.globalPos()
        else:  # 调整窗口大小
            delta = event.globalPos() - self.drag_start_position
            geo = self.geometry()
            
            if "left" in self.drag_edge:
                geo.setLeft(geo.left() + delta.x())
            if "right" in self.drag_edge:
                geo.setRight(geo.right() + delta.x())
            if "top" in self.drag_edge:
                geo.setTop(geo.top() + delta.y())
            if "bottom" in self.drag_edge:
                geo.setBottom(geo.bottom() + delta.y())
                
            self.setGeometry(geo)
            self.drag_start_position = event.globalPos()
    
    def mouseReleaseEvent(self, event):
        self.drag_start_position = None
        self.drag_edge = None
    
    def get_edge(self, pos):
        """检测鼠标是否在窗口边缘（用于调整大小）"""
        margin = 5  # 边缘检测宽度（像素）
        rect = self.rect()
        
        edges = []
        if pos.x() <= margin:
            edges.append("left")
        if pos.x() >= rect.width() - margin:
            edges.append("right")
        if pos.y() <= margin:
            edges.append("top")
        if pos.y() >= rect.height() - margin:
            edges.append("bottom")
        
        if not edges:
            return None
        return "_".join(edges)  # 例如 "left_top"

    def event(self, event):
        """动态修改鼠标光标形状（当悬停在边缘时）"""
        if event.type() == event.HoverMove:
            edge = self.get_edge(event.pos())
            if edge == "left" or edge == "right":
                self.setCursor(Qt.SizeHorCursor)
            elif edge == "top" or edge == "bottom":
                self.setCursor(Qt.SizeVerCursor)
            elif edge in ("left_top", "right_bottom"):
                self.setCursor(Qt.SizeFDiagCursor)
            elif edge in ("right_top", "left_bottom"):
                self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.setCursor(Qt.ArrowCursor)
        return super().event(event)


def windowapp():
    app2 = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app2.exec_())

# windowapp()