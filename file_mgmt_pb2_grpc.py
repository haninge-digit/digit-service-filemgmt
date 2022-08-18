# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import file_mgmt_pb2 as file__mgmt__pb2


class FileMgmtStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ListFiles = channel.unary_unary(
                '/FileMgmt/ListFiles',
                request_serializer=file__mgmt__pb2.ListFilesRequest.SerializeToString,
                response_deserializer=file__mgmt__pb2.ListFilesReply.FromString,
                )
        self.ReadFile = channel.unary_unary(
                '/FileMgmt/ReadFile',
                request_serializer=file__mgmt__pb2.ReadFileRequest.SerializeToString,
                response_deserializer=file__mgmt__pb2.ReadFileReply.FromString,
                )


class FileMgmtServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ListFiles(self, request, context):
        """List files in a specified directory with possibly a filename filter applied
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReadFile(self, request, context):
        """Get content of a spcific file
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_FileMgmtServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ListFiles': grpc.unary_unary_rpc_method_handler(
                    servicer.ListFiles,
                    request_deserializer=file__mgmt__pb2.ListFilesRequest.FromString,
                    response_serializer=file__mgmt__pb2.ListFilesReply.SerializeToString,
            ),
            'ReadFile': grpc.unary_unary_rpc_method_handler(
                    servicer.ReadFile,
                    request_deserializer=file__mgmt__pb2.ReadFileRequest.FromString,
                    response_serializer=file__mgmt__pb2.ReadFileReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'FileMgmt', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class FileMgmt(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ListFiles(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/FileMgmt/ListFiles',
            file__mgmt__pb2.ListFilesRequest.SerializeToString,
            file__mgmt__pb2.ListFilesReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ReadFile(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/FileMgmt/ReadFile',
            file__mgmt__pb2.ReadFileRequest.SerializeToString,
            file__mgmt__pb2.ReadFileReply.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
