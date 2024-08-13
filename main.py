import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget
from ui import HomeScreen, SimulationScreen, ResultScreen
from utils.data_manager import DataManager
from utils.simulation_engine import SimulationEngine

class LifePlanApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ライフプランシミュレーター")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.data_manager = DataManager()
        self.simulation_engine = SimulationEngine()

        self.home_screen = HomeScreen(self)
        self.simulation_screen = SimulationScreen(self)
        self.result_screen = ResultScreen(self)

        self.central_widget.addWidget(self.home_screen)
        self.central_widget.addWidget(self.simulation_screen)
        self.central_widget.addWidget(self.result_screen)

        self.setup_connections()
        self.load_styles()

        # Load last simulation result
        last_simulation = self.data_manager.load_last_simulation_result()
        if last_simulation and 'result' in last_simulation:
            age = last_simulation['result'].get('start_age', 30)  # デフォルト値として30を使用
            self.home_screen.update_graph(last_simulation['result'].get('graph_data', []), age)
            self.home_screen.update_summary(last_simulation['result'], last_simulation.get('timestamp', '不明'))
        else:
            self.home_screen.update_summary({'total_savings': 0, 'yearly_savings': 0, 'advice': 'シミュレーションを実行してください。'}, '未実行')

    def setup_connections(self):
        self.home_screen.start_button.clicked.connect(self.start_simulation)
        self.simulation_screen.submit_button.clicked.connect(self.process_answer)
        self.result_screen.restart_button.clicked.connect(self.restart_simulation)

    def load_styles(self):
        with open('assets/styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

    def start_simulation(self):
        self.simulation_screen.reset()
        self.central_widget.setCurrentWidget(self.simulation_screen)

    def process_answer(self):
        answer = self.simulation_screen.get_answer()
        self.simulation_screen.update_graph()
        if self.simulation_screen.is_last_question():
            results = self.simulation_engine.calculate_results(is_final=True)
            self.result_screen.display_results(results)
            self.data_manager.save_simulation_result(results)
            self.central_widget.setCurrentWidget(self.result_screen)
        else:
            self.simulation_screen.next_question()

    def restart_simulation(self):
        last_simulation = self.data_manager.load_last_simulation_result()
        if last_simulation:
            age = last_simulation['result'].get('start_age', 30)  # デフォルト値として30を使用
            self.home_screen.update_graph(last_simulation['result']['graph_data'], age)
            self.home_screen.update_summary(last_simulation['result'], last_simulation['timestamp'])
        self.central_widget.setCurrentWidget(self.home_screen)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = LifePlanApp()
    main_window.show()
    sys.exit(app.exec_())