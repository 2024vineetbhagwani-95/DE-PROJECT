"""Additional behavioral analytics derived from the synthetic activity records."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

def build_behavior_insights(df: pd.DataFrame, output: Path):
    x=df.copy(); x['date_dt']=pd.to_datetime(x['date']); x['month']=x.date_dt.dt.to_period('M').astype(str)
    x['week']=x.date_dt.dt.to_period('W').astype(str)
    x['load_points']=x.duration_minutes * x.intensity.map({'Low':0.7,'Moderate':1.0,'High':1.5}).fillna(1.0)
    # Weekly guideline is a simple project metric (150 active minutes), not medical advice.
    weekly=x.groupby(['participant_id','week'],as_index=False).agg(active_minutes=('duration_minutes','sum'),sessions=('date','size'))
    weekly['goal_met']=weekly.active_minutes>=150
    goal=[{'label':'Below 75 min','participants':int((weekly.active_minutes<75).sum())},
          {'label':'75–149 min','participants':int(((weekly.active_minutes>=75)&(weekly.active_minutes<150)).sum())},
          {'label':'150+ min','participants':int((weekly.active_minutes>=150).sum())}]
    goal_summary={'weekly_goal_minutes':150,'weeks_observed':int(weekly.week.nunique()),'goal_met_rate':round(float(weekly.goal_met.mean()*100),1),'bands':goal}
    p=x.groupby('participant_id').agg(sessions=('date','size'),active_days=('date','nunique'),avg_sleep=('hours_sleep','mean'),avg_stress=('stress_level','mean'),avg_hr=('avg_heart_rate','mean'),avg_fitness=('fitness_level','mean'),total_minutes=('duration_minutes','sum')).reset_index()
    p['active_day_rate']=p.active_days/365*100
    p['consistency_band']=pd.cut(p.active_day_rate,[-1,8,18,35,101],labels=['Occasional','Building','Consistent','Highly consistent']).astype(str)
    consistency=p.groupby('consistency_band',observed=False).agg(participants=('participant_id','nunique'),avg_sessions=('sessions','mean')).reset_index()
    consistency_data=[{'band':r.consistency_band,'participants':int(r.participants),'avg_sessions':round(float(r.avg_sessions),1) if pd.notna(r.avg_sessions) else 0} for r in consistency.itertuples()]
    # Recovery score is an illustrative composite based on sleep, stress and heart rate.
    p['recovery_score']=np.clip(60+(p.avg_sleep-7)*12-(p.avg_stress-5)*5-(p.avg_hr-120)*.2,0,100)
    p['recovery_band']=pd.cut(p.recovery_score,[-1,45,58,72,101],labels=['Needs attention','Fair','Good','Strong']).astype(str)
    recovery=p.groupby('recovery_band',observed=False).agg(participants=('participant_id','nunique'),avg_sleep=('avg_sleep','mean'),avg_stress=('avg_stress','mean')).reset_index()
    recovery_data=[{'band':r.recovery_band,'participants':int(r.participants),'avg_sleep':round(float(r.avg_sleep),2) if pd.notna(r.avg_sleep) else 0,'avg_stress':round(float(r.avg_stress),2) if pd.notna(r.avg_stress) else 0} for r in recovery.itertuples()]
    # Retention: share of participants active in the first month who return in each later month.
    active_by_month={m:set(g.participant_id.astype(int)) for m,g in x.groupby('month')}
    months=sorted(active_by_month)
    cohort=active_by_month.get(months[0],set()) if months else set()
    retention=[]
    for m in months:
        active=active_by_month[m]
        retention.append({'month':m,'month_label':pd.Period(m).strftime('%b'),'active_participants':len(active),'cohort_return_rate':round(100*len(cohort&active)/max(1,len(cohort)),1)})
    # Activity mix by intensity and activity type, plus a monthly load curve.
    load_month=x.groupby('month',as_index=False).agg(avg_load=('load_points','mean'),total_load=('load_points','sum'),sessions=('date','size'))
    load_data=[{'month':r.month,'month_label':pd.Period(r.month).strftime('%b'),'avg_load':round(float(r.avg_load),1),'total_load':round(float(r.total_load),1),'sessions':int(r.sessions)} for r in load_month.itertuples()]
    activity_eff=x.groupby('activity_type',as_index=False).agg(sessions=('date','size'),avg_duration=('duration_minutes','mean'),avg_calories=('calories_burned','mean'),avg_load=('load_points','mean')).sort_values('sessions',ascending=False)
    activity_data=[{'activity_type':r.activity_type,'sessions':int(r.sessions),'avg_duration':round(float(r.avg_duration),1),'avg_calories':round(float(r.avg_calories),1),'avg_load':round(float(r.avg_load),1)} for r in activity_eff.itertuples()]
    result={'goal_adherence':goal_summary,'consistency':consistency_data,'recovery':recovery_data,'retention':retention,'training_load':load_data,'activity_efficiency':activity_data,
            'definitions':{'weekly_goal':'150 active minutes per participant-week; simplified project benchmark.','recovery_score':'Illustrative composite derived from sleep, stress and heart-rate averages; not a medical measure.','retention':'Monthly return rate relative to participants active in the first month.'}}
    (output/'behavior_insights.json').write_text(json.dumps(result,indent=2))
    # Export user-level derived features for an explainable data engineering artifact.
    p[['participant_id','sessions','active_days','active_day_rate','consistency_band','avg_sleep','avg_stress','avg_hr','recovery_score','recovery_band','total_minutes']].round(2).to_csv(output/'participant_behavior_features.csv',index=False)
    return result
