"""Lagos Events Agent: searches the web for events/opportunities in Lagos
(Island + Mainland) and emails a digest every morning."""
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from zoneinfo import ZoneInfo

import anthropic

MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5-5")
FOCUS = os.environ.get(
    "EVENT_FOCUS",
    "tech events: developer meetups, startup and founder events, hackathons, "
    "AI/data/fintech/crypto gatherings, tech conferences, workshops and bootcamps, "
    "demo days, pitch competitions, accelerator and grant applications, "
    "tech job fairs, and tech community mixers",
)
AREAS = "Lagos Island (Victoria Island, Ikoyi, Lekki, Lagos Island) and the Lagos Mainland (Yaba, Ikeja, Surulere, Maryland, Ikorodu)"

now = datetime.now(ZoneInfo("Africa/Lagos"))
TODAY = now.strftime("%A, %d %B %Y")

PROMPT = f"""Today is {TODAY} (Lagos time).

Search the web for upcoming events and opportunities in {AREAS}.
Focus on: {FOCUS}.

Look at sources such as Eventbrite, Meetup, Luma, Tix Africa, Nairaland events,
Instagram/X event pages, Techcabal, Techpoint, GDG Lagos, Google Developer Groups, Devcongress, Founders Connect, and venue/organizer sites.

Rules:
- Only include events happening from today through the next 14 days.
- Only include events you actually found in search results. Never invent events.
- For each event give: name, date and time, venue and area (Island or Mainland),
  price (or Free), why it might be worth attending, and the source link.
- Group by "Today / This Week" and "Coming Up". Flag free events.
- Put anything with a deadline (applications, registrations) in a short
  "Deadlines" section at the top.
- If you find little, say so honestly instead of padding.

Return ONLY a clean HTML fragment (no <html> or <body> tags), using <h2>, <h3>,
<ul>, <li>, and <a href> links."""


def build_digest() -> str:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
    messages = [{"role": "user", "content": PROMPT}]
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 12}]

    for _ in range(5):  # continue if the server-side search loop pauses
        resp = client.messages.create(
            model=MODEL, max_tokens=4000, tools=tools, messages=messages
        )
        if resp.stop_reason != "pause_turn":
            break
        messages.append({"role": "assistant", "content": resp.content})

    html = "".join(b.text for b in resp.content if b.type == "text").strip()
    return html.replace("```html", "").replace("```", "").strip()


def send_email(html_body: str) -> None:
    user = os.environ["SMTP_USER"]
    password = os.environ["SMTP_PASSWORD"]
    to = os.environ.get("EMAIL_TO", user)
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "465"))

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Lagos events for {now.strftime('%a %d %b')}"
    msg["From"] = user
    msg["To"] = to
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP_SSL(host, port) as server:
        server.login(user, password)
        server.sendmail(user, [t.strip() for t in to.split(",")], msg.as_string())


if __name__ == "__main__":
    digest = build_digest()
    if not digest:
        raise SystemExit("Empty digest, not sending.")
    send_email(digest)
    print("Digest sent.")
