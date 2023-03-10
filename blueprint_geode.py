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
@geode_routes.route('/get_allowed_files', methods=['GET'])
def get_allowed_files():
    extensions = functions.list_objects_input_extensions()
    return {"status": 200, "extensions": extensions}
@geode_routes.route('/get_object_allowed_files', methods=['POST'])
def get_allowed_files():
    geode_objects = flask.request.form.get('geode_objects') 
    extensions = functions.list_objects_input_extensions(geode_objects)
    return {"status": 200, "extensions": extensions}
@geode_routes.route('/get_allowed_objects', methods=['POST'])
def get_allowed_objects():
    filename = flask.request.form.get('filename')
    if filename is None:
        return flask.make_response({"error_message": "No file sent"}, 400)
    file_extension = os.path.splitext(filename)[1][1:]
    objects = functions.list_objects(file_extension)
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

@geode_routes.route('/convert_file', methods=['POST'])
def convert_file():
    try:
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        object_type = flask.request.form.get('object_type')
        file = flask.request.form.get('file')
        old_file_name = flask.request.form.get('old_file_name')
        file_size = flask.request.form.get('file_size')

        if object_type is None:
            return flask.make_response({"error_message": "No object_type sent"}, 400)
        if file is None:
            return flask.make_response({"error_message": "No file sent"}, 400)
        if old_file_name is None:
            return flask.make_response({"error_message": "No old_file_name sent"}, 400)
        if file_size is None:
            return flask.make_response({"error_message": "No file_size sent"}, 400)

        secure_file_name = werkzeug.utils.secure_filename(old_file_name)
        file_path = os.path.join(UPLOAD_FOLDER, secure_file_name)
        id = str(uuid.uuid4()).replace('-', '')

        uploaded_file = functions.upload_file(file, secure_file_name, UPLOAD_FOLDER, file_size)
        if not uploaded_file:
            flask.make_response({"error_message": "File not uploaded"}, 500)

        data = geode_objects.objects_list()[object_type]['load'](file_path)

        name = data.name()
        native_extension = data.native_extension()

        viewable_file_path = os.path.join(UPLOAD_FOLDER, id)
        native_file_path = os.path.join(UPLOAD_FOLDER, id + '.' + native_extension)

        saved_viewable_file_path = functions.geode_objects.objects_list()[object_type]['save_viewable'](data, viewable_file_path)
        functions.geode_objects.objects_list()[object_type]['save'](data, native_file_path)


        native_file_name = os.path.basename(native_file_path)
        viewable_file_name = os.path.basename(saved_viewable_file_path)

        return flask.make_response({
                                    "name": name,
                                    "native_file_name": native_file_name,
                                    "viewable_file_name": viewable_file_name,
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

@geode_routes.route('/get_texture_coordinates', methods=['POST'])
def get_texture_coordinates():
    try:
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        native_file_name = flask.request.form.get('native_file_name')
        geode_object = flask.request.form.get('geode_object')

        if geode_object is None:
            return flask.make_response({"error_message": "No geode_object sent"}, 400)
        if native_file_name is None:
            return flask.make_response({"error_message": "No native_file_name sent"}, 400)

        native_file_path = os.path.join(UPLOAD_FOLDER, native_file_name)
        data = geode_objects.objects_list()[geode_object]['load'](native_file_path)
        texture_coordinates = data.texture_manager().texture_names()

        return flask.make_response({ "texture_coordinates": texture_coordinates }, 200)
    except Exception as e:
        print("error : ", str(e), flush=True)
        return flask.make_response({"error_message": str(e)}, 500)


@geode_routes.route('/convert_viewable_raster_image', methods=['POST'])
def convert_viewable_raster_image():
    try:
        UPLOAD_FOLDER = flask.current_app.config['UPLOAD_FOLDER']
        native_file_name = flask.request.form.get('native_file_name')
        geode_object = flask.request.form.get('geode_object')

        if geode_object is None:
            return flask.make_response({"error_message": "No geode_object sent"}, 400)
        if native_file_name is None:
            return flask.make_response({"error_message": "No native_file_name sent"}, 400)

        native_file_path = os.path.join(UPLOAD_FOLDER, native_file_name)
        data = geode_objects.objects_list()[geode_object]['load'](native_file_path)
        texture_coordinates = data.texture_manager().texture_names()

        return flask.make_response({ "texture_coordinates": texture_coordinates }, 200)
    except Exception as e:
        print("error : ", str(e), flush=True)
        return flask.make_response({"error_message": str(e)}, 500)


        save_viewable_raster_image2D