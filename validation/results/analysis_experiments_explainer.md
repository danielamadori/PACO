# Experiment Analysis from Notebook Dataset

This analysis uses `benchmarks.sqlite` and focuses on the same timing dimensions used in `Validation_Expalining_Strategies_for_Expected_Impacts.ipynb`, extended with explainer statuses and leaves.

## Global Summary

- total_rows: 17095
- completed_rows: 17090
- completed_error_rows: 10
- completed_error_rate_pct: 0.06
- migrated_rows: 12604
- migrated_error_rows: 10
- migrated_error_rate_pct: 0.08
- migrated_explain_attempt_rows: 8272
- migrated_explain_attempt_rate_pct: 65.63
- impacts_success_when_attempted_pct: 100.0

## Data Coverage Note for Leaves

- `explainer_leaves_total` exists only in experiments executed after this metric was introduced.
- Leaf-ready rows: 227 / 12604 migrated rows (1.80%).
- Leaf-ready attempted rows: 175 / 8272 attempted rows (2.12%).
- Current leaf-ready subset is concentrated on `(x=1, y=3)`.

## Time Split (Create vs Explain) on Migrated Rows

- create_pct: 57.57
- explain_pct: 42.43
- create_ms_sum: 102577.009
- explain_ms_sum: 75599.13

## Status Counts (Migrated Rows)

### explain_strategy_impacts_based_status
- success: 8272
- not_attempted: 4332

### explain_strategy_decision_based_status
- not_attempted: 12604

### explain_strategy_hybrid_status
- not_attempted: 12604

## Explainer Leaves Distribution (attempted rows)

- min: 1
- p25: 1.0
- median: 2.0
- p75: 3.0
- p90: 3.0
- max: 3
- mean: 1.931

## Aggregation by (x,y)

 x  y    n  error_rate  explain_attempt_rate  impacts_success_rate  avg_leaves  median_total_ms
 1  1  913    0.000000              0.486309              0.486309         NaN           2.1460
 1  2 5398    0.000371              0.670433              0.670433         NaN          10.2675
 1  3  893    0.008959              0.733483              0.733483    1.488987          66.6560
 2  1 5400    0.000000              0.658148              0.658148         NaN           5.4705

## Aggregation by num_impacts

 num_impacts    n  explain_attempt_rate  impacts_success_rate  avg_leaves  median_explain_ms
           1 1241              0.470588              0.470588         NaN             0.0040
           2 1241              0.663175              0.663175         NaN             1.6570
           3 1241              0.673650              0.673650    1.857143             1.8150
           4 1291              0.680093              0.680093    1.500000             1.5600
           5 1296              0.678241              0.678241    1.518519             1.8400
           6 1296              0.658179              0.658179    1.425926             1.4530
           7 1272              0.675314              0.675314    1.100000             1.5685
           8 1242              0.685185              0.685185         NaN             1.5405
           9 1242              0.681965              0.681965         NaN             1.4700
          10 1242              0.694042              0.694042         NaN             1.6630

## Correlation (attempted migrated rows)

                        explainer_leaves_total  time_explain_strategy  strategy_tree_time  build_strategy_time  phase_explain_ms
explainer_leaves_total                   1.000                  0.681              -0.267                0.382             0.343
time_explain_strategy                    0.681                  1.000              -0.106                0.295             0.281
strategy_tree_time                      -0.267                 -0.106               1.000               -0.120             0.037
build_strategy_time                      0.382                  0.295              -0.120                1.000             0.988
phase_explain_ms                         0.343                  0.281               0.037                0.988             1.000
