from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea
from PyQt5.QtCore import Qt
from .matplotlib_canvas import MatplotlibCanvas

class HomeScreen(QWidget):
    def __init__(self, parent=None):
        super(HomeScreen, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title = QLabel("ライフプランシミュレーター", alignment=Qt.AlignCenter)
        layout.addWidget(self.title)

        self.graph = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.graph)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.summary_label = QLabel("", alignment=Qt.AlignLeft)
        self.summary_label.setWordWrap(True)
        scroll_area.setWidget(self.summary_label)
        layout.addWidget(scroll_area)

        self.start_button = QPushButton("シミュレーション開始")
        layout.addWidget(self.start_button)

    def update_graph(self, data, age):
        # データを万円単位に変換
        data_in_million_yen = [value / 10000 for value in data]
        # 年齢に基づいたx軸の値を生成
        ages = list(range(age, age + len(data_in_million_yen)))
        self.graph.plot_data(ages, data_in_million_yen)

    def update_summary(self, result, timestamp):
        summary = f"前回のシミュレーション結果 (実行日時: {timestamp}):\n"
        summary += f"総貯蓄額: {result['total_savings']/10000:,.1f}万円\n"
        summary += f"年間貯蓄額: {result['yearly_savings']/10000:,.1f}万円\n"
        summary += f"アドバイス: {result['advice']}"
        self.summary_label.setText(summary)