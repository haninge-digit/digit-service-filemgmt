from concurrent import futures
import logging
import json
import re
import os

import grpc
from digit_file_mgmt import file_mgmt_pb2, file_mgmt_pb2_grpc

from msgraph.core import GraphClient
from azure.identity import ClientSecretCredential


"""
Environment & Globals
"""
TENANT_ID = os.getenv('TENANT_ID', "")
CLIENT_ID = os.getenv('CLIENT_ID', "")
CLIENT_SECRET = os.getenv('CLIENT_SECRET', "")

DEBUG_MODE = os.getenv('DEBUG', 'false') == "true"                       # Global DEBUG logging

LOGFORMAT = "%(asctime)s %(funcName)-10s [%(levelname)s] %(message)s"   # Log format

credential = ClientSecretCredential(TENANT_ID, CLIENT_ID, CLIENT_SECRET)
client = GraphClient(credential=credential)


"""
Service error class
"""


class ServiceError(Exception):
    def __init__(self, code, details=""):
        # grpc.ServicerContext.abort()
        self.code = code
        self.details = details


"""
Service functions
"""


def get_drive_at_site(siteId):
    result = client.get(f"/sites/{siteId}/drive").json()        # Get the sites driveId
    if 'error' in result:
        raise ServiceError(grpc.StatusCode.PERMISSION_DENIED, f"An error occured when getting driveId: {result['error']['message']}")
    return result['id']


def list_files_in_drive(siteId, driveId, path, pattern):
    file_list = {'siteId': siteId, 'driveId': driveId, 'path': path, 'pattern': pattern, 'files': []}

    if not siteId and not driveId:
        raise ServiceError(grpc.StatusCode.INVALID_ARGUMENT, f"Either siteId or driveId must be given")

    if not driveId:
        driveId = get_drive_at_site(siteId)
        file_list['driveId'] = driveId

    if path:
        result = client.get(f"/drives/{driveId}/root:/{path}:/children").json()     # List a known path
    else:
        result = client.get(f"/drives/{driveId}/root/children").json()      # List the root folder
    if 'error' in result:
        raise ServiceError(grpc.StatusCode.PERMISSION_DENIED, f"An error occured when listing drive: {result['error']['message']}")

    try:
        r = re.compile(pattern)
    except re.error:
        raise ServiceError(grpc.StatusCode.INVALID_ARGUMENT, f"'{pattern}' is not a valid RegExp expression")

    for file in result['value']:
        if r.match(file['name']):
            if 'folder' in file:
                type = "folder"
            elif 'file' in file:
                type = file['file']['mimeType']
            else:
                type = "Unknown"
            file_info = {
                'name': file['name'],
                'type': type,
                'created': file['fileSystemInfo']['createdDateTime'],
                'modified': file['fileSystemInfo']['lastModifiedDateTime'],
                'id': file['id']
            }
            file_list['files'].append(file_info)

    return file_list


def read_file_content(siteId, driveId, path, fileName, itemId):
    if not driveId:
        driveId = get_drive_at_site(siteId)

    if not itemId:
        file_list = list_files_in_drive(siteId, driveId, path, fileName)
        if len(file_list['files']) == 0:
            raise ServiceError(grpc.StatusCode.NOT_FOUND, f"{fileName} not found!")
        if len(file_list['files']) != 1:
            raise ServiceError(grpc.StatusCode.NOT_FOUND, f"More than one {fileName} found???")

        itemId = file_list['files'][0]['id']        # Get the ID of the file from the search
        fileType = file_list['files'][0]['type']    # Also save the file type
    else:
        fileType = ""       # Blank for now. Might implement a get_file_type function later

    result = client.get(f"/drives/{driveId}/items/{itemId}/content")
    if 'error' in result:
        raise ServiceError(grpc.StatusCode.PERMISSION_DENIED, f"An error occured when reading the file: {result['error']['message']}")

    return fileType, result.content


"""
gRPC worker
"""


class FileMgmt(file_mgmt_pb2_grpc.FileMgmtServicer):

    def ListFiles(self, request, context):
        try:
            file_list = list_files_in_drive(request.siteId, request.driveId, request.path, request.pattern)
        except ServiceError as e:
            logging.error(e.details)
            context.abort(e.code, e.details)

        return file_mgmt_pb2.ListFilesReply(files=json.dumps(file_list))

    def ReadFile(self, request, context):
        try:
            type, content = read_file_content(request.siteId, request.driveId, request.path, request.fileName, request.fileId)
        except ServiceError as e:
            logging.error(e.details)
            context.abort(e.code, e.details)

        return file_mgmt_pb2.ReadFileReply(type=type, content=content)


"""
Run gRPC server
"""


def run_server():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))        # Get a threaded server instance
    file_mgmt_pb2_grpc.add_FileMgmtServicer_to_server(FileMgmt(), server)     # Add our endpoint to the server

    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)

    logging.info(f"Starting file_mgmt gRPC service on {listen_addr}")
    server.start()      # Start the server

    server.wait_for_termination()   # Wait for termination signal
    logging.info(f"Got terminations signal. Stopping file_mgmt gRPC service")
    server.stop(5)      # Wait another 5 seconds for things to complete
    logging.info(f"Shutting down")


if __name__ == '__main__':
    # Enable logging. INFO is default. DEBUG if requested
    logging.basicConfig(level=logging.DEBUG if DEBUG_MODE else logging.INFO, format=LOGFORMAT)

    run_server()     # Run the server
