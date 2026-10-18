"""Generate a deterministic, explicitly synthetic fitness activity dataset for FitGraph."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

ACTIVITIES = np.array(['Walking','Running','Cycling','Yoga','Weight Training','HIIT','Swimming','Dancing','Basketball','Tennis'])
INTENSITIES = np.array(['Low','Moderate','High'])

def generate(output: str, participants: int = 600, year: int = 2025, seed: int = 42):
    rng = np.random.default_rng(seed)
    people=[]
    for pid in range(1, participants+1):
        age=int(np.clip(rng.normal(34, 11),18, seventy:=75))
        gender=rng.choice(['Female','Male','Non-binary'],p=[.48,.49,.03])
        height=float(np.clip(rng.normal(170 if gender=='Male' else 163,8),145,202))
        weight=float(np.clip(rng.normal(76 if gender=='Male' else 65,14),42,145))
        fitness=float(np.clip(rng.normal(5.8,1.8),1,10))
        preferred=str(rng.choice(ACTIVITIES,p=[.19,.14,.11,.10,.14,.08,.06,.06,.06,.06]))
        consistency=float(rng.beta(2.2,3.0))
        churn_month=int(rng.integers(4,11)) if rng.random()<0.22 else 13
        people.append((pid,age,gender,height,weight,fitness,preferred,consistency,churn_month))
    rows=[]
    dates=pd.date_range(f'{year}-01-01',f'{year}-12-31',freq='D')
    for pid,age,gender,height,weight,fitness,preferred,consistency,churn_month in people:
        active_prob=.045 + consistency*.42
        for date in dates:
            # Weekend boost and a gentle seasonal signal; all data is simulated.
            weekend=1.18 if date.dayofweek>=5 else 1.0
            seasonal=1.0 + .12*np.sin((date.dayofyear/365)*2*np.pi)
            churn_factor = 0.10 if date.month >= churn_month else 1.0
            if rng.random() > min(.68,active_prob*weekend*seasonal*churn_factor):
                continue
            activity=preferred if rng.random()<.56 else str(rng.choice(ACTIVITIES))
            base={'Walking':38,'Running':34,'Cycling':48,'Yoga':42,'Weight Training':52,'HIIT':28,'Swimming':40,'Dancing':45,'Basketball':50,'Tennis':46}[activity]
            duration=float(np.clip(rng.normal(base,12),12,120))
            intensity=str(rng.choice(INTENSITIES,p=[.24,.51,.25]))
            multiplier={'Low':.78,'Moderate':1.0,'High':1.35}[intensity]
            calories=float(max(40, duration * (weight/70) * multiplier * rng.normal(5.1, .45)))
            resting=float(np.clip(rng.normal(72-(fitness-5)*1.5,7),48,100))
            heart=float(np.clip(resting + {'Low':22,'Moderate':38,'High':55}[intensity]+rng.normal(0,7),80,195))
            sleep=float(np.clip(rng.normal(7.25 - max(0,age-45)*.012 - (1-consistency)*.45, .85),3.5,10.5))
            stress=float(np.clip(rng.normal(5.0 + (6.5-sleep)*.55 - (fitness-5)*.25,1.6),1,10))
            steps=int(np.clip(rng.normal(6800 + duration*32 + (fitness-5)*350,1900),500,24000))
            hydration=float(np.clip(rng.normal(2.1 + duration*.012, .55),.5,5.5))
            bmi=weight/((height/100)**2)
            systolic=float(np.clip(rng.normal(118+(bmi-24)*.7,10),88,180))
            diastolic=float(np.clip(rng.normal(77+(bmi-24)*.35,7),52,115))
            rows.append([pid,date.date().isoformat(),age,gender,round(height,1),round(weight,1),activity,round(duration,1),intensity,round(calories,1),round(heart,1),round(sleep,2),round(stress,1),steps,round(hydration,2),round(bmi,2),round(resting,1),round(systolic,1),round(diastolic,1),rng.choice(['None','Asthma','Hypertension','Diabetes','None','None'],p=[.58,.08,.08,.05,.12,.09]),rng.choice(['Never','Former','Current'],p=[.76,.15,.09]),round(fitness,2)])
    cols=['participant_id','date','age','gender','height_cm','weight_kg','activity_type','duration_minutes','intensity','calories_burned','avg_heart_rate','hours_sleep','stress_level','daily_steps','hydration_level','bmi','resting_heart_rate','blood_pressure_systolic','blood_pressure_diastolic','health_condition','smoking_status','fitness_level']
    df=pd.DataFrame(rows,columns=cols).sort_values(['date','participant_id'])
    path=Path(output); path.parent.mkdir(parents=True,exist_ok=True); df.to_csv(path,index=False)
    print(f'Generated {len(df):,} synthetic workout records for {df.participant_id.nunique():,} participants: {path}')
    return df

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--output',default='data/raw/synthetic_fitness_dataset.csv'); p.add_argument('--participants',type=int,default=600); p.add_argument('--year',type=int,default=2025); p.add_argument('--seed',type=int,default=42); a=p.parse_args()
    generate(a.output,a.participants,a.year,a.seed)
