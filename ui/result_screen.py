from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea
from PyQt5.QtCore import Qt
from .matplotlib_canvas import MatplotlibCanvas

class ResultScreen(QWidget):
    def __init__(self, app, parent=None):
        super(ResultScreen, self).__init__(parent)
        self.app = app
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title = QLabel("シミュレーション結果", alignment=Qt.AlignCenter)
        layout.addWidget(self.title)

        self.graph = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.graph)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.summary_label = QLabel("", alignment=Qt.AlignLeft)
        self.summary_label.setWordWrap(True)
        scroll_area.setWidget(self.summary_label)
        layout.addWidget(scroll_area)

        self.restart_button = QPushButton("再シミュレーション")
        layout.addWidget(self.restart_button)

    def display_results(self, results):
        # グラフデータを万円単位に変換
        graph_data_in_million_yen = [value / 10000 for value in results['graph_data']]
        
        # 現在の年齢を取得
        current_age = self.app.simulation_engine.current_answers['age']
        
        # 年齢に基づいたx軸の値を生成
        ages = list(range(current_age, current_age + len(graph_data_in_million_yen)))
        
        self.graph.plot_data(ages, graph_data_in_million_yen)

        summary = f"シミュレーション結果:\n"
        summary += f"総貯蓄額: {results['total_savings']/10000:,.1f}万円\n"
        summary += f"年間平均貯蓄額: {results['yearly_savings']/10000:,.1f}万円\n"
        summary += f"アドバイス: {results['advice']}"
        self.summary_label.setText(summary)