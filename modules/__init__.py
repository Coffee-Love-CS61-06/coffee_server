from flask import Flask
from modules import backed, api
from tensorflow.keras.models import load_model

app = Flask(__name__)
UPLOAD_FOLDER = '/static/assets/uploads/covers/'



app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
load_model("modules/model/mobilenet_model.hdf5")
print("model loading .... plaese wait this might take a while")

app.secret_key ='1234'
from modules.backed.routes import mod
from modules.api.routes import mod

# # register blueprints for api and site

app.register_blueprint(backed.routes.mod)
app.register_blueprint(api.routes.mod, url_prefix='/api')