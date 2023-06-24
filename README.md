> ATTENTION: Version 1.0 is underway and planned for mid August 2023 (includes major changes).

# Midnight Sea

Midnight Sea (MS) is a crawler for "Dark Web" marketplaces.
The tool can crawl any current marketplace, featuring a human-like behavior to bypass anti-crawling mechanisms and an efficient crawling strategy.

## Usage

The simplest method is to use Docker to load all the necessary services and components.
For this, simply type the following command in your terminal:

```bash
# Using Make to start the container
make up
# OR
Docker-compose -p midnight_sea -f deployments/docker-compose.yaml up -d --build
```

Once everything is started, open a terminal to the crawler service and type the name of the marketplace.
When the crawler starts, it will ask for a cookie token from an open session with the market. If you don't have one, do a manual login into the market and copy/paste the session cookie.

Currently, MS does not solve CAPTCHA nor automatically login into marketplaces. Therefore, it will require your help once in a while to overcome login pages and CAPTCHA. The crawler will eventually ask that you provide a session cookie (every ~45 min).

MS will tell you if other issues arise, such as "kill path" (i.e., your Tor circuit has been blocked). To solve this, it is enough to restart the Proxy service.

---

The container includes the following services:

| Service   | Description                                                   |
| --------- | ------------------------------------------------------------- |
| Scraper   | Captures data points from pages                               |
| Storage   | Handles how and where the data is stored                      |
| Crawler   | This is the crawler!                                          |
| Postgres  | A Postgres database instance to store the data                |
| PgAdmin   | A visual tool to manage the database                          |
| Proxy     | A proxy service for Tor and I2P                               |
| pgBackups | A service that backup the postgres database once every 30 min |