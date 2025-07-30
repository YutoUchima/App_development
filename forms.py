from wtforms import Form
from wtforms.fields import (
   IntegerField, DateField, SelectField, RadioField, TimeField, SubmitField, FloatField, BooleanField
)
# 使用するvalidatorをインポート
from wtforms.validators import (
    DataRequired, NumberRange
)


def generate_time_choices():
    choices = []
    # 00:00を最初に追加
    display = "00:00"
    value = "00.0"
    choices.append((value, display))

    for hour in range(6, 30):  # 6〜30時（翌朝6時）
        for minute in [0, 15, 30, 45]:
            display = f"{hour:02}:{minute:02}"  # 表示用：例 "06:30"
            float_value = hour + minute / 60    # 保存用：例 6 + 30/60 = 6.5
            value = str(round(float_value, 2))  # 文字列に変換して渡す（例 "6.5"）
            choices.append((value, display))

    # 30:00を最後に追加
    display = "30:00"
    value = "30.0"
    choices.append((value, display))

    return choices



# ==================================================
# Formクラス
# ==================================================
# ユーザー情報クラス
class SettingInfoForm(Form):


# 目標金額入力
    GoalAmount = IntegerField('目標金額: ', validators=[NumberRange(min=0, message='目標金額を０以上で入力してください')])

# 達成目標日入力
    AchievementDay = DateField('目標達成日: ', validators=[DataRequired('達成日は必須入力です')], format="%Y-%m-%d", render_kw={"placeholder": "yyyy/mm/dd"})


# 初期設定登録
    submit = SubmitField('決定')



class WageSettingInfoForm(Form):

# 時給入力
# 平日
    WeekdayNormalTimeWage = IntegerField('通常: ', validators=[NumberRange(min=0, message='時給を０以上で入力してください')])
    WeekdayNightTimeWage = IntegerField('夜間: ', validators=[NumberRange(min=0, message='時給を０以上で入力してください')])
    WeekdayMidnightTimeWage = IntegerField('深夜: ', validators=[NumberRange(min=0, message='時給を０以上で入力してください')])
# 土日祝 
    HolidayNormalTimeWage = IntegerField('通常: ', validators=[NumberRange(min=0, message='時給を０以上で入力してください')])
    HolidayNightTimeWage = IntegerField('夜間: ', validators=[NumberRange(min=0, message='時給を０以上で入力してください')])
    HolidayMidnightTimeWage = IntegerField('深夜: ', validators=[NumberRange(min=0, message='時給を０以上で入力してください')])

# 時間帯入力
    NormalStart = SelectField('通常開始', validators=[DataRequired(message='値を選択してください')])
    NormalEnd = SelectField('通常終了', validators=[DataRequired(message='値を選択してください')])
    NightStart = SelectField('夜間開始', validators=[DataRequired(message='値を選択してください')])
    NightEnd = SelectField('夜間終了', validators=[DataRequired(message='値を選択してください')])
    MidnightStart = SelectField('深夜開始', validators=[DataRequired(message='値を選択してください')])
    MidnightEnd =SelectField('深夜終了', validators=[DataRequired(message='値を選択してください')])


# 初期設定登録
    submit = SubmitField('決定')


    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            time_choices = generate_time_choices()
            self.NormalStart.choices = time_choices
            self.NormalEnd.choices = time_choices
            self.NightStart.choices = time_choices
            self.NightEnd.choices = time_choices
            self.MidnightStart.choices = time_choices
            self.MidnightEnd.choices = time_choices


class ShiftInfoForm(Form):
    ShiftDay = DateField('日付: ', validators=[DataRequired('日付は必須入力です')], format="%Y-%m-%d", render_kw={"placeholder": "yyyy/mm/dd"})
    StartTime = SelectField('開始時間', validators=[DataRequired(message='値を選択してください')])
    EndTime = SelectField('終了時間', validators=[DataRequired(message='値を選択してください')])
    BreakStartTime = SelectField('休憩開始時間', validators=[DataRequired(message='値を選択してください')])
    BreakEndTime = SelectField('休憩終了時間', validators=[DataRequired(message='値を選択してください')])
    DayType = RadioField('曜日区分: ', choices=[('weekday', '平日'), ('holiday', '土日祝')], default='weekday')
    Complete = BooleanField(default=False)

    submit = SubmitField('決定')


    
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            time_choices = generate_time_choices()
            self.StartTime.choices = time_choices
            self.EndTime.choices = time_choices
            self.BreakStartTime.choices = time_choices
            self.BreakEndTime.choices = time_choices

            

            