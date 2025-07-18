from wtforms import Form
from wtforms.fields import (
   IntegerField, DateField, RadioField, SubmitField
)
# 使用するvalidatorをインポート
from wtforms.validators import (
    DataRequired, NumberRange
)
# ==================================================
# Formクラス
# ==================================================
# ユーザー情報クラス
class SettingInfoForm(Form):

# 目標金額入力
    GoalAmount = IntegerField('目標金額: ', validators=[NumberRange(min=0, message='目標金額を０以上で入力してください')])

# 達成目標日入力
    AchievementDay = DateField('達成目標日: ', validators=[DataRequired('達成日は必須入力です')], format="%Y-%m-%d", render_kw={"placeholder": "yyyy/mm/dd"})

# 時給入力
    NomalTimeWage = IntegerField('通常: ', validators=[NumberRange(min=0, message='時給を０以上で入力してください')])
    NightTimeWage = IntegerField('夜間: ', validators=[NumberRange(min=0, message='時給を０以上で入力してください')])
    MidnightTimeWage = IntegerField('深夜: ', validators=[NumberRange(min=0, message='時給を０以上で入力してください')])

# 初期設定登録
    submit = SubmitField('決定')