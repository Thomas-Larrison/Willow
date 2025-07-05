# Willow

A simple Kraken crypto trading bot.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` to provide your `KRAKEN_API_KEY`, `KRAKEN_API_SECRET`, and database URL.

3. Initialize the database tables:
   ```bash
   python init_db.py
   ```

4. Run the bot:
   ```bash
   python main.py
   ```
