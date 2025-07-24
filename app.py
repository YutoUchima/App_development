from flask import Flask, render_template, request
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
# ==================================================
# インスタンス生成
# ==================================================
app = Flask(__name__)


# ==================================================
# Flaskに対する設定
# ==================================================
import os
# 乱数を設定
app.config['SECRET_KEY'] = os.urandom(24)
base_dir = os.path.dirname(__file__)
database = 'sqlite:///' + os.path.join(base_dir, 'data.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ★db変数を使用してSQLAlchemyを操作できる
db = SQLAlchemy(app)
# ★「flask_migrate」を使用できる様にする
Migrate(app, db)

#==================================================
# モデル
#==================================================
# 課題
class HourlyWage(db.Model):
    # テーブル名
    __tablename__ = 'hourly_wage'
    
    # 課題ID
    HourlyWageID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 内容
    NormalTimeWage = db.Column(db.Integer, nullable=False)
    NightTimeWage = db.Column(db.Integer, nullable=False)
    MidnightTimeWage = db.Column(db.Integer, nullable=False)
    # 完了フラグ
    DayType = db.Column(db.Boolean, nullable=False)    

    # 表示用
    def __repr__(self):
        return f'<HourlyWage id={self.id}, DayType={self.DayType}>'


# ==================================================
# ルーティング
# ==================================================
from forms import SettingInfoForm

# ユーザー情報：入力
@app.route('/', methods=['GET','POST'])
def show_enter():
    # フォームの作成
    form = SettingInfoForm(request.form)
    # POST
    if request.method == "POST" and form.validate():

        weekday_wage = HourlyWage.query.filter_by(DayType=False).first()
        if weekday_wage:
            # 更新処理
            weekday_wage.NormalTimeWage = form.WeekdayNormalTimeWage.data
            weekday_wage.NightTimeWage = form.WeekdayNightTimeWage.data
            weekday_wage.MidnightTimeWage = form.WeekdayMidnightTimeWage.data
        else:
            # 新規作成
            weekday_wage = HourlyWage(
                NormalTimeWage=form.WeekdayNormalTimeWage.data,
                NightTimeWage=form.WeekdayNightTimeWage.data,
                MidnightTimeWage=form.WeekdayMidnightTimeWage.data,
                DayType=False
            )
            db.session.add(weekday_wage)

        # 土日祝 DayType=True
        holiday_wage = HourlyWage.query.filter_by(DayType=True).first()
        if holiday_wage:
            # 更新処理
            holiday_wage.NormalTimeWage = form.HolidayNormalTimeWage.data
            holiday_wage.NightTimeWage = form.HolidayNightTimeWage.data
            holiday_wage.MidnightTimeWage = form.HolidayMidnightTimeWage.data
        else:
            # 新規作成
            holiday_wage = HourlyWage(
                NormalTimeWage=form.HolidayNormalTimeWage.data,
                NightTimeWage=form.HolidayNightTimeWage.data,
                MidnightTimeWage=form.HolidayMidnightTimeWage.data,
                DayType=True
            )
            db.session.add(holiday_wage)
        db.session.commit()

        return render_template('displaytest.html', form=form)
    # POST以外と「form.validate()がfalse」
    return render_template('enter.html', form=form)

# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run()
