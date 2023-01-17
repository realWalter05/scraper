from properties import CityProperty
from flask import Flask, send_file, render_template, Response, request, Response
import os
import csv
from werkzeug.security import check_password_hash
from celery import Celery

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    #celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
celery = make_celery(app)
password_hash = "pbkdf2:sha256:260000$E5JkMcO1xPv6jTOs$c8d222f76b1f70af9fa01577e5ebd877d19d5e0623dfcf512d5fb50de40f03b7"

@app.route("/")
def index():
    data_files = []
    for file in os.listdir("./"):
        if "city" in file and "data" in file:
            if len(data_files) > 2:
                print(file)
                os.remove("./"+file)
                break
            print(file)
            data_files.append(file)
    print(data_files)
    return render_template("index.html", files=data_files)



@app.route('/get_data', methods=["POST"])
def get_data():
    if "password" in request.form:
        try:
            user_pwd = request.form["password"]
            if check_password_hash(password_hash, user_pwd):
                for data_file in os.listdir("/home/zikavaclav05/"):
                    if "data" in data_file:
                        return send_file("/home/zikavaclav05/" + data_file, as_attachment=True)
            return render_template("index.html", status="Password is wrong.")
        except Exception:
                return render_template("index.html", status="The data was not found. Try again later or contact the developer.")
    return render_template("index.html", status="Type password.")



@app.route('/download_property_data', methods=["POST"])
def download_property_data():
    if "password" in request.form:
        try:
            user_pwd = request.form["password"]
            if check_password_hash(password_hash, user_pwd):
                file = request.form["file"]
                print(file)
                if file in os.listdir("/home/zikavaclav05/"):
                    if "city" in file and "data" in file:
                        return send_file("/home/zikavaclav05/" + file, as_attachment=True)
            print("wrong")
            return render_template("index.html", status_property="Password is wrong.")
        except Exception:
                return render_template("index.html", status_property="The data was not found. Try again later or contact the developer.")
    return render_template("index.html", status_property="Type password.")


@app.route('/get_property_data', methods=["POST"])
def get_property_data():
    if "password" in request.form:
        try:
            user_pwd = request.form["password"]
            if check_password_hash(password_hash, user_pwd):
                get_property_celery.delay(request.form["property"])
                return render_template("index.html", status="The procces of gathering the data started in the background. You can close the page.")

            return render_template("index.html", status="Password is wrong.")
        except Exception as e:
                return render_template("index.html", status=str(e))
    return render_template("index.html", status="Type password.")


@celery.task(name="celery_get_property_data")
def get_property_celery(property):
    csv_file = CityProperty(property)
    csv_file.write_csv()


if __name__ == "__main__":
    app.run(debug=True)
