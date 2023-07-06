import flask
import flask_cors
import os
import functions
import werkzeug
import geode_objects
import uuid
import shutil

import opengeode_geosciences as og_gs

geode_routes = flask.Blueprint("geode_routes", __name__)
flask_cors.CORS(geode_routes)


@geode_routes.before_request
def before_request():
    functions.create_lock_file()


@geode_routes.teardown_request
def teardown_request(exception):
    functions.remove_lock_file()


@geode_routes.route("/", methods=["GET"])
def root():
    return flask.make_response({"message": "root"}, 200)


@geode_routes.route("/sharetwin/createbackend", methods=["POST", "OPTIONS"])
def createbackend():
    return flask.make_response({"ID": str("123456")}, 200)


@geode_routes.route("/healthcheck", methods=["GET"])
def healthcheck():
    return flask.make_response({"message": "healthy"}, 200)


@geode_routes.route("/allowed_files", methods=["GET"])
def allowed_files():
    extensions = functions.list_objects_input_extensions(True)
    return {"status": 200, "extensions": extensions}


@geode_routes.route("/object_allowed_files", methods=["POST"])
def object_allowed_files():
    geode_object = flask.request.form.get("geode_object")
    if geode_object is None:
        return flask.make_response({"error_message": "No geode_object sent"}, 400)
    extensions = functions.list_objects_input_extensions(False, geode_object)
    return {"status": 200, "extensions": extensions}


@geode_routes.route("/allowed_objects", methods=["POST"])
def allowed_objects():
    filename = flask.request.form.get("filename")
    print(f"{filename=}", flush=True)
    if filename is None:
        return flask.make_response({"error_message": "No file sent"}, 400)
    file_extension = os.path.splitext(filename)[1][1:]
    allowed_objects = functions.list_objects(file_extension)
    print(f"{allowed_objects=}", flush=True)
    return flask.make_response({"allowed_objects": allowed_objects}, 200)


@geode_routes.route("/ping", methods=["GET", "POST"])
def ping():
    LOCK_FOLDER = flask.current_app.config["LOCK_FOLDER"]
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    if not os.path.isfile(LOCK_FOLDER + "/ping.txt"):
        f = open(LOCK_FOLDER + "/ping.txt", "a")
        f.close()
    return flask.make_response({"message": "Flask server is running"}, 200)


@geode_routes.route("/convert_file", methods=["POST"])
def convert_file():
    try:
        UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
        object_type = flask.request.form.get("object_type")
        file = flask.request.form.get("file")
        old_file_name = flask.request.form.get("old_file_name")
        file_size = flask.request.form.get("file_size")

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
        id = str(uuid.uuid4()).replace("-", "")

        uploaded_file = functions.upload_file(
            file, secure_file_name, UPLOAD_FOLDER, file_size
        )
        if not uploaded_file:
            flask.make_response({"error_message": "File not uploaded"}, 500)

        data = geode_objects.objects_list()[object_type]["load"](file_path)

        if geode_objects.objects_list()[object_type]["is_viewable"]:
            name = data.name()
        else:
            name = old_file_name

        native_extension = data.native_extension()

        viewable_file_path = os.path.join(UPLOAD_FOLDER, id)
        native_file_path = os.path.join(UPLOAD_FOLDER, id + "." + native_extension)

        saved_viewable_file_path = functions.geode_objects.objects_list()[object_type][
            "save_viewable"
        ](data, viewable_file_path)
        print("Saved viewable", flush=True)
        functions.geode_objects.objects_list()[object_type]["save"](
            data, native_file_path
        )
        print("Saved native", flush=True)

        native_file_name = os.path.basename(native_file_path)
        viewable_file_name = os.path.basename(saved_viewable_file_path)

        return flask.make_response(
            {
                "name": name,
                "native_file_name": native_file_name,
                "viewable_file_name": viewable_file_name,
                "id": id,
            },
            200,
        )
    except Exception as e:
        print("error : ", str(e), flush=True)
        return flask.make_response({"error_message": str(e)}, 500)


@geode_routes.route("/delete_all_files", methods=["DELETE"])
def delete_all_files():
    try:
        UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
        for filename in os.listdir(UPLOAD_FOLDER):
            f = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(f):
                print(f)
                os.remove(f)
            else:
                shutil.rmtree(f)

        return flask.make_response({"message": "deleted"}, 204)
    except Exception as e:
        print("error : ", str(e), flush=True)
        return flask.make_response({"error_message": str(e)}, 500)


@geode_routes.route("/texture_coordinates", methods=["POST"])
def texture_coordinates():
    try:
        UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
        native_file_name = flask.request.form.get("native_file_name")
        geode_object = flask.request.form.get("geode_object")

        if geode_object is None:
            return flask.make_response({"error_message": "No geode_object sent"}, 400)
        if native_file_name is None:
            return flask.make_response(
                {"error_message": "No native_file_name sent"}, 400
            )

        native_file_path = os.path.join(UPLOAD_FOLDER, native_file_name)
        data = geode_objects.objects_list()[geode_object]["load"](native_file_path)
        texture_coordinates = data.texture_manager().texture_names()

        return flask.make_response({"texture_coordinates": texture_coordinates}, 200)
    except Exception as e:
        print("error : ", str(e), flush=True)
        return flask.make_response({"error_message": str(e)}, 500)


@geode_routes.route("/coordinate_systems", methods=["POST"])
def coordinate_systems():
    try:
        UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
        native_file_name = flask.request.form.get("native_file_name")
        geode_object = flask.request.form.get("geode_object")

        if geode_object is None:
            return flask.make_response({"error_message": "No geode_object sent"}, 400)
        if native_file_name is None:
            return flask.make_response(
                {"error_message": "No native_file_name sent"}, 400
            )

        native_file_path = os.path.join(UPLOAD_FOLDER, native_file_name)
        data = geode_objects.objects_list()[geode_object]["load"](native_file_path)
        list_coordinate_systems = (
            data.main_coordinate_reference_system_manager().coordinate_reference_system_names()
        )

        coordinate_systems = []
        geo_crs_type = og_gs.GeographicCoordinateSystem3D.type_name_static()

        for coordinate_system in list_coordinate_systems:
            type_name = (
                data.main_coordinate_reference_system_manager()
                .find_coordinate_reference_system(coordinate_system)
                .type_name()
            )

            data.main_coordinate_reference_system_manager().active_coordinate_reference_system_name
            is_geo = type_name.matches(geo_crs_type)
            is_active = (
                data.main_coordinate_reference_system_manager().active_coordinate_reference_system_name()
                == coordinate_system
            )
            coordinate_systems.append(
                {"name": coordinate_system, "is_geo": is_geo, "is_active": is_active}
            )

        return flask.make_response({"coordinate_systems": coordinate_systems}, 200)
    except Exception as e:
        print("error : ", str(e), flush=True)
        return flask.make_response({"error_message": str(e)}, 500)


@geode_routes.route("/asign_geographic_coordinate_system", methods=["POST"])
def asign_geographic_coordinate_system():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
    geode_object = flask.request.form.get("geode_object")
    id = flask.request.form.get("id")
    filename = flask.request.form.get("filename")
    crs_authority = flask.request.form.get("crs_authority")
    crs_code = flask.request.form.get("crs_code")
    crs_name = flask.request.form.get("crs_name")

    if geode_object is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No geode_object sent"}, 400
        )
    if id is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No id sent"}, 400
        )
    if filename is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No filename sent"}, 400
        )
    if crs_authority is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No crs_authority sent"}, 400
        )
    if crs_code is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No crs_code sent"}, 400
        )
    if crs_name is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No crs_name sent"}, 400
        )

    input_crs = {
        "authority": crs_authority,
        "code": crs_code,
        "name": crs_name,
    }

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    data = geode_objects.objects_list()[geode_object]["load"](file_path)

    functions.asign_geographic_coordinate_system_info(geode_object, data, input_crs)

    geode_objects.objects_list()[geode_object]["save"](
        data, os.path.join(UPLOAD_FOLDER, filename)
    )
    geode_objects.objects_list()[geode_object]["save_viewable"](
        data, os.path.join(UPLOAD_FOLDER, id)
    )

    return flask.make_response({"message": "files regenerated"}, 200)


@geode_routes.route("/convert_geographic_coordinate_system", methods=["POST"])
def convert_geographic_coordinate_system():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
    geode_object = flask.request.form.get("geode_object")
    id = flask.request.form.get("id")
    filename = flask.request.form.get("filename")
    input_crs_authority = flask.request.form.get("input_crs_authority")
    input_crs_code = flask.request.form.get("input_crs_code")
    input_crs_name = flask.request.form.get("input_crs_name")
    output_crs_authority = flask.request.form.get("output_crs_authority")
    output_crs_code = flask.request.form.get("output_crs_code")
    output_crs_name = flask.request.form.get("output_crs_name")

    if geode_object is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No geode_object sent"}, 400
        )
    if id is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No id sent"}, 400
        )
    if filename is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No filename sent"}, 400
        )
    if input_crs_authority is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No input_crs_authority sent"}, 400
        )
    if input_crs_code is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No input_crs_code sent"}, 400
        )
    if input_crs_name is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No input_crs_name sent"}, 400
        )
    if output_crs_authority is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No output_crs_authority sent"}, 400
        )
    if output_crs_code is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No output_crs_code sent"}, 400
        )
    if output_crs_name is None:
        return flask.make_response(
            {"name": "Bad Request", "description": "No output_crs_name sent"}, 400
        )

    input_crs = {
        "authority": input_crs_authority,
        "code": input_crs_code,
        "name": input_crs_name,
    }

    output_crs = {
        "authority": output_crs_authority,
        "code": output_crs_code,
        "name": output_crs_name,
    }

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    data = geode_objects.objects_list()[geode_object]["load"](file_path)

    functions.asign_geographic_coordinate_system_info(geode_object, data, input_crs)
    functions.convert_geographic_coordinate_system_info(geode_object, data, output_crs)

    geode_objects.objects_list()[geode_object]["save"](
        data, os.path.join(UPLOAD_FOLDER, filename)
    )
    geode_objects.objects_list()[geode_object]["save_viewable"](
        data, os.path.join(UPLOAD_FOLDER, id)
    )

    return flask.make_response({"message": "files regenerated"}, 200)
