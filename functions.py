import base64
import geode_objects
import os
import pkg_resources
import werkzeug
import flask
import uuid

def list_objects_input_extensions(geode_objects: array = [],is_viewable: bool=True):
    """
    Purpose:
        Function that returns a list of all input extensions
    Returns:
        An ordered list of input file extensions
    """
    return_list = []
    objects_list = geode_objects.objects_list()

    for object_ in objects_list.values():
        if values['is_viewable'] == is_viewable or object_ in geode_objects:
            values = object_['input']
            for value in values:
                list_creators = value.list_creators()
                for creator in list_creators:
                    if creator not in return_list:
                        return_list.append(creator)
    return_list.sort()
    return return_list

def list_objects(extension: str, is_viewable: bool=True):
    """
    Purpose:
        Function that returns a list of objects that can handle a file, given his extension
    Args:
        extension -- The extension of the file
    Returns:
        An ordered list of object's names
    """
    return_list = []
    objects_list = geode_objects.objects_list()

    for object_, values in objects_list.items():
        if values['is_viewable'] == is_viewable:
            list_values = values['input']
            for value in list_values:
                if value.has_creator(extension):
                    if object_ not in return_list:
                        return_list.append(object_)
    return_list.sort()
    return return_list

def list_output_file_extensions(object: str):
    """
    Purpose:
        Function that returns a list of output file extensions that can be handled by an object
    Args:
        object -- The name of the object
    Returns:
        An ordered list of file extensions
    """
    List = []
    objects_list = geode_objects.objects_list()

    values = objects_list[object]['output']
    for value in values:
        list_creators = value.list_creators()
        for creator in list_creators:
            if creator not in List:
                List.append(creator)
    List.sort()
    return List


def get_versions(list_packages: list):
    list_with_versions = []
    for package in list_packages:
        list_with_versions.append({"package": package, "version": pkg_resources.get_distribution(package).version})
    return list_with_versions

def upload_file(file: str, file_name: str, upload_folder: str, file_size: int):
    if not os.path.exists(upload_folder):
        os.mkdir(upload_folder)
    file_decoded = base64.b64decode(file.split(',')[-1])
    secure_file_name = werkzeug.utils.secure_filename(file_name)
    file_path = os.path.join(upload_folder, secure_file_name)
    f = open(file_path, "wb")
    f.write(file_decoded)
    f.close()

    final_size =  os.path.getsize(file_path)
    return int(file_size) == int(final_size)

def create_lock_file():
    LOCK_FOLDER = flask.current_app.config['LOCK_FOLDER']
    if not os.path.exists(LOCK_FOLDER):
        os.mkdir(LOCK_FOLDER)
    flask.g.UUID = uuid.uuid4()
    file_path = f'{LOCK_FOLDER}/{str(flask.g.UUID)}.txt'
    f = open(file_path, 'a')
    f.close()

def remove_lock_file():
    LOCK_FOLDER = flask.current_app.config['LOCK_FOLDER']
    os.remove(f'{LOCK_FOLDER}/{str(flask.g.UUID)}.txt')
    