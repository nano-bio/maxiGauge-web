# MaxiGauge Logger and Viewer

### Setup 3rd party software

```
pip install -r requirements.txt
```


### Settings

Copy file `.env.example` to `.env` and change the variables in `.env` to your needs.

- `LOGGING_FOLDER`: Where the daily log files are saved
- `SERVER_PORT`: Leave at `80` (default) or change to a port which is not in use.
- `COM_PORT`: If you know the COM port, set it (e.g. `COM_PORT=COM3`)
- `CHART_LINE_WIDTH`: If you want to have thicker lines within the viewer


### Run
- Windows: doubleclick on `start.py`
- Linux: In Terminal `python3 start.py`

### Access
- http://localhost:SERVER_PORT (e.g. http://localhost:8000 )
- http://your-ip-adress-or-hostname:SERVER_PORT (e.g. http://138.232.74.165:8000 )

### Troubles?
- The software tries to find the right COM port. If it does not work, provide a `COM_PORT` in the
`.env` file.
- You can not use this program in parallel to other maxiGauge software.


### Thanks
- Philipp Klaus (see maxiGauge.py)
- Josi (so many reasons...)


### License
GNU
