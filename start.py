try:
    import webbrowser
    import json
    from datetime import datetime, timedelta
    import os
    from flask import Flask, render_template
    from flask_cors import CORS

    from maxiGauge import MaxiGaugeLogger
    from dotenv import load_dotenv

    load_dotenv()
    serial_port = os.getenv('COM_PORT', None)
    server_port = int(os.getenv('SERVER_PORT', 80))
    CHART_LINE_WIDTH = os.getenv('CHART_LINE_WIDTH', 1)

    app = Flask(__name__)
    CORS(app)

    mgl = MaxiGaugeLogger(serial_port=serial_port)
    mgl.start()


    @app.route('/')
    def index():
        if mgl.is_alive():
            return render_template('index.html', labels=mgl.labels, chart_line_width=CHART_LINE_WIDTH)
        else:
            return "Logger died!"


    @app.route('/last')
    def last_data_point():
        if mgl.is_alive():
            return json.dumps(mgl.values, default=str)
        else:
            return "Logger died!"


    @app.route('/history')
    @app.route('/history/<int:minutes>')
    def history_data_point(minutes=60):
        if mgl.is_alive():
            values = mgl.history
            i = 0
            for i, v in enumerate(values):
                if v[0] > datetime.now() - timedelta(minutes=minutes): break
            values = values[i:]
            return json.dumps({
                'labels': mgl.labels,
                'values': values
            }, default=str)
        else:
            return "Logger died!"


    if __name__ == '__main__':
        try:
            webbrowser.open(f'http://localhost:{server_port}', new=1)
        except Exception as e:
            print(e)

        app.run(debug=False, host='0.0.0.0', port=server_port)

except Exception as e:
    print("Error:", e)
    input()
