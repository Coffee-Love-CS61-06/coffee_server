from flask import Blueprint
from modules.dataBase import collection as db
from bson.json_util import dumps

mod = Blueprint('api', __name__, template_folder='templates')



@mod.route('/')
def api():
    return dumps(db.getAllImages())
