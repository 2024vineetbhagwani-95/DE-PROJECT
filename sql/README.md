The warehouse loader creates:
- `dim_participant`: participant profile dimension
- `dim_workout_type`: activity type dimension
- `dim_date`: calendar dimension
- `fact_workout_activity`: one participant's daily activity record
- `daily_activity_aggregate`: daily summaries by workout type
- `participant_graph_metrics`: graph centrality and community metrics

The loader is idempotent for the activity fact using `(participant_id, activity_date)` as its key. This matches the source's one-record-per-participant-per-date grain.
