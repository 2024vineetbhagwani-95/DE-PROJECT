import React, { useEffect, useMemo, useState } from 'react'
import { Activity, Users, Flame, Footprints, Moon, TrendingUp, LayoutDashboard, Workflow, Search, RefreshCw, ChevronRight, HeartPulse, CircleHelp, Database, ArrowUpRight, Clock3, CheckCircle2, AlertTriangle, Zap, CalendarDays, Gauge, Timer } from 'lucide-react'
import { ResponsiveContainer, AreaChart, Area, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'

const API = import.meta.env.VITE_API_URL || ''
const colors = ['#7c9cff','#45d6b4','#f5b85d','#c59aff','#ff8e9e','#6dc8f0','#a4e27b','#ffb86b','#8a9cff','#f28ad2']
async function get(path) { const r = await fetch(`${API}${path}`); if (!r.ok) throw new Error(`API request failed: ${path}`); return r.json() }
const fmt = n => Number(n || 0).toLocaleString('en-US')
const dec = (n,d=1) => Number(n || 0).toFixed(d)

function Sidebar({page,setPage}) {
  const links = [
    {id:'overview',label:'Overview',icon:LayoutDashboard},
    {id:'network',label:'Behavior insights',icon:TrendingUp},
    {id:'participants',label:'Participants',icon:Users},
    {id:'pipeline',label:'Data pipeline',icon:Workflow},
  ]
  return <aside className="sidebar">
    <div className="brand"><div className="brand-icon"><Activity size={22}/></div><div><strong>fitgraph<span>.</span></strong><small>DATA INTELLIGENCE</small></div></div>
    <div className="workspace-label">WORKSPACE</div>
    <nav>{links.map(x=><button key={x.id} className={`nav-item ${page===x.id?'active':''}`} onClick={()=>setPage(x.id)}><x.icon size={18}/><span>{x.label}</span>{page===x.id&&<ChevronRight size={15} className="nav-arrow"/>}</button>)}</nav>
    <div className="sidebar-bottom"><div className="status-dot"></div><div><b>Analytics engine</b><small>Dataset loaded</small></div><span className="live-pill">READY</span></div>
    <div className="sidebar-foot">FITGRAPH / DE PROJECT<br/>Version 1.0.0</div>
  </aside>
}

function Header({page}) {
  const titles = {overview:['Overview','Your fitness data, transformed into insights.'],network:['Behavior insights','Explore adherence, consistency, recovery and participant retention.'],participants:['Participants','Search participant profiles and compare activity patterns.'],pipeline:['Data pipeline','Inspect ETL stages, data quality, and warehouse readiness.']}
  return <header className="topbar"><div><div className="crumb">FITGRAPH <span>/</span> {page.toUpperCase()}</div><h1>{titles[page][0]}</h1><p>{titles[page][1]}</p></div><div className="top-actions"><div className="dataset-badge"><span className="green-dot"></span> SYNTHETIC DATASET</div><div className="avatar">FG</div></div></header>
}

function StatCard({title,value,sub,icon:Icon,accent}) {
  return <div className="stat-card"><div className={`stat-icon ${accent}`}><Icon size={19}/></div><div className="stat-title">{title}</div><div className="stat-value">{value}</div><div className="stat-sub">{sub}</div></div>
}

function Overview({summary,activities,monthly,intensity,weekday}) {
  const totalAct = activities.reduce((s,a)=>s+a.workouts,0)
  return <div className="page-content">
    <section className="welcome-hero"><div className="hero-orb hero-orb-one"/><div className="hero-orb hero-orb-two"/><div className="hero-copy"><span className="eyebrow"><span className="green-dot"/> FITNESS DATA INTELLIGENCE</span><h2>Turn activity into<br/><em>meaningful insights.</em></h2><p>Explore workout patterns, participant networks and health trends — all in one clear view.</p><div className="hero-foot"><span><Activity size={14}/> 687K+ activity records</span><span><Users size={14}/> 3,000 participants</span></div></div><div className="hero-quote"><span className="quote-mark">“</span><p>A healthier world is a more connected world.</p><div className="quote-line"/></div></section>
    <div className="section-heading"><div><h2>Performance snapshot</h2><p>Aggregated across the source dataset</p></div><span className="period-pill"><Clock3 size={14}/> Jan – Dec 2024</span></div>
    <div className="stats-grid">
      <StatCard title="Activity records" value={fmt(summary.records)} sub={`${fmt(summary.participants)} unique participants`} icon={Activity} accent="blue"/>
      <StatCard title="Workout categories" value={fmt(summary.activity_types)} sub="Distinct activity types" icon={HeartPulse} accent="mint"/>
      <StatCard title="Avg. session duration" value={`${dec(summary.avg_duration)} min`} sub="Across recorded activities" icon={Clock3} accent="amber"/>
      <StatCard title="Avg. daily steps" value={fmt(summary.avg_steps)} sub="Mean recorded steps" icon={Footprints} accent="violet"/>
    </div>
    <div className="charts-grid">
      <section className="panel trend-panel"><div className="panel-head"><div><h3>Activity volume</h3><p>Recorded workout sessions by month</p></div><span className="mini-tag"><span className="green-dot"/> DATA LOADED</span></div>
        <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={monthly} margin={{top:10,right:12,left:-18,bottom:0}}><defs><linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#7c9cff" stopOpacity={0.3}/><stop offset="100%" stopColor="#7c9cff" stopOpacity={0.01}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" stroke="#273243" vertical={false}/><XAxis dataKey="month" tick={{fill:'#8290a4',fontSize:11}} tickLine={false} axisLine={false}/><YAxis tick={{fill:'#8290a4',fontSize:11}} tickLine={false} axisLine={false}/><Tooltip contentStyle={{background:'#151f2d',border:'1px solid #2a394d',borderRadius:10,color:'#eef3fc'}}/><Area type="monotone" dataKey="workouts" stroke="#7c9cff" strokeWidth={2.5} fill="url(#areaFill)" activeDot={{r:5}}/></AreaChart></ResponsiveContainer></div>
      </section>
      <section className="panel activity-panel"><div className="panel-head"><div><h3>Workout mix</h3><p>Records by activity category</p></div><span className="chart-total">{fmt(totalAct)}<small> records</small></span></div>
        <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><BarChart data={activities.slice(0,7)} layout="vertical" margin={{top:0,right:12,left:8,bottom:0}}><CartesianGrid strokeDasharray="3 3" stroke="#273243" horizontal={false}/><XAxis type="number" tick={{fill:'#8290a4',fontSize:10}} tickLine={false} axisLine={false}/><YAxis dataKey="activity_type" type="category" width={100} tick={{fill:'#aab5c6',fontSize:11}} tickLine={false} axisLine={false}/><Tooltip contentStyle={{background:'#151f2d',border:'1px solid #2a394d',borderRadius:10,color:'#eef3fc'}}/><Bar dataKey="workouts" radius={[0,5,5,0]}>{activities.slice(0,7).map((a,i)=><Cell key={a.activity_type} fill={colors[i%colors.length]}/>)}</Bar></BarChart></ResponsiveContainer></div>
      </section>
    </div>
    <div className="bottom-grid">
      <section className="panel"><div className="panel-head"><div><h3>Weekly rhythm</h3><p>When activities are recorded</p></div></div><div className="chart-wrap short"><ResponsiveContainer width="100%" height="100%"><BarChart data={weekday} margin={{top:10,right:5,left:-20,bottom:0}}><CartesianGrid strokeDasharray="3 3" stroke="#273243" vertical={false}/><XAxis dataKey="weekday" tickFormatter={v=>v.slice(0,3)} tick={{fill:'#8290a4',fontSize:10}} tickLine={false} axisLine={false}/><YAxis tick={{fill:'#8290a4',fontSize:10}} tickLine={false} axisLine={false}/><Tooltip contentStyle={{background:'#151f2d',border:'1px solid #2a394d',borderRadius:10,color:'#eef3fc'}}/><Bar dataKey="workouts" fill="#45d6b4" radius={[4,4,0,0]}/></BarChart></ResponsiveContainer></div></section>
      <section className="panel"><div className="panel-head"><div><h3>Training intensity</h3><p>Distribution across recorded sessions</p></div></div><div className="intensity-layout"><div className="donut"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={intensity} dataKey="workouts" nameKey="intensity" innerRadius={48} outerRadius={68} paddingAngle={4} stroke="none">{intensity.map((a,i)=><Cell key={a.intensity} fill={colors[i+1]}/>)}</Pie><Tooltip contentStyle={{background:'#151f2d',border:'1px solid #2a394d',borderRadius:10,color:'#eef3fc'}}/></PieChart></ResponsiveContainer></div><div className="legend">{intensity.map((x,i)=><div className="legend-row" key={x.intensity}><span style={{background:colors[i+1]}}></span><label>{x.intensity}</label><b>{(100*x.workouts/totalAct).toFixed(1)}%</b></div>)}</div></div></section>
    </div>
    <div className="data-note"><CircleHelp size={16}/><div><b>Data interpretation</b><span>Metrics describe the supplied dataset, not clinical guidance. The source has many missing health-condition values; missing values are treated as unknown.</span></div></div>
  </div>
}

function TrendsPage({summary,monthly,weekday,activities}) {
  const [metric,setMetric]=useState('workouts')
  const [selectedDay,setSelectedDay]=useState(null)
  const sortedDays=[...weekday].sort((a,b)=>['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].indexOf(a.weekday)-['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'].indexOf(b.weekday))
  const sortedActivities=[...activities].sort((a,b)=>b.workouts-a.workouts)
  const total=sortedActivities.reduce((n,x)=>n+x.workouts,0)||1
  const busiest=[...sortedDays].sort((a,b)=>b.workouts-a.workouts)[0]
  const quietest=[...sortedDays].sort((a,b)=>a.workouts-b.workouts)[0]
  const peak=[...monthly].sort((a,b)=>b.workouts-a.workouts)[0]
  const metricConfig={workouts:{label:'Workout sessions',field:'workouts',suffix:' sessions'},calories:{label:'Calories recorded',field:'calories',suffix:' calories'},duration:{label:'Average session duration',field:'avg_duration',suffix:' min'}}
  const config=metricConfig[metric]
  const monthlyData=monthly.map(m=>({...m,monthLabel:new Date(`${m.month}-01T00:00:00`).toLocaleDateString('en-US',{month:'short'}),metricValue:Number(m[config.field]||0)}))
  return <div className="page-content simple-behavior-page">
    <section className="simple-page-intro">
      <div><span className="eyebrow"><span className="green-dot"/> FITNESS ACTIVITY · 2024</span><h2>Understand the workout habits.</h2><p>Three simple views of when people exercise, what they choose, and how activity changes through the year.</p></div>
      <div className="intro-fact"><span>DATASET</span><strong>{fmt(summary.participants)}</strong><small>participants represented</small></div>
    </section>

    <section className="panel simple-chart-panel">
      <div className="simple-panel-heading"><div><span className="section-kicker">01 · WHEN</span><h3>Which day is busiest?</h3><p>Each bar is the number of recorded sessions for that day.</p></div><div className="insight-chip"><span>Most active</span><strong>{busiest?.weekday||'—'}</strong></div></div>
      <div className="simple-chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={sortedDays} margin={{top:16,right:12,left:0,bottom:0}} onClick={e=>{if(e?.activePayload?.[0])setSelectedDay(e.activePayload[0].payload)}}><CartesianGrid strokeDasharray="3 3" stroke="#273243" vertical={false}/><XAxis dataKey="weekday" tickFormatter={v=>v.slice(0,3)} tick={{fill:'#a8b4cc',fontSize:12}} tickLine={false} axisLine={false}/><YAxis tickFormatter={v=>`${Math.round(v/1000)}k`} tick={{fill:'#8290a4',fontSize:11}} tickLine={false} axisLine={false} width={44}/><Tooltip formatter={v=>[fmt(v),'Recorded sessions']} labelFormatter={v=>v} contentStyle={{background:'#151b2d',border:'1px solid #303a58',borderRadius:10,color:'#eef3fc'}}/><Bar dataKey="workouts" name="Recorded sessions" fill="#9277f5" radius={[6,6,0,0]} cursor="pointer" activeBar={{fill:'#45d6b4'}}/></BarChart></ResponsiveContainer></div>
      <div className="plain-insight-row"><div><span className="insight-dot purple-dot"/><span>Click a bar to inspect a day</span></div>{selectedDay?<strong>{selectedDay.weekday}: {fmt(selectedDay.workouts)} sessions</strong>:<strong>Quietest: {quietest?.weekday||'—'}</strong>}</div>
    </section>

    <section className="panel simple-chart-panel">
      <div className="simple-panel-heading"><div><span className="section-kicker">02 · WHAT</span><h3>Which workouts are most common?</h3><p>Activities are ranked from most recorded to least recorded.</p></div><span className="small-neutral-pill">{activities.length} workout types</span></div>
      <div className="ranked-activities">{sortedActivities.map((a,i)=><div className="ranked-activity" key={a.activity_type}><span className="rank-number">{String(i+1).padStart(2,'0')}</span><div className="rank-main"><div className="rank-label"><strong>{a.activity_type}</strong><span>{fmt(a.workouts)} sessions · {(100*a.workouts/total).toFixed(1)}%</span></div><div className="rank-track"><span style={{width:`${100*a.workouts/Math.max(sortedActivities[0]?.workouts||1,1)}%`}}/></div></div></div>)}</div>
    </section>

    <section className="panel simple-chart-panel">
      <div className="simple-panel-heading"><div><span className="section-kicker">03 · OVER TIME</span><h3>How does activity change by month?</h3><p>Compare the year using one clear trend line.</p></div><select className="filter-select" value={metric} onChange={e=>setMetric(e.target.value)}><option value="workouts">Workout sessions</option><option value="calories">Calories recorded</option><option value="duration">Average duration</option></select></div>
      <div className="simple-chart monthly-simple-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={monthlyData} margin={{top:15,right:18,left:0,bottom:0}}><CartesianGrid strokeDasharray="3 3" stroke="#273243" vertical={false}/><XAxis dataKey="monthLabel" tick={{fill:'#a8b4cc',fontSize:12}} tickLine={false} axisLine={false}/><YAxis tickFormatter={v=>metric==='duration'?`${Math.round(v)}m`:`${Math.round(v/1000)}k`} tick={{fill:'#8290a4',fontSize:11}} tickLine={false} axisLine={false} width={44}/><Tooltip formatter={v=>[metric==='duration'?`${dec(v)} min`:fmt(Math.round(v)),config.label]} contentStyle={{background:'#151b2d',border:'1px solid #303a58',borderRadius:10,color:'#eef3fc'}}/><Line type="monotone" dataKey="metricValue" name={config.label} stroke="#45d6b4" strokeWidth={3} dot={{r:3,fill:'#45d6b4',strokeWidth:0}} activeDot={{r:6}}/></LineChart></ResponsiveContainer></div>
      <div className="plain-insight-row"><div><span className="insight-dot mint-dot"/><span>{config.label}</span></div><strong>Highest session month: {peak?new Date(`${peak.month}-01T00:00:00`).toLocaleDateString('en-US',{month:'long'}):'—'}</strong></div>
    </section>
    <p className="simple-data-note"><CircleHelp size={15}/> These charts describe the supplied dataset only. Recorded activity may not represent every real-world workout.</p>
  </div>
}

function ParticipantsPage() {
  const [q,setQ]=useState(''), [activity,setActivity]=useState('All'), [items,setItems]=useState([]), [total,setTotal]=useState(0), [loading,setLoading]=useState(false), [selected,setSelected]=useState(null)
  useEffect(()=>{setLoading(true);get(`/api/participants?limit=500&q=${encodeURIComponent(q)}&activity=${encodeURIComponent(activity)}`).then(d=>{setItems(d.items);setTotal(d.total)}).catch(console.error).finally(()=>setLoading(false))},[q,activity])
  const types = ['All',...new Set(items.map(x=>x.dominant_activity))].sort((a,b)=>a==='All'?-1:a.localeCompare(b))
  return <div className="page-content">
    <div className="section-heading"><div><h2>Participant directory</h2><p>Aggregated profile metrics derived from daily activity records.</p></div><span className="period-pill"><Users size={14}/>{fmt(total)} profiles</span></div>
    <section className="panel"><div className="table-tools"><div className="search-box"><Search size={16}/><input placeholder="Search participant ID…" value={q} onChange={e=>setQ(e.target.value)}/></div><select className="filter-select" value={activity} onChange={e=>setActivity(e.target.value)}>{types.map(x=><option key={x}>{x}</option>)}</select></div>
      <div className="table-wrap"><table><thead><tr><th>Participant</th><th>Preferred activity</th><th>Workouts</th><th>Avg. duration</th><th>Avg. steps</th><th>Avg. sleep</th><th>Fitness score</th><th></th></tr></thead><tbody>
        {items.map(x=><tr key={x.participant_id} onClick={()=>setSelected(x)} className="click-row"><td><div className="participant-cell"><div className="person-avatar">{String(x.participant_id).slice(-2)}</div><b>Participant #{x.participant_id}</b></div></td><td><span className="activity-pill">{x.dominant_activity}</span></td><td>{fmt(x.workouts)}</td><td>{dec(x.avg_duration)} min</td><td>{fmt(x.avg_steps)}</td><td>{dec(x.avg_sleep)} h</td><td>{dec(x.avg_fitness_level,2)}</td><td><ChevronRight size={15}/></td></tr>)}
      </tbody></table>{loading&&<div className="loading">Loading participants…</div>}{!loading&&!items.length&&<div className="loading">No participants match this search.</div>}</div>
      <div className="table-foot">Showing {fmt(items.length)} of {fmt(total)} matching participant profiles · Select a row for details</div>
    </section>
    {selected&&<section className="panel profile-detail"><div className="panel-head"><div><h3>Participant #{selected.participant_id}</h3><p>Aggregated from all available records for this participant</p></div><button className="secondary-btn" onClick={()=>setSelected(null)}>Close</button></div><div className="profile-grid">{[['Age',selected.age],['Gender',selected.gender],['Dominant activity',selected.dominant_activity],['Intensity preference',selected.avg_intensity],['Avg. heart rate',`${dec(selected.avg_heart_rate)} bpm`],['Avg. stress',dec(selected.avg_stress)],['Avg. hydration',`${dec(selected.avg_hydration)} L`],['Avg. calories field',dec(selected.avg_calories,2)]].map(([k,v])=><div key={k}><small>{k}</small><b>{v??'Unknown'}</b></div>)}</div></section>}
  </div>
}

function PipelinePage() {
  const [data,setData]=useState(null),[error,setError]=useState('')
  const reload=()=>get('/api/pipeline/status').then(setData).catch(e=>setError(e.message))
  useEffect(()=>{reload()},[])
  const stages=data?.stages||[]
  return <div className="page-content">
    <div className="section-heading"><div><h2>Pipeline observability</h2><p>ETL stage status and source data quality.</p></div><button className="secondary-btn" onClick={reload}><RefreshCw size={14}/> Refresh status</button></div>
    {error&&<div className="data-note"><AlertTriangle size={16}/><div>{error}</div></div>}
    <div className="pipeline-banner"><div className="pipeline-mark"><Workflow size={24}/></div><div><small>PIPELINE SNAPSHOT</small><h2>FitGraph Fitness ETL</h2><p>CSV ingestion → validation & transform → graph analytics → warehouse load</p></div><span className="success-pill"><CheckCircle2 size={14}/> {data?.status||'Loading'}</span></div>
    <div className="stage-list">{stages.map((s,i)=><div className="stage-row" key={s.name}><div className={`stage-number ${s.status==='success'?'done':''}`}>{s.status==='success'?<CheckCircle2 size={17}/>:i+1}</div><div className="stage-info"><b>{s.name}</b><span>{s.detail}</span></div><span className={`stage-status ${s.status}`}>{s.status}</span></div>)}</div>
    <div className="bottom-grid">
      <section className="panel"><div className="panel-head"><div><h3>Data quality report</h3><p>Checks run on the source CSV</p></div><Database size={18} className="muted-icon"/></div><div className="quality-list">
        {[['Input records',fmt(data?.quality_report?.rows_in ?? data?.source_records)],['Output records',fmt(data?.quality_report?.rows_out ?? data?.source_records)],['Critical nulls remaining',fmt(data?.quality_report?.critical_nulls_remaining ?? 0)],['Optional health-condition nulls',fmt(data?.quality_report?.health_condition_nulls_preserved ?? 490275)],['Duplicate source rows',fmt(data?.quality_report?.duplicate_rows_removed ?? 0)]].map(([k,v])=><div key={k}><span>{k}</span><b>{v}</b></div>)}
      </div></section>
      <section className="panel"><div className="panel-head"><div><h3>Data lineage</h3><p>From source to insights</p></div></div><div className="lineage">
        {['Synthetic CSV','Pandas ETL','PostgreSQL warehouse','Behavior analytics','FastAPI + React'].map((x,i)=><div className="lineage-step" key={x}><span>{i+1}</span><b>{x}</b>{i<4&&<ChevronRight size={15}/>}</div>)}
      </div><div className="note-small">PostgreSQL loading is available when DATABASE_URL is configured and the ETL is run. The bundled dashboard uses precomputed analytics for fast startup.</div></section>
    </div>
  </div>
}

function BehaviorInsightsPage() {
  const [data,setData]=useState(null), [error,setError]=useState('')
  useEffect(()=>{get('/api/insights/behavior').then(setData).catch(e=>setError(e.message))},[])
  if(error) return <div className="page-content"><div className="data-note"><AlertTriangle size={16}/><div>Behavior analytics are not available yet. Run the synthetic ETL pipeline, then restart the API.</div></div></div>
  if(!data) return <div className="loading full">Loading behavior insights…</div>
  const maxGoal=Math.max(1,...data.goal_adherence.bands.map(x=>x.participants))
  const maxCons=Math.max(1,...data.consistency.map(x=>x.participants))
  const maxRecovery=Math.max(1,...data.recovery.map(x=>x.participants))
  const topActivities=data.activity_efficiency.slice(0,7)
  return <div className="page-content behavior-page">
    <section className="simple-page-intro"><div><span className="eyebrow"><span className="green-dot"/> SYNTHETIC FITNESS LAB · 2025</span><h2>What helps people stay active?</h2><p>Move beyond activity counts: explore goal progress, consistency, recovery signals and participant return rates.</p></div><div className="intro-fact"><span>SIMULATED PROFILES</span><strong>{fmt(data.consistency.reduce((n,x)=>n+x.participants,0))}</strong><small>fictional participants</small></div></section>
    <div className="behavior-grid">
      <section className="panel behavior-panel"><div className="simple-panel-heading"><div><span className="section-kicker">01 · GOAL PROGRESS</span><h3>Weekly activity goal</h3><p>How many participant-weeks fall into each active-minute band?</p></div><span className="small-neutral-pill">150 min benchmark</span></div><div className="behavior-bars">{data.goal_adherence.bands.map((x,i)=><div className="behavior-bar-row" key={x.label}><div className="behavior-bar-label"><span>{x.label}</span><b>{fmt(x.participants)}</b></div><div className="rank-track"><span className={`goal-fill fill-${i}`} style={{width:`${100*x.participants/maxGoal}%`}}/></div></div>)}</div><div className="behavior-foot">{data.goal_adherence.goal_met_rate}% of participant-weeks met the 150-minute benchmark.</div></section>
      <section className="panel behavior-panel"><div className="simple-panel-heading"><div><span className="section-kicker">02 · CONSISTENCY</span><h3>How often do they show up?</h3><p>Profiles grouped by the share of days with a recorded workout.</p></div></div><div className="behavior-bars">{data.consistency.map((x,i)=><div className="behavior-bar-row" key={x.band}><div className="behavior-bar-label"><span>{x.band}</span><b>{fmt(x.participants)}</b></div><div className="rank-track"><span className={`goal-fill fill-${i%3}`} style={{width:`${100*x.participants/maxCons}%`}}/></div><small>Average {x.avg_sessions} sessions per participant</small></div>)}</div></section>
      <section className="panel behavior-panel"><div className="simple-panel-heading"><div><span className="section-kicker">03 · RECOVERY SIGNAL</span><h3>Sleep and stress snapshot</h3><p>A simple, non-clinical grouping based on sleep, stress and heart rate.</p></div></div><div className="recovery-list">{data.recovery.map((x,i)=><div className="recovery-row" key={x.band}><div><span className={`recovery-dot fill-${i%3}`}/><b>{x.band}</b><small>{fmt(x.participants)} participants</small></div><div className="recovery-stats"><span>{x.avg_sleep} h <small>avg sleep</small></span><span>{x.avg_stress}/10 <small>avg stress</small></span></div></div>)}</div></section>
      <section className="panel behavior-panel"><div className="simple-panel-heading"><div><span className="section-kicker">04 · RETENTION</span><h3>Do participants come back?</h3><p>Monthly active participants compared with the first month’s cohort.</p></div></div><div className="behavior-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={data.retention} margin={{top:12,right:10,left:-16,bottom:0}}><CartesianGrid strokeDasharray="3 3" stroke="#273243" vertical={false}/><XAxis dataKey="month_label" tick={{fill:'#9aa7bf',fontSize:11}} tickLine={false} axisLine={false}/><YAxis unit="%" domain={[0,100]} tick={{fill:'#8290a4',fontSize:10}} tickLine={false} axisLine={false}/><Tooltip formatter={(v,n)=>[n==='cohort_return_rate'?`${v}%`:fmt(v),n==='cohort_return_rate'?'First-month cohort returning':'Active participants']} contentStyle={{background:'#151b2d',border:'1px solid #303a58',borderRadius:10,color:'#eef3fc'}}/><Line type="monotone" dataKey="cohort_return_rate" stroke="#45d6b4" strokeWidth={3} dot={{r:3,fill:'#45d6b4'}}/></LineChart></ResponsiveContainer></div></section>
      <section className="panel behavior-panel"><div className="simple-panel-heading"><div><span className="section-kicker">05 · TRAINING LOAD</span><h3>Monthly training load</h3><p>Session duration weighted by intensity, shown as a trend.</p></div></div><div className="behavior-chart"><ResponsiveContainer width="100%" height="100%"><AreaChart data={data.training_load} margin={{top:12,right:10,left:-12,bottom:0}}><defs><linearGradient id="loadFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#9277f5" stopOpacity={.32}/><stop offset="100%" stopColor="#9277f5" stopOpacity={.02}/></linearGradient></defs><CartesianGrid strokeDasharray="3 3" stroke="#273243" vertical={false}/><XAxis dataKey="month_label" tick={{fill:'#9aa7bf',fontSize:11}} tickLine={false} axisLine={false}/><YAxis tick={{fill:'#8290a4',fontSize:10}} tickLine={false} axisLine={false}/><Tooltip contentStyle={{background:'#151b2d',border:'1px solid #303a58',borderRadius:10,color:'#eef3fc'}}/><Area type="monotone" dataKey="avg_load" name="Average load points" stroke="#9277f5" strokeWidth={2.5} fill="url(#loadFill)"/></AreaChart></ResponsiveContainer></div></section>
      <section className="panel behavior-panel"><div className="simple-panel-heading"><div><span className="section-kicker">06 · ACTIVITY EFFICIENCY</span><h3>Calories per session</h3><p>Compare average calories recorded across popular activity types.</p></div></div><div className="behavior-chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={topActivities} layout="vertical" margin={{top:4,right:12,left:8,bottom:0}}><CartesianGrid strokeDasharray="3 3" stroke="#273243" horizontal={false}/><XAxis type="number" tick={{fill:'#8290a4',fontSize:10}} tickLine={false} axisLine={false}/><YAxis type="category" dataKey="activity_type" width={104} tick={{fill:'#a8b4cc',fontSize:10}} tickLine={false} axisLine={false}/><Tooltip formatter={v=>[`${v} kcal`,'Average calories']} contentStyle={{background:'#151b2d',border:'1px solid #303a58',borderRadius:10,color:'#eef3fc'}}/><Bar dataKey="avg_calories" name="Average calories" fill="#45d6b4" radius={[0,5,5,0]}/></BarChart></ResponsiveContainer></div></section>
    </div>
    <p className="simple-data-note"><CircleHelp size={15}/> All records are synthetic and fictional. Goal adherence and recovery scores are educational analytics, not medical advice or real-world health claims.</p>
  </div>
}

export default function App() {
  const [page,setPage]=useState('overview'), [summary,setSummary]=useState(null),[activities,setActivities]=useState([]),[monthly,setMonthly]=useState([]),[weekday,setWeekday]=useState([]),[intensity,setIntensity]=useState([]),[error,setError]=useState('')
  useEffect(()=>{Promise.all([get('/api/summary'),get('/api/activities'),get('/api/trends/monthly'),get('/api/trends/weekday'),get('/api/intensity')]).then(([s,a,m,w,i])=>{setSummary(s);setActivities(a);setMonthly(m);setWeekday(w);setIntensity(i)}).catch(e=>setError(`${e.message}. Start the FastAPI backend on port 8000.`))},[])
  return <div className="app-shell"><Sidebar page={page} setPage={setPage}/><main className="main"><Header page={page}/>{error?<div className="error-state"><AlertTriangle size={28}/><h2>Unable to load FitGraph data</h2><p>{error}</p><code>cd backend && uvicorn app.main:app --reload --port 8000</code></div>:!summary?<div className="loading full">Loading FitGraph analytics…</div>:page==='overview'?<Overview summary={summary} activities={activities} monthly={monthly} intensity={intensity} weekday={weekday}/>:page==='network'?<BehaviorInsightsPage/>:page==='participants'?<ParticipantsPage/>:<PipelinePage/>}<footer>FITGRAPH <span>•</span> Data Engineering & Fitness Trends <span className="footer-right">Source: synthetic_fitness_dataset.csv · synthetic data</span></footer></main></div>
}
