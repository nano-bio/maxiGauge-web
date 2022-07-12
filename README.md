# MaxiGauge Logger and Viewer

### Setup 3rd party software

```
pip install -r requirements.txt
```


### Set parameters to your environment

Copy file `.env.example` to `.env` and change the variables in `.env` to your needs.

- `LOGGING_FOLDER`: Where the daily log files are saved
- `SERVER_PORT`: Leave at `80` (default) or change to a port which is not in use.
- `COM_PORT`: If you know the COM port, set it (`COM_PORT=COM3`)


### Run

Run start.py (just doubleclick). Open a browser and navigate to http://localhost
or http://localhost:8000 (if you do not use port 80 but port 8000)
or http://your-ip-adress-or-hostname (if you want to connect from the office)


### Troubles?
- The software tries to find the right COM port. If it does not work, provide a `COM_PORT` in the
`.env` file.
- You can not use this program in parallel to other maxiGauge software.


### Thanks
- Philipp Klaus (see maxiGauge.py)
- Josi (so many reasons...)


### License
GNU
