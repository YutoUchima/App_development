from flask import Flask, render_template, request
import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import false

from datetime import time



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

#HourlyWageクラス
class HourlyWage(db.Model):
  __tablename__ = 'hourly_wage'
   
  HourlyWageID = db.Column(db.Integer, primary_key=True, autoincrement=True)
  
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
  
  def __repr__(self):
      return f'<HourlyWage id={self.id}, DayType={self.DayType}, NomalTimeWage={self.NormalTimeWage}, NightTaimeWage={self.NightTimeWage}, MidnightTimeWage={self.MidnightTimeWage}>'



#Shiftクラス
class Shift(db.Model):
 __tablename__ = 'shift'
 
 ShiftID = db.Column(db.Integer, primary_key=True, autoincrement=True)
 ShiftDay = db.Column(db.Date, nullable=False)
 StartTime = db.Column(db.Float, nullable=False)
 EndTime = db.Column(db.Float, nullable=False)
 BreakStartTime = db.Column(db.Float, nullable=False)
 BreakEndTime = db.Column(db.Float, nullable=False)
 DayType = db.Column(db.Integer, nullable=False)
 DailyWage = db.Column(db.Integer,nullable=False)
 Complete = db.Column(db.Boolean, default=False, nullable=False)

 def __repr__(self):
    return f'<Shift id={self.ShiftID}, DayType={self.DayType} >'



#Settingクラス
class Setting(db.Model):
 __tablename__ = 'setting'

 SettingID = db.Column(db.Integer, primary_key=True)
 GoalAmount = db.Column(db.Integer, nullable=False)
 AchievementDay = db.Column(db.Date, nullable=False)

 def __repr__(self):
    return f'<Setting id={self.SettingID}, GoalAmount={self.GoalAmount}, AchievementDay={self.AchievementDay}>'



#Displayクラス
class Display(db.Model):
 __tablename__ = 'display'

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
from forms import WageSettingInfoForm
from forms import ShiftInfoForm


#ホーム
@app.route('/')
def home():
   # 未完了・完了シフト取得
   uncompleted_shifts = Shift.query.filter_by(Complete=False).order_by(Shift.ShiftDay.asc()).all()
   completed_shifts = Shift.query.filter_by(Complete=True).order_by(Shift.ShiftDay.asc()).all()
   # 各設定確認
   setting_exists = Setting.query.first() is not None
   wage_setting_exists = HourlyWage.query.first() is not None
   setting_complete = setting_exists and wage_setting_exists

   return render_template(
       'home.html',
       uncompleted_shifts=uncompleted_shifts,
       completed_shifts=completed_shifts,
       no_setting=not setting_exists,
       wage_setting=not wage_setting_exists,
       setting_complete=setting_complete
   )



# 登録
@app.route('/new_shift', methods=['GET', 'POST'])
def new_shift():
  form = ShiftInfoForm(request.form)
  
  if request.method == 'POST' and form.validate():
      shift = Shift.query.filter_by(Complete=False).first()

      def zennikkyuu(wage: HourlyWage, start: float, end: float) -> int:
          total = 0
          time_zone = [
              (wage.NormalStart, wage.NormalEnd, wage.NormalTimeWage),
              (wage.NightStart, wage.NightEnd, wage.NightTimeWage),
              (wage.MidnightStart, wage.MidnightEnd, wage.MidnightTimeWage)
          ]
          for tz_start, tz_end, wage in time_zone:
              if end <= tz_start:
                  break
              work_start = max(start, tz_start)
              work_end = min(end, tz_end)
              if work_start < work_end:
                  total += (work_end - work_start) * wage
          return int(total)

      def kyuukei(wage: HourlyWage, break_start: float, break_end: float) -> int:
          return zennikkyuu(wage, break_start, break_end)

      wage = HourlyWage.query.filter_by(DayType=(form.DayType.data == 'holiday')).first()

      work_pay = zennikkyuu(wage, float(form.StartTime.data), float(form.EndTime.data))
      break_pay = kyuukei(wage, float(form.BreakStartTime.data), float(form.BreakEndTime.data))
      daily_wage = work_pay - break_pay

      shift = Shift(
          ShiftDay=form.ShiftDay.data,
          StartTime=float(form.StartTime.data),
          EndTime=float(form.EndTime.data),
          BreakStartTime=float(form.BreakStartTime.data),
          BreakEndTime=float(form.BreakEndTime.data),
          DayType=(form.DayType.data == 'holiday'),
          DailyWage=daily_wage,
          Complete=False
      )

      db.session.add(shift)
      db.session.commit()
      return redirect(url_for('home'))
  return render_template('new_shift.html',form=form)



#完了
@app.route('/shift/<int:shift_id>/complete', methods=['POST'])
def complete_shift(shift_id):
  shift = Shift.query.get(shift_id)
  shift.Complete =   True
  db.session.commit()
  return redirect(url_for('home'))



#削除
@app.route('/shift/<int:shift_id>/delete', methods=['POST'])
def delete_shift(shift_id):
  shift = Shift.query.get(shift_id)
  if shift:
      db.session.delete(shift)
      db.session.commit()
  return redirect(url_for('home'))



# 未完了
@app.route('/shift/<int:shift_id>/uncomplete', methods=['POST'])
def uncomplete_shift(shift_id):
  shift = Shift.query.get(shift_id)
  shift.Complete = False
  db.session.commit()
  return redirect(url_for('home'))



#初期設定
@app.route('/setting', methods=['GET','POST'])
def setting():
  form = SettingInfoForm(request.form)
  if request.method == "POST" and form.validate():
      setting = Setting.query.first()
      #すでに設定されていたら上書き更新
      if setting:
          setting.GoalAmount = form.GoalAmount.data
          setting.AchievementDay = form.AchievementDay.data
      #新規設定
      else:
          setting = Setting(
              GoalAmount=form.GoalAmount.data,
              AchievementDay=form.AchievementDay.data
          )
          db.session.add(setting)
      db.session.commit()

      return redirect(url_for('home'))
  return render_template('setting.html', form=form)



#時給設定
@app.route('/wage_setting', methods=['GET','POST'])
def wage_setting():
  form = WageSettingInfoForm(request.form)
  if request.method == "POST" and form.validate():
      #平日
      weekday_wage = HourlyWage.query.filter_by(DayType=False).first()
      #すでに設定されていたら上書き更新
      if weekday_wage:
          weekday_wage.NormalTimeWage = form.WeekdayNormalTimeWage.data
          weekday_wage.NightTimeWage = form.WeekdayNightTimeWage.data
          weekday_wage.MidnightTimeWage = form.WeekdayMidnightTimeWage.data

          weekday_wage.NormalStart = form.NormalStart.data
          weekday_wage.NormalEnd = form.NormalEnd.data
          weekday_wage.NightStart = form.NightStart.data
          weekday_wage.NightEnd = form.NightEnd.data
          weekday_wage.MidnightStart = form.MidnightStart.data
          weekday_wage.MidnightEnd = form.MidnightEnd.data
      #新規設定
      else:
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

      # 土日祝 
      holiday_wage = HourlyWage.query.filter_by(DayType=True).first()
      #すでに設定されていたら上書き更新
      if holiday_wage:
          holiday_wage.NormalTimeWage = form.HolidayNormalTimeWage.data
          holiday_wage.NightTimeWage = form.HolidayNightTimeWage.data
          holiday_wage.MidnightTimeWage = form.HolidayMidnightTimeWage.data

          holiday_wage.NormalStart = form.NormalStart.data
          holiday_wage.NormalEnd = form.NormalEnd.data
          holiday_wage.NightStart = form.NightStart.data
          holiday_wage.NightEnd = form.NightEnd.data
          holiday_wage.MidnightStart = form.MidnightStart.data
          holiday_wage.MidnightEnd = form.MidnightEnd.data
      #新規設定
      else:
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

      return redirect(url_for('home'))
  return render_template('wage_setting.html', form=form)



#金額表示
@app.route('/display', methods=['GET'])
def display():
  current_amount = db.session.query(db.func.sum(Shift.DailyWage)).filter_by(Complete=True).scalar() or 0

  setting = Setting.query.first()
  if setting:
      goal_amount = setting.GoalAmount
      remaining_amount = max(goal_amount - current_amount, 0) 
  else:
      goal_amount = 0
      remaining_amount = 0

  weekday_wage = HourlyWage.query.filter_by(DayType=False).first()
  if weekday_wage and weekday_wage.NormalTimeWage > 0:
      remaining_work_time = round(remaining_amount / weekday_wage.NormalTimeWage, 2)
  else:
      remaining_work_time = 0

  display = Display.query.first()
  if display:
      display.CurrentAmount = current_amount
      display.RemainingAmount = remaining_amount
      display.RemainingWorkTime = remaining_work_time
  else:
      display = Display(
          CurrentAmount=current_amount,
          RemainingAmount=remaining_amount,
          RemainingWorkTime=remaining_work_time
      )
      db.session.add(display)
  db.session.commit()

  return render_template('display.html', display=display,setting=setting)



# float → 時刻の文字列へ変換する
def float_to_time_str(f):
  hour = int(f)
  minute = int((f - hour) * 60)
  return f"{hour:02d}:{minute:02d}"



# テンプレートで使えるように登録
app.jinja_env.filters['time_str'] = float_to_time_str



# ==================================================
# 実行
# ==================================================
if __name__ == '__main__':
  app.run()