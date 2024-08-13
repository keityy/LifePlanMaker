from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QLineEdit, QHBoxLayout, QButtonGroup, QRadioButton
from PyQt5.QtCore import Qt
from .matplotlib_canvas import MatplotlibCanvas

class SimulationScreen(QWidget):
    def __init__(self, app, parent=None):
        super(SimulationScreen, self).__init__(parent)
        self.app = app  # LifePlanAppへの参照を保持
        self.init_ui()
        self.questions = [
            {"text": "年齢を入力してください。", "type": "number"},
            {"text": "年収を入力してください。（万円）", "type": "number"},
            {"text": "持ち家を購入する予定はありますか？", "type": "yes_no"},
            {"text": "何歳で結婚する予定ですか？（結婚しない場合は0）", "type": "number"},
            {"text": "結婚後の家計状況は？", "type": "radio", "options": ["共働き", "片働き"]},
            {"text": "子供は何人欲しいですか？", "type": "number"},
            {"text": "子供の大学進学を考えていますか？", "type": "yes_no"},
            {"text": "老後の生活費として月にいくら必要だと考えていますか？（万円）", "type": "number"},
            {"text": "転職の予定はありますか？", "type": "yes_no"},
            {"text": "副業収入はありますか？", "type": "yes_no"},
            {"text": "定年後も働く予定はありますか？", "type": "yes_no"},
            {"text": "将来、介護が必要な家族の世話をする可能性はありますか？", "type": "yes_no"}
        ]
        self.current_question = 0
        self.answers = []

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.question_label = QLabel("", alignment=Qt.AlignCenter)
        layout.addWidget(self.question_label)

        self.input_layout = QHBoxLayout()
        layout.addLayout(self.input_layout)

        self.answer_input = QLineEdit()
        self.input_layout.addWidget(self.answer_input)
        self.answer_input.hide()

        self.yes_button = QPushButton("はい")
        self.no_button = QPushButton("いいえ")
        self.input_layout.addWidget(self.yes_button)
        self.input_layout.addWidget(self.no_button)
        self.yes_button.hide()
        self.no_button.hide()

        self.radio_group = QButtonGroup(self)
        self.radio_buttons = []

        self.yes_button.clicked.connect(lambda: self.handle_yes_no("はい"))
        self.no_button.clicked.connect(lambda: self.handle_yes_no("いいえ"))

        self.submit_button = QPushButton("回答を送信")
        layout.addWidget(self.submit_button)

        self.graph = MatplotlibCanvas(self, width=5, height=4, dpi=100)
        layout.addWidget(self.graph)

    def reset(self):
        self.current_question = 0
        self.answers = []
        self.show_question()
        self.update_graph()

    def show_question(self):
        question = self.questions[self.current_question]
        self.question_label.setText(question["text"])
        
        self.answer_input.hide()
        self.yes_button.hide()
        self.no_button.hide()
        self.submit_button.hide()
        for button in self.radio_buttons:
            button.hide()

        if question["type"] == "yes_no":
            self.yes_button.show()
            self.no_button.show()
        elif question["type"] == "number":
            self.answer_input.show()
            self.submit_button.show()
        elif question["type"] == "radio":
            self.radio_buttons = []
            for option in question["options"]:
                radio_button = QRadioButton(option)
                self.radio_group.addButton(radio_button)
                self.radio_buttons.append(radio_button)
                self.input_layout.addWidget(radio_button)
                radio_button.show()
            self.submit_button.show()

    def handle_yes_no(self, answer):
        self.answers.append(answer)
        self.update_graph()
        self.next_question()

    def get_answer(self):
        if self.current_question >= len(self.questions):
            return None
        question = self.questions[self.current_question]
        answer = None
        if question["type"] == "yes_no":
            answer = "はい" if self.yes_button.isChecked() else "いいえ"
        elif question["type"] == "number":
            answer = self.answer_input.text()
            self.answer_input.clear()
        elif question["type"] == "radio":
            for button in self.radio_buttons:
                if button.isChecked():
                    answer = button.text()
                    break
        if answer is not None:
            self.app.simulation_engine.update_answer(self.current_question, answer)
        
        return answer

    def next_question(self):
        self.current_question += 1
        if self.current_question < len(self.questions):
            self.show_question()
        else:
            self.current_question = len(self.questions) - 1  # インデックスを最後の質問に戻す
            self.app.process_answer()

    def is_last_question(self):
        return self.current_question == len(self.questions) - 1

    def get_all_answers(self):
        return self.answers

    def update_graph(self):
        results = self.app.simulation_engine.calculate_results()
        # グラフデータを万円単位に変換
        graph_data_in_million_yen = [value / 10000 for value in results['graph_data']]
        
        # 現在の年齢を取得
        current_age = self.app.simulation_engine.current_answers['age']
        
        # 年齢に基づいたx軸の値を生成
        ages = list(range(current_age, current_age + len(graph_data_in_million_yen)))
        
        self.graph.plot_data(ages, graph_data_in_million_yen)