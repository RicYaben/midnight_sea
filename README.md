# Midnight Sea

Midnight Sea (MS) is a generic crawler for Dark Web marketplaces.
MS features a human-like behavior to bypass anti-crawling mechanisms and a new crawling strategy.

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

The container includes the following services:

<div align="center">

| Service   | Description                                                   |
| --------- | ------------------------------------------------------------- |
| Scraper   | Captures data points from pages                               |
| Storage   | Handles how and where the data is stored                      |
| Crawler   | This is the crawler!                                          |
| Postgres  | A Postgres database instance to store the data                |
| PgAdmin   | A visual tool to manage the database                          |
| Proxy     | A proxy service for Tor and I2P                               |
| pgBackups | A service that backup the postgres database once every 30 min |

</div>

---

## Publications

- Georgoulias, D., Yaben, R., & Vasilomanolakis, E. (Accepted/In press). Cheaper than you thought? A dive into the darkweb market of cyber-crime products. In Proceedings of The 18th International Conference on Availability, Reliability and Security (ARES 2023) ACM. [[link](https://orbit.dtu.dk/en/publications/cheaper-than-you-thought-a-dive-into-the-darkweb-market-of-cyber-)]

## How do I cite Midnight Sea?

For now, cite [this paper](https://orbit.dtu.dk/en/publications/cheaper-than-you-thought-a-dive-into-the-darkweb-market-of-cyber-) or use the following citation:

```latex
@software{midnightsea,
	title        = {Midnight Sea},
	author       = {Ricardo Yaben},
	url          = {https://github.com/RicYaben/midnight\%5Fsea},
	version      = {0.1.0}
}
```
