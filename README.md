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
Copyright (C) 2012 Philipp Klaus (Institut fuer Kernphysik Frankfurt) (see maxiGauge.py)

The following license only applies to files written by Philipp Klaus.
A couple of other files have different licenses, such as the javascript
libraries d3, Rickshaw, jQuery and cubism!

MIT:

> Permission is hereby granted, free of charge, to any person
> obtaining a copy of this software and associated documentation files
> (the "Software"), to deal in the Software without restriction, including
> without limitation the rights to use, copy, modify, merge, publish,
> distribute, sublicense, and/or sell copies of the Software, and to
> permit persons to whom the Software is furnished to do so, subject to
> the following conditions:
> 
> The above copyright notice and this permission notice shall be
> included in all copies or substantial portions of the Software.
> 
> THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
> EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
> MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
> IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
> CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
> TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
> SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
