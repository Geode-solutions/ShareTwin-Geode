# Standard library imports
import os
import shutil
import uuid

# Third party imports
import flask
import flask_cors
import werkzeug

from opengeodeweb_back import geode_functions
import opengeode_geosciences as og_gs

share_twin_routes = flask.Blueprint("share_twin_routes", __name__)
flask_cors.CORS(share_twin_routes)


@share_twin_routes.before_request
def before_request():
    geode_functions.create_lock_file(flask.current_app.config["LOCK_FOLDER"])


@share_twin_routes.teardown_request
def teardown_request(exception):
    geode_functions.remove_lock_file(flask.current_app.config["LOCK_FOLDER"])


@share_twin_routes.route("/allowed_files", methods=["GET"])
def allowed_files():
    extensions = geode_functions.list_input_extensions()
    return flask.make_response({"extensions": extensions}, 200)


@share_twin_routes.route("/allowed_objects", methods=["POST"])
def allowed_objects():
    array_variables = ["filename"]
    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )
    file_extension = geode_functions.get_extension_from_filename(
        variables_dict["filename"]
    )
    allowed_objects = geode_functions.list_geode_objects(file_extension)
    return flask.make_response({"allowed_objects": allowed_objects}, 200)


@share_twin_routes.route("/geode_object_allowed_files", methods=["POST"])
def geode_object_allowed_files():
    array_variables = ["geode_object"]
    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )
    extensions = geode_functions.get_geode_object_input_extensions(
        variables_dict["geode_object"]
    )
    return flask.make_response({"extensions": extensions}, 200)


@share_twin_routes.route("/convert_file", methods=["POST"])
def convert_file():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
    array_variables = ["geode_object", "file", "old_file_name", "file_size"]
    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )

    secure_file_name = werkzeug.utils.secure_filename(variables_dict["old_file_name"])
    absolute_file_path = os.path.join(UPLOAD_FOLDER, secure_file_name)
    generated_id = str(uuid.uuid4()).replace("-", "")

    uploaded_file = geode_functions.upload_file(
        variables_dict["file"],
        secure_file_name,
        UPLOAD_FOLDER,
        variables_dict["file_size"],
    )

    data = geode_functions.load(variables_dict["geode_object"], absolute_file_path)

    if geode_functions.is_viewable(variables_dict["geode_object"]):
        name = data.name()
    else:
        name = variables_dict["old_file_name"]

    native_extension = data.native_extension()

    absolute_native_file_path = os.path.join(
        UPLOAD_FOLDER, generated_id + "." + native_extension
    )

    saved_viewable_file_path = geode_functions.save_viewable(
        variables_dict["geode_object"], data, UPLOAD_FOLDER, generated_id
    )
    geode_functions.save(
        variables_dict["geode_object"],
        data,
        UPLOAD_FOLDER,
        generated_id + "." + native_extension,
    )

    native_file_name = os.path.basename(absolute_native_file_path)
    viewable_file_name = os.path.basename(saved_viewable_file_path)

    return flask.make_response(
        {
            "name": name,
            "native_file_name": native_file_name,
            "viewable_file_name": viewable_file_name,
            "id": generated_id,
        },
        200,
    )


@share_twin_routes.route("/texture_coordinates", methods=["POST"])
def texture_coordinates():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
    array_variables = ["geode_object", "native_file_name"]
    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )

    native_file_path = os.path.join(UPLOAD_FOLDER, variables_dict["native_file_name"])
    data = geode_functions.load(variables_dict["geode_object"], native_file_path)
    texture_coordinates = data.texture_manager().texture_names()

    return flask.make_response({"texture_coordinates": texture_coordinates}, 200)


@share_twin_routes.route("/geographic_coordinate_systems", methods=["POST"])
def crs_converter_geographic_coordinate_systems():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
    array_variables = ["geode_object"]
    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )
    infos = geode_functions.get_geographic_coordinate_systems(
        variables_dict["geode_object"]
    )
    crs_list = []

    for info in infos:
        crs = {}
        crs["name"] = info.name
        crs["code"] = info.code
        crs["authority"] = info.authority
        crs_list.append(crs)
    return flask.make_response({"crs_list": crs_list}, 200)


@share_twin_routes.route("/coordinate_systems", methods=["POST"])
def coordinate_systems():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
    array_variables = ["geode_object", "native_file_name"]
    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )

    native_file_path = os.path.join(UPLOAD_FOLDER, variables_dict["native_file_name"])
    data = geode_functions.load(variables_dict["geode_object"], native_file_path)
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


@share_twin_routes.route("/assign_geographic_coordinate_system", methods=["POST"])
def assign_geographic_coordinate_system():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]
    array_variables = [
        "geode_object",
        "id",
        "filename",
        "crs_authority",
        "crs_code",
        "crs_name",
    ]
    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )

    input_crs = {
        "authority": variables_dict["crs_authority"],
        "code": variables_dict["crs_code"],
        "name": variables_dict["crs_name"],
    }

    file_path = os.path.join(UPLOAD_FOLDER, variables_dict["filename"])
    data = geode_functions.load(variables_dict["geode_object"], file_path)

    geode_functions.assign_geographic_coordinate_system_info(
        variables_dict["geode_object"], data, input_crs
    )

    geode_functions.save(
        variables_dict["geode_object"],
        data,
        UPLOAD_FOLDER,
        variables_dict["filename"],
    )
    geode_functions.save_viewable(
        variables_dict["geode_object"], data, UPLOAD_FOLDER, variables_dict["id"]
    )

    return flask.make_response({}, 200)


@share_twin_routes.route("/convert_geographic_coordinate_system", methods=["POST"])
def convert_geographic_coordinate_system():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]

    array_variables = [
        "geode_object",
        "id",
        "filename",
        "output_crs_authority",
        "output_crs_code",
        "output_crs_name",
    ]
    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )

    output_crs = {
        "authority": variables_dict["output_crs_authority"],
        "code": variables_dict["output_crs_code"],
        "name": variables_dict["output_crs_name"],
    }

    absolute_file_path = os.path.join(UPLOAD_FOLDER, variables_dict["filename"])
    data = geode_functions.load(variables_dict["geode_object"], absolute_file_path)

    geode_functions.convert_geographic_coordinate_system_info(
        variables_dict["geode_object"], data, output_crs
    )

    geode_functions.save(
        variables_dict["geode_object"], data, UPLOAD_FOLDER, variables_dict["filename"]
    )
    geode_functions.save_viewable(
        variables_dict["geode_object"], data, UPLOAD_FOLDER, variables_dict["id"]
    )

    return flask.make_response({}, 200)


@share_twin_routes.route("/coordinate_reference_system_exists", methods=["POST"])
def coordinate_system_name_exists():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]

    array_variables = [
        "geode_object",
        "filename",
        "coordinate_system_name",
    ]

    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )

    absolute_file_path = os.path.join(UPLOAD_FOLDER, variables_dict["filename"])
    data = geode_functions.load(variables_dict["geode_object"], absolute_file_path)

    coordinate_reference_system_exists = data.main_coordinate_reference_system_manager().coordinate_reference_system_exists(
        variables_dict["coordinate_system_name"]
    )

    return flask.make_response(
        {"coordinate_reference_system_exists": coordinate_reference_system_exists}, 200
    )


@share_twin_routes.route("/georeference", methods=["POST"])
def georeference():
    UPLOAD_FOLDER = flask.current_app.config["UPLOAD_FOLDER"]

    array_variables = [
        "geode_object",
        "id",
        "filename",
        "coordinate_system_name",
        "input_origin_x",
        "input_origin_y",
        "input_point_1_x",
        "input_point_1_y",
        "input_point_2_x",
        "input_point_2_y",
        "output_origin_x",
        "output_origin_y",
        "output_point_1_x",
        "output_point_1_y",
        "output_point_2_x",
        "output_point_2_y",
    ]
    variables_dict = geode_functions.get_form_variables(
        flask.request.form, array_variables
    )

    input_coordinate_points = {
        "origin_x": float(variables_dict["input_origin_x"]),
        "origin_y": float(variables_dict["input_origin_y"]),
        "point_1_x": float(variables_dict["input_point_1_x"]),
        "point_1_y": float(variables_dict["input_point_1_y"]),
        "point_2_x": float(variables_dict["input_point_2_x"]),
        "point_2_y": float(variables_dict["input_point_2_y"]),
    }

    output_coordinate_points = {
        "origin_x": float(variables_dict["output_origin_x"]),
        "origin_y": float(variables_dict["output_origin_y"]),
        "point_1_x": float(variables_dict["output_point_1_x"]),
        "point_1_y": float(variables_dict["output_point_1_y"]),
        "point_2_x": float(variables_dict["output_point_2_x"]),
        "point_2_y": float(variables_dict["output_point_2_y"]),
    }

    data = geode_functions.load(variables_dict["geode_object"], file_path)

    geode_functions.create_coordinate_system(
        variables_dict["geode_object"],
        data,
        variables_dict["coordinate_system_name"],
        input_coordinate_points,
        output_coordinate_points,
    )

    geode_functions.save(
        variables_dict["geode_object"],
        data,
        UPLOAD_FOLDER,
        variables_dict["filename"],
    )
    geode_functions.save_viewable(
        variables_dict["geode_object"],
        data,
        UPLOAD_FOLDER,
        variables_dict["id"],
    )

    return flask.make_response({}, 200)
