try:
    import json
    from datetime import datetime, timedelta

    from flask import Flask, render_template
    from flask_cors import CORS

    from maxiGauge import MaxiGaugeLogger

    app = Flask(__name__)
    CORS(app)

    mgl = MaxiGaugeLogger()
    mgl.start()


    @app.route('/')
    def index():
        if mgl.is_alive():
            return render_template('index.html', labels=mgl.labels)
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
        app.run(debug=False, host='0.0.0.0', port=80)

except Exception as e:
    print(e)
    input()
