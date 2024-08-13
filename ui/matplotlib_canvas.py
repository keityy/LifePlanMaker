from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib
import sys

class MatplotlibCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.setup_japanese_font()
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MatplotlibCanvas, self).__init__(fig)

    def setup_japanese_font(self):
        if sys.platform.startswith('win'):
            # Windows の場合
            font_path = 'C:\\Windows\\Fonts\\meiryo.ttc'
        elif sys.platform.startswith('darwin'):
            # macOS の場合
            font_path = '/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc'
        elif sys.platform.startswith('linux'):
            # Linux の場合
            font_path = '/usr/share/fonts/truetype/takao-gothic/TakaoPGothic.ttf'
        else:
            # その他のOSの場合、デフォルトのフォントを使用
            font_path = matplotlib.font_manager.findfont(matplotlib.font_manager.FontProperties())

        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Meiryo', 'Hiragino Sans', 'Yu Gothic', 'Takao', 'IPAexGothic']
        matplotlib.font_manager.fontManager.addfont(font_path)

    def plot_data(self, ages, data):
        self.axes.clear()
        self.axes.plot(ages, data)
        self.axes.set_ylabel('資産 (万円)')
        self.axes.set_xlabel('年齢')
        self.axes.set_xticks(range(min(ages), max(ages)+1, 5))  # 5年ごとに目盛りを表示
        self.draw()