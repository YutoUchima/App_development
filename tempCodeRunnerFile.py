from flask import Flask, render_template, request
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import false


from datetime import datetime, time

def parse_float_time(value_str):
    hour, minute = map(int, value_str.split('.'))
    return time(hour=hour, minute=minute)



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

    NormalStart = db.Column(db.Float, nullable=False)
    NormalEnd = db.Column(db.Float, nullable=False)
    NightStart = db.Column(db.Float, nullable=False)
    NightEnd = db.Column(db.Float, nullable=False)
    MidnightStart = db.Column(db.Float, nullable=False)
    MidnightEnd = db.Column(db.Float, nullable=False)

    DayType = db.Column(db.Boolean, nullable=False)   





    # 表示用
    def __repr__(self):
        return f'<HourlyWage id={self.id}, DayType={self.DayType}, NomalTimeWage={self.NormalTimeWage}, NightTaimeWage={self.NightTimeWage}, MidnightTimeWage={self.MidnightTimeWage}>'

class Shift(db.Model):
   # テーブル名
   __tablename__ = 'shift'

   # ID
   ShiftID = db.Column(db.Integer, primary_key=True, autoincrement=True)

   ShiftDay = db.Column(db.Date, nullable=False)
   StartTime = db.Column(db.Float, nullable=False)
   EndTime = db.Column(db.Float, nullable=False)
   BreakStartTime = db.Column(db.Float, nullable=False)
   BreakEndTime = db.Column(db.Float, nullable=False)
   DayType = db.Column(db.Integer, db.ForeignKey('hourly_wage.DayType'), nullable=False)
   Complete = db.Column(db.Boolean, default=False, nullable=False)

   def __repr__(self):
      return f'<Shift id={self.ShiftID}, DayType={self.DayType} >'

class Setting(db.Model):
   #　テーブル名
   __tablename__ = 'setting'

   #　ID
   SettingID = db.Column(db.Integer, primary_key=True)

   GoalAmount = db.Column(db.Integer, nullable=False)
   AchievementDay = db.Column(db.Date, nullable=False)

   def __repr__(self):
      return f'<Setting id={self.SettingID}, GoalAmount={self.GoalAmount}, AchievementDay={self.AchievementDay}>'


class Display(db.Model):
   #　テーブル名
   __tablename__ = 'display'

   #　ID
   DisplayID = db.Column(db.Integer, primary_key=True)

   CurrentAmount = db.Column(db.Integer, nullable=False)
   RemainingAmount = db.Column(db.Integer, nullable=False)
   RemainingWorkTime = db.Column(db.Float, nullable=False)

   def __repr__(self):
      return f'<Display id={self.DisplayID}, CurrentAmount={self.CurrentAmount}, RemainingAmount={self.RemainingAmount}, RemainingWorkTime{self.RemainingWorkTime}>'



# ==================================================
# ルーティング
# ==================================================
from forms import SettingInfoForm
from forms import ShiftInfoForm



@app.route('/')
def home():
    # 未完了課題を取得
    uncompleted_shifts  = Shift.query.filter_by(Complete = False).all()
    # 完了課題を取得
    completed_shifts  = Shift.query.filter_by(Complete=True).all()
    return render_template('home.html', uncompleted_shifts=uncompleted_shifts, completed_shifts=completed_shifts)


# 登録
@app.route('/new_shift', methods=['GET', 'POST'])
def new_shift():
    
    # フォームの作成
    form = ShiftInfoForm(request.form)


    # POST
    if request.method == 'POST' and form.validate():
        # 入力値取得
        shift = Shift.query.filter_by(Complete=False).first()


        # インスタンス生成
        shift = Shift(
                ShiftDay=form.ShiftDay.data,
                StartTime=float(form.StartTime.data),
                EndTime=float(form.EndTime.data),
                BreakStartTime=float(form.BreakStartTime.data),
                BreakEndTime=float(form.BreakEndTime.data),
                DayType=(form.DayType.data == 'holiday'),
                Complete=False
            )


        # 登録
        db.session.add(shift)
        db.session.commit()
        # 一覧へ
        return redirect(url_for('home'))
    # GET
    return render_template('new_shift.html',form=form)



# 完了
@app.route('/shift/<int:shift_id>/complete', methods=['POST'])
def complete_shift(shift_id):
    # 対象データ取得
    shift = Shift.query.get(shift_id)
    # 完了フラグに「True」を設定
    shift.Complete =   True
    db.session.commit()
    return redirect(url_for('home'))


#削除
@app.route('/shift/<int:shift_id>/delete', methods=['POST'])
def delete_shift(shift_id):
    # 対象データ取得
    shift = Shift.query.get(shift_id)
    if shift:
        db.session.delete(shift)
        db.session.commit()
    return redirect(url_for('home'))

# 未完了
@app.route('/shift/<int:shift_id>/uncomplete', methods=['POST'])
def uncomplete_shift(shift_id):
    # 対象データ取得
    shift = Shift.query.get(shift_id)
    # 完了フラグに「False」を設定
    shift.Complete = False
    db.session.commit()
    return redirect(url_for('home'))

# ユーザー情報：入力
@app.route('/', methods=['GET','POST'])
def setting():
    # フォームの作成
    form = SettingInfoForm(request.form)
    # POST
    if request.method == "POST" and form.validate():

# HourlyWage テーブル
        weekday_wage = HourlyWage.query.filter_by(DayType=False).first()
        if weekday_wage:
            # 更新処理
            weekday_wage.NormalTimeWage = form.WeekdayNormalTimeWage.data
            weekday_wage.NightTimeWage = form.WeekdayNightTimeWage.data
            weekday_wage.MidnightTimeWage = form.WeekdayMidnightTimeWage.data

            weekday_wage.NormalStart = form.NormalStart.data
            weekday_wage.NormalEnd = form.NormalEnd.data
            weekday_wage.NightStart = form.NightStart.data
            weekday_wage.NightEnd = form.NightEnd.data
            weekday_wage.MidnightStart = form.MidnightStart.data
            weekday_wage.MidnightEnd = form.MidnightEnd.data
        else:
            # 新規作成
            weekday_wage = HourlyWage(
                NormalTimeWage=form.WeekdayNormalTimeWage.data,
                NightTimeWage=form.WeekdayNightTimeWage.data,
                MidnightTimeWage=form.WeekdayMidnightTimeWage.data,
                DayType=False,

                NormalStart=form.NormalStart.data,
                NormalEnd=form.NormalEnd.data,
                NightStart=form.NightStart.data,
                NightEnd=form.NightEnd.data,
                MidnightStart=form.MidnightStart.data,
                MidnightEnd=form.MidnightEnd.data
            )
            db.session.add(weekday_wage)

        # 土日祝 DayType=True
        holiday_wage = HourlyWage.query.filter_by(DayType=True).first()
        if holiday_wage:
            # 更新処理
            holiday_wage.NormalTimeWage = form.HolidayNormalTimeWage.data
            holiday_wage.NightTimeWage = form.HolidayNightTimeWage.data
            holiday_wage.MidnightTimeWage = form.HolidayMidnightTimeWage.data

            holiday_wage.NormalStart = form.NormalStart.data
            holiday_wage.NormalEnd = form.NormalEnd.data
            holiday_wage.NightStart = form.NightStart.data
            holiday_wage.NightEnd = form.NightEnd.data
            holiday_wage.MidnightStart = form.MidnightStart.data
            holiday_wage.MidnightEnd = form.MidnightEnd.data
        else:
            # 新規作成
            holiday_wage = HourlyWage(
                NormalTimeWage=form.HolidayNormalTimeWage.data,
                NightTimeWage=form.HolidayNightTimeWage.data,
                MidnightTimeWage=form.HolidayMidnightTimeWage.data,
                DayType=True,

                NormalStart=form.NormalStart.data,
                NormalEnd=form.NormalEnd.data,
                NightStart=form.NightStart.data,
                NightEnd=form.NightEnd.data,
                MidnightStart=form.MidnightStart.data,
                MidnightEnd=form.MidnightEnd.data
            )
            db.session.add(holiday_wage)


        db.session.commit()


# Setting　テーブル
        setting = Setting.query.first()
        if setting:
            # 更新処理
            setting.GoalAmount = form.GoalAmount.data
            setting.AchievementDay = form.AchievementDay.data
            
        else:
            # 新規作成
            setting = Setting(
                GoalAmount=form.GoalAmount.data,
                AchievementDay=form.AchievementDay.data
            )
            db.session.add(setting)
        db.session.commit()



        return redirect(url_for('home'))
    # POST以外と「form.validate()がfalse」
    return render_template('home.html', form=form)

# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
    app.run()
