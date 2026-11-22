# How to upload your weather project to GitHub (very easy)

## Method 1 — GitHub Desktop (recommended for beginners)

1. Install **GitHub Desktop** from https://desktop.github.com/ and sign in.
2. Download the ZIP shared with you. Right-click it and choose **Extract All**.
3. Open GitHub Desktop. Choose **File → Add Local Repository → Choose** the extracted folder. If GitHub Desktop says this is not a Git repository, choose **Create a repository here**.
4. Enter repository name `weather-forecast-alert-application`, optionally enter a description, then click **Create Repository**.
5. On the left you will see the changes. Verify `.env`, `.venv`, `db/weather.sqlite`, and other private files are not listed.
6. In **Summary (required)** type `Initial working weather alert app`. Click **Commit to main**.
7. At the top click **Publish repository**. Choose **Public** (if you want it on your portfolio), then **Publish repository**.
8. Your GitHub project will now have a link you can share.
9. After making improvements later, type a new commit message and click **Commit to main** then **Push origin**.

If your downloaded folder contains demo outputs, commit them: they are deliberately labelled **SIMULATED**. Take your own screenshots after running Streamlit and place them in `images/`.

## Method 2 — Git and terminal (for students practising Git)

Inside the extracted project folder:

```bash
git init
git branch -M main
git add .
git commit -m "Initial weather app: demo, API, dashboard and alerts"
```

Create an **empty public repository** named `weather-forecast-alert-application` at https://github.com/new (do NOT initialize it with another README if using the commands above). Then run the two commands GitHub shows with **your own username and repository URL**, in this format:

```bash
git remote add origin https://github.com/YOUR_USERNAME/weather-forecast-alert-application.git
git push -u origin main
```

Future updates:

```bash
git add .
git commit -m "Improve alerts and update screenshots"
git push
```

For Git authentication, GitHub Desktop or a credential manager is easiest. Do not put passwords or API tokens in URLs or screenshots.

## What to upload vs. what to keep private

| Upload | Do not upload |
|---|---|
| Python source code | `.env` with secrets |
| `README.md`, `.env.example` | `TELEGRAM_BOT_TOKEN`, chat ID |
| `requirements.txt` and tests | `.venv/` packages |
| Sample simulated CSV/chart/report | `db/weather.sqlite` (local history) |
| Own dashboard screenshots | Personal location information / credentials |

## Suggested GitHub tags

`python`, `weather-api`, `streamlit`, `fastapi`, `automation`, `sqlite`, `matplotlib`, `open-meteo`
