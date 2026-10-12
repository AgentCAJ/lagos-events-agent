# Lagos Events Agent

Emails you a digest of tech events and opportunities in Lagos Island and the Mainland
every morning, using Claude with web search, run on GitHub Actions.

## Setup (about 10 minutes)

1. **Create a GitHub repo** (private is fine) and push these files to it.
2. **Get an Anthropic API key** at https://console.anthropic.com and make sure
   web search is enabled in Console privacy settings.
3. **Make a Gmail app password** (Google Account > Security > 2-Step
   Verification > App passwords). Use this, not your normal password.
4. In your repo: **Settings > Secrets and variables > Actions > New repository secret**:
   - `ANTHROPIC_API_KEY`
   - `SMTP_USER` (your Gmail address)
   - `SMTP_PASSWORD` (the app password)
   - `EMAIL_TO` (where to send; comma-separate for several)
5. Optional: under **Variables**, add `EVENT_FOCUS` to tune interests, e.g.
   `AI meetups, fintech events, hackathons`.
6. Go to the **Actions** tab, open "Daily Lagos Events Email", click **Run workflow** to test.

## Timing

Scheduled for 05:00 UTC = 6:00 AM Lagos, because GitHub's scheduler often runs
late. Change the cron line in `.github/workflows/daily-events.yml` if needed.
Scheduled workflows pause after 60 days of no repo activity, so push a small
commit now and then (or re-enable in the Actions tab).

## Local test

    pip install -r requirements.txt
    export ANTHROPIC_API_KEY=... SMTP_USER=... SMTP_PASSWORD=...
    python agent.py
