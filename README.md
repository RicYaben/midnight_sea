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
docker compose -p ms -f bin/docker/docker-compose.yaml up -d --build
```

Once everything is started, open a terminal to the crawler service (e.g., `docker attach crawler`) and type the name of the marketplace.
When the crawler starts, it will ask for a cookie token from an open session with the market. If you don't have one, do a manual login into the market and copy/paste the session cookie.
You can find the cookie by sending a new authenticated request to the market home page, and checking either your browser cookie jar, or the cookies sent during the request (from the `Network` tab).

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

## Develop

Requirements:

	- Linux environment (e.g., Dev container, WSL, etc)
	- Pipx
	- Python from 3.7 to 3.10 (the project relies on Poetry to install dependencies and 3.11 is not supported just yet).


Run `make init` to install all the packages included in the project for each service and their dependencies.
You can test each individual project/workspace using `make .venv-<project>` where `<project>` can be either crawler, storage or scraper.

Alternatively, you can install the application altogether and run it as a normal Python app with `python -m pip install -e workspaces/<project>` and running it through `python -m <project>`.

These projects use [Hydra](https://hydra.cc/docs/intro/) as a configuration loader. The configuration files are stored in the root folder `config` and in each project under the same name (e.g. `workspaces/crawler/src/crawlerconfig`). The usage is better described in Hydra's main page.

In addition, the crawler and scraper services use custom configuration files to recognise the structure of the markets and the content to scrape.
These files are located in the `dist` folder of each project (e.g., `workspaces/crawler/dist`).
I came up with a poor naming convention to distinguish these files:

	- Plans: Provide the structure of the markets, validation rules and market metadata (url, name, etc.)
	- Market State: Contain the state of the crawler for a given market. Helpful to resume crawling sessions.
	- Blueprints: Sort of helpers for the scraper to guide through the raw files and capture relevant data points.

## Future Plans

I am currently rewriting the crawler in Go.
There are multiple features that get very challenging to implement in a language like Python.
Here is a list of some of the features I am planning to add to the crawler (in no particular order):

- Automated login, account managers and account generators
- CAPTCHA solvers
- Automated/assisted layout recognition (together with the GUI)
- Multi-sessions and crawl-sharding (multiple sessions crawling the same market)
- A GUI (easier to click than to type)
- Crawlers for Forums and chat applications.
- And much more!

Keep an eye on the project :)

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
