from keras.models import load_model
from modules import app

#encryption relies on secret keys so they could be run
model = load_model("modules/model/mobilenet_model.hdf5")
print("model loading .... plaese wait this might take a while")

if __name__ == "__main__":
    app.run(debug=True)
