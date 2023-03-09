import flask
import flask_cors
import os
import functions
import werkzeug
import geode_objects
import uuid
import shutil

geode_routes = flask.Blueprint('geode_routes', __name__)
flask_cors.CORS(geode_routes)

@geode_routes.before_request
def before_request():
    functions.create_lock_file()

@geode_routes.teardown_request
def teardown_request(exception):
    functions.remove_lock_file()

@geode_routes.route('/', methods=['GET'])
def root():
    return flask.make_response({"message": "root"}, 200)
@geode_routes.route('/sharetwin/createbackend', methods=['POST', 'OPTIONS'])
def createbackend():
    return flask.make_response({"ID": str("123456")}, 200)
@geode_routes.route('/healthcheck', methods=['GET'])
def healthcheck():
    return flask.make_response({"message": "healthy"}, 200)
@geode_routes.route('/allowedfiles', methods=['GET'])
def allowedfiles():
    extensions = functions.ListAllInputExtensions()
    return {"status": 200, "extensions": extensions}
@geode_routes.route('/allowedobjects', methods=['POST'])
def allowedobjects():
    filename = flask.request.form.get('filename')
    if filename is None:
        return flask.make_response({"error_message": "No file sent"}, 400)
    file_extension = os.path.splitext(filename)[1][1:]
    objects = functions.ListObjects(file_extension)
    return flask.make_response({"objects": objects}, 200)
@geode_routes.route('/ping', methods=['GET', 'POST'])
def ping():
    LOCK_FOLDER = flask.current_app.config['LOCK_FOLDER']
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if not os.path.isfile(LOCK_FOLDER + '/ping.txt'):
        f = open(LOCK_FOLDER + '/ping.txt', 'a')
        f.close()
    return flask.make_response({"message": "Flask server is running"}, 200)

@geode_routes.route('/uploadfile', methods=['POST'])
def uploadfile():
    try:
        DATA_FOLDER = flask.current_app.config['DATA_FOLDER']
        file = flask.request.form.get('file')
        old_file_name = flask.request.form.get('old_file_name')
        file_size = flask.request.form.get('file_size')
        
        if file is None:
            return flask.make_response({"error_message": "No file sent"}, 400)
        if old_file_name is None:
            return flask.make_response({"error_message": "No old_file_name sent"}, 400)
        if file_size is None:
            return flask.make_response({"error_message": "No file_size sent"}, 400)
        
        new_file_name = werkzeug.utils.secure_old_file_name(old_file_name)
        uploaded_file = functions.UploadFile(file, new_file_name, DATA_FOLDER, file_size)
        if not uploaded_file:
            flask.make_response({"error_message": "File not uploaded"}, 500)
            
        return flask.make_response({"new_file_name": new_file_name }, 200)
    except Exception as e:
        print("error : ", str(e))
        return flask.make_response({"error_message": str(e)}, 500)

@geode_routes.route('/convertfile', methods=['POST'])
def convertfile():
    try:
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        object_type = flask.request.form.get('object_type')
        file = flask.request.form.get('file')
        old_file_name = flask.request.form.get('old_file_name')
        file_size = flask.request.form.get('file_size')

        if object is None:
            return flask.make_response({"error_message": "No object sent"}, 400)
        if file is None:
            return flask.make_response({"error_message": "No file sent"}, 400)
        if old_file_name is None:
            return flask.make_response({"error_message": "No old_file_name sent"}, 400)
        if file_size is None:
            return flask.make_response({"error_message": "No file_size sent"}, 400)

        secure_file_name = werkzeug.utils.secure_filename(old_file_name)
        file_path = os.path.join(UPLOAD_FOLDER, secure_file_name)
        id = str(uuid.uuid4()).replace('-', '')

        uploaded_file = functions.upload_file(file, old_file_name, UPLOAD_FOLDER, file_size)
        if not uploaded_file:
            flask.make_response({"error_message": "File not uploaded"}, 500)

        new_file_path = os.path.join(UPLOAD_FOLDER, id)
        model = geode_objects.objects_list()[object_type]['load'](file_path)
        new_file_path = functions.geode_objects.objects_list()[object_type]['save_viewable'](model, new_file_path)
        new_file_name = new_file_path.split('/')[-1]

        return flask.make_response({
                                    "new_file_name": new_file_name,
                                    "old_file_name": old_file_name,
                                    "id" : id
                                    }, 200)
    except Exception as e:
        print("error : ", str(e), flush=True)
        return flask.make_response({"error_message": str(e)}, 500)

@geode_routes.route('/delete_all_files', methods=['DELETE'])
def delete_all_files():
    try:
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        for filename in os.listdir(UPLOAD_FOLDER):
            f = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(f):
                print(f)
                os.remove(f)
            else:
                shutil.rmtree(f)

        return flask.make_response({ "message": "deleted" }, 204)
    except Exception as e:
        print("error : ", str(e), flush=True)
        return flask.make_response({"error_message": str(e)}, 500)