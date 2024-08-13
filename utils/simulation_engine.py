import numpy as np
from datetime import datetime
import random

LAST_AGE = 90 # シミュレーション終了年齢

class SimulationEngine:
    def __init__(self):
        self.default_answers = {
            'age': 30,
            'income': 400,  # 万円
            'buy_house': 'いいえ',
            'marriage_age': 0,
            'working_style': '共働き',
            'num_children': 0,
            'children_university': 'いいえ',
            'retirement_expense': 20,  # 万円
            'job_change': 'いいえ',
            'side_job': 'いいえ',
            'work_after_retirement': 'いいえ',
            'family_care': 'いいえ'
        }
        self.current_answers = self.default_answers.copy()

    def update_answer(self, question_index, answer):
        keys = list(self.current_answers.keys())
        if question_index < len(keys):
            key = keys[question_index]
            if key in ['age', 'income', 'marriage_age', 'num_children', 'retirement_expense']:
                try:
                    self.current_answers[key] = int(answer)
                except ValueError:
                    print(f"Warning: Invalid numeric input for {key}: {answer}")
                    # 期待しない入力がされたときデフォルト値を使用
            else:
                self.current_answers[key] = answer

    def simulate_lifetime_expenses(self, start_age=22, end_age=LAST_AGE, distribution='normal_clip', lower_limit=0.8, upper_limit=1.2):
        """
        生涯支出をシミュレーションする関数
        :param start_age: シミュレーション開始年齢 (デフォルト: 22)
        :param end_age: シミュレーション終了年齢 (デフォルト: 80)
        :param distribution: 使用する確率分布 ('uniform', 'normal', または 'normal_clip')
        :param lower_limit: 下限（正規分布のクリッピング用、デフォルト: 0.8）
        :param upper_limit: 上限（正規分布のクリッピング用、デフォルト: 1.2）
        :return: 年齢ごとの年間支出のリスト(中身は整数)
        """
        years = end_age - start_age + 1
        annual_expenses = []
        
        for current_age in range(start_age, end_age + 1):
            # 総務省「家計調査（家計収支編　単身世帯）2022年」による
            if current_age <= 34:
                monthly_expense = 158000
            elif current_age <= 59:
                monthly_expense = 186000
            else:
                monthly_expense = 150000
            
            # 毎月の支出にランダムな変動を加える
            if distribution == 'uniform':
                # 一様分布を使用（±10%）
                monthly_expense *= np.random.uniform(0.9, 1.1)
            elif distribution == 'normal':
                # 正規分布を使用（平均1、標準偏差0.05）
                monthly_expense *= np.random.normal(1, 0.05)
            elif distribution == 'normal_clip':
                # クリッピング付き正規分布を使用
                factor = np.clip(np.random.normal(1, 0.05), lower_limit, upper_limit)
                monthly_expense *= factor
            
            # 年間支出を計算
            annual_expense = monthly_expense * 12
            
            # 突発的な出費を考慮（5%の確率で年間支出の10%〜30%の追加支出）
            if np.random.random() < 0.05:
                annual_expense += annual_expense * np.random.uniform(0.1, 0.3)
            
            annual_expenses.append(round(annual_expense))
        
        return annual_expenses
    
    def calculate_pension(self, average_income):
        """
        在職中の平均年収に基づいて年間の年金額を計算する関数
        平均標準報酬額*(5.481÷1,000)*加入期間の月数/12カ月で計算
        40年間払っていることを前提としている
        参考：オリックス銀行[https://www.orixbank.co.jp/column/article/200/]
        回帰直線 y = 165.00x + 70650.00 を使用

        :param average_income: 在職中の平均年収（万円）
        :return: 年間の年金額（円）
        """

        # 回帰直線を使用して月額年金を計算
        monthly_pension = 165.00 * average_income + 70650.00 # 単位：円
        
        # 年間の年金額に変換
        annual_pension = monthly_pension * 12
        
        return round(annual_pension)

    def simulate_lifetime_income(self, current_age, current_income, retirement_age=65, last_age=LAST_AGE):
        """
        生涯収入をシミュレーションする関数
        
        :param current_age: 現在の年齢
        :param current_income: 現在の年収
        :param retirement_age: 退職年齢 (デフォルト: 65)
        :param last_age: シミュレーション終了年齢 (デフォルト: 90)
        :return: 年齢ごとの年間収入のリスト
        """
        years = last_age - current_age + 1
        annual_incomes = []
        
        # 多項式回帰モデルのパラメータ
        b0, b1, b2 = -150, 20, -0.2
        
        # 現在の収入に基づいてモデルを調整
        age_factor = b0 + b1 * current_age + b2 * current_age**2
        income_factor = current_income / (age_factor * 10000)
        
        # 緩やかな変動のためのパラメータ
        variation = 0.03  # 年間の最大変動率
        trend = 0  # トレンド（上昇or下降）
        
        for age in range(current_age, retirement_age + 1):
            # 現役期間の収入
            # 基本的な収入曲線（多項式モデル）
            base_income = (b0 + b1 * age + b2 * age**2) * 10000 * income_factor
            
            # トレンドの更新（-0.5%から0.5%の範囲で緩やかに変化）
            trend += np.random.uniform(-0.005, 0.005)
            trend = max(min(trend, 0.01), -0.01)  # トレンドを-1%から1%の範囲に制限
            
            # 緩やかな変動の追加
            random_variation = np.random.uniform(-variation, variation)
            income = base_income * (1 + trend + random_variation)
            annual_incomes.append(round(income))

        # 現役期間の平均収入を計算
        average_income = sum(annual_incomes) / len(annual_incomes) # 単位：円

        for age in range(retirement_age, last_age + 1):
            # 退職後の収入（年金）
            if age == retirement_age:
                pension = self.calculate_pension(average_income/10000)
            income = pension * (1 + np.random.uniform(-0.02, 0.02))  # 小さな変動
            annual_incomes.append(round(income))
        
        return annual_incomes, average_income

    def calculate_results(self, is_final=False):
        age = self.current_answers['age']
        income = self.current_answers['income'] * 10000  # 万円から円に変換
        buy_house = self.current_answers['buy_house'] == "はい"
        marriage_age = self.current_answers['marriage_age']
        working_style = self.current_answers['working_style']
        num_children = self.current_answers['num_children']
        children_university = self.current_answers['children_university'] == "はい"
        retirement_expense = self.current_answers['retirement_expense'] * 10000  # 万円から円に変換
        #job_change = self.current_answers['job_change'] == "はい"
        side_job = self.current_answers['side_job'] == "はい"
        work_after_retirement = self.current_answers['work_after_retirement'] == "はい"
        family_care = self.current_answers['family_care'] == "はい"

        years = LAST_AGE - age  # 90歳までシミュレーション
        yearly_income, average_income = self.simulate_lifetime_income(age, income)  # 生涯収入のシミュレーション
        yearly_expense = self.simulate_lifetime_expenses(start_age=age, end_age=LAST_AGE) # 生涯支出のシミュレーション

        # 持ち家購入の影響
        if buy_house:
            for i in range(0, min(30, years)):# 30年間ローンを支払うと仮定
                yearly_expense[i+15] += 1200000  # 住宅ローン返済額

        # 結婚の影響
        if marriage_age > age:
            marriage_year = marriage_age - age
            for i in range(marriage_year, years):
                yearly_expense[i] += 1000000

        # 共働きの場合、現役時代の収入を増やす
        if working_style == "共働き":
            retirement_age = 65  # 退職年齢を65歳と仮定
            for i in range(min(retirement_age - age, len(yearly_income))):
                yearly_income[i] += 1200000

        # 子供の影響
        for child in range(num_children):
            birth_year = max(marriage_age - age, 0) + 2 + child * 2  # 結婚2年後に第一子、以降3年おきに出産と仮定
            for i in range(birth_year, min(birth_year + 20, years)):
                yearly_expense[i] += 800000
            if children_university:
                for i in range(birth_year + 18, min(birth_year + 22, years)):
                    yearly_expense[i] += 1500000

        # 老後の生活費
        # for i in range(65 - age, LAST_AGE - age):
        #     yearly_expense[i] = retirement_expense * 12

        # # 転職の影響
        # if job_change and is_final:
        #     change_year = random.randint(1, 10)
        #     change_rate = random.uniform(0.9, 1.2)
        #     for i in range(change_year, years):
        #         yearly_income[i] *= change_rate

        # 副業収入
        if side_job:
            side_income = max(0,np.random.normal(600000, 180000))
            for i in range(years):
                yearly_income[i] += side_income

        # 定年後の就労
        if work_after_retirement:
            for i in range(65 - age, years):
                yearly_income[i] = average_income * 0.4

        # 家族の介護
        if family_care:
            care_start = max(50 - age, 0) # 50歳から介護が始まると仮定
            for i in range(care_start, min(care_start + 10, years)):# 年100万で10年継続と仮定
                yearly_expense[i] += 1500000
            
            #結婚している場合は配偶者の家族の介護も考慮
            if marriage_age > 0:
                for i in range(care_start, min(care_start + 10, years)):
                    yearly_expense[i] += 1500000

        # 資産推移の計算
        assets = [0]
        for i in range(years):
            assets.append(assets[-1] + yearly_income[i] - yearly_expense[i])

        total_savings = max(assets)
        yearly_savings = sum([yearly_income[i] - yearly_expense[i] for i in range(years)]) / years

        advice = self.generate_advice(assets, age, marriage_age, num_children)

        return {
            'graph_data': assets,
            'advice': advice,
            'total_savings': total_savings,
            'yearly_savings': yearly_savings,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'start_age': age  # 開始年齢を結果に含める
        }

    def generate_advice(self, assets, current_age, marriage_age, num_children):
        if assets[-1] < 0:
            return "現在の計画では老後の資金が不足する可能性があります。支出を見直すか、収入を増やす方法を検討してください。"
        elif assets[-1] < assets[-1] * 0.2:
            return f"{current_age}歳から毎月{int(assets[-1]*0.01)}円の積立投資を始めることをお勧めします。"
        else:
            return "現在の計画で順調に資産が増えていく見込みです。定期的に計画を見直すことをお勧めします。"