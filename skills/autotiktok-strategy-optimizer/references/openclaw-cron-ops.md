# AutoTikTok OpenClaw Cron Ops

This reference describes the preferred recurring runtime path for AutoTikTok optimizer jobs on a real OpenClaw Gateway.

## Source Of Truth

For recurring optimizer runs, the preferred source of truth is:

- `openclaw cron list`
- `openclaw cron runs --id <job-id>`
- Gateway cron history

Do not treat these compatibility artifacts as recurring runtime source of truth:

- `optimizer-job-schedule.sample.json`
- `optimizer-job-schedule.external.sample.json`
- `optimizer-job-execution-context.sample.json`
- `optimizer-job-orchestration-cycle.sample.json`

They remain useful for:

- fixture generation
- deterministic rehearsal
- cutover validation

## Stable Jobs

The committed contract freezes two stable OpenClaw cron job names:

- `autotiktok:daily-optimizer`
- `autotiktok:weekly-optimizer`

Freeze or inspect that contract with:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/build_optimizer_openclaw_cron_contract.py
```

## Preferred Runtime Entrypoints

Use these thin entrypoints for recurring runs:

```bash
python3 skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_daily_optimizer.py
python3 skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_weekly_optimizer.py
```

They default to the committed canonical runtime inputs:

- daily: `optimizer-input-manifest.sample.json`
- weekly: `optimizer-input-manifest.sample.json` + `optimizer-weekly-review-window.sample.json`

Both entrypoints:

- emit `optimizer-job-run.v1`
- support `--output` and `--output-root`
- print concise plain-text summaries for isolated cron runs

## Setup Flow

Follow this order:

1. Run `openclaw cron list`
2. Match on exact `name`
3. If the job exists, update it with `openclaw cron edit <id> ...`
4. If the job does not exist, create it with `openclaw cron add ...`

Recommended defaults:

- `--session isolated`
- `--tools exec,read,write`
- `--light-context`
- `--no-deliver`

## Recommended Commands

Daily:

```bash
openclaw cron add \
  --name "autotiktok:daily-optimizer" \
  --cron "0 4 * * *" \
  --tz "UTC" \
  --session isolated \
  --message "Run python3 skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_daily_optimizer.py and summarize the result, key decision, and output artifact path." \
  --tools exec,read,write \
  --light-context \
  --no-deliver
```

Weekly:

```bash
openclaw cron add \
  --name "autotiktok:weekly-optimizer" \
  --cron "15 4 * * 0" \
  --tz "UTC" \
  --session isolated \
  --message "Run python3 skills/autotiktok-strategy-optimizer/scripts/run_openclaw_cron_weekly_optimizer.py and summarize the weekly decision and output artifact path." \
  --tools exec,read,write \
  --light-context \
  --no-deliver
```

Inspect recent runs:

```bash
openclaw cron runs --id <job-id>
```

## Focused Gates

Use these two gates together when working on recurring runtime behavior:

```bash
python3 skills/autotiktok/scripts/validate_optimizer_openclaw_cron_runtime_alignment.py
python3 skills/autotiktok/scripts/validate_optimizer_scheduler_compatibility_role_alignment.py
```

The first gate proves the preferred OpenClaw cron runtime still regenerates deterministically.

The second gate proves the legacy scheduler-facing artifacts still self-identify as compatibility-only rehearsal contracts.
