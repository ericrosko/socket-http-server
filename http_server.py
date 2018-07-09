#!/usr/bin/env python3

import socket
import sys
import traceback
import os
import mimetypes

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->

        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """
    return b"\r\n".join([
        b"HTTP/1.1 200 OK",
        b"Content-Type: " + mimetype,
        b"",
        body,
    ])


def parse_request(request):
    """
    Given the content of an HTTP request, returns the uri of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.

    GET /pub/WWW/TheProject.html HTTP/1.1
    GET / HTTP/1.1
    """

    print("trying to parse request:", request)
    lines = request.split("\r\n")
    print("lines", lines)
    first_line_components = lines[0].split(" ")
    method = first_line_components[0]
    path = first_line_components[1]
    # method, path, version = request.split("\r\n")[0].split(" ")

    if method != "GET":
        raise NotImplementedError

    return path


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""
    return b"\r\n".join([
        b"HTTP/1.1 405 Method Not Allowed",
        b"",
        b"You can't do that on this server!",
    ])


def retrieve_bytes(path):
    """
    will retrieve a txt file in bytes

    :param path: str must not have leading / !
    """
    assert path[0] != '/', "cannot have leading / before os.path.join"
    local_path = os.path.join('webroot', path)
    with open(local_path, 'rb') as f:
        file_contents = f.read()

    return file_contents

def retrieve_mimetype(path):
    """
    'text/plain' .txt
    'image/jpeg'
    'text/html'
    'text/png' .png
    'image/vnd.microsoft.icon' .ico
    """
    extension = os.path.splitext(path)[1]
    result = mimetypes.types_map[extension]
    return str.encode(result)

def response_not_found():
    """Returns a 404 Not Found response"""
    return b"\r\n".join([
        b"HTTP/1.1 404 File Not Found",
        b"", # this line must be blank!
        b"<h1>404 Not Found</h1>",
    ])


def resolve_uri(uri):
    """
    This method should return appropriate content and a mime type.

    If the requested URI is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the URI is a file, it should return the contents of that file
    and its correct mimetype.

    If the URI does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.

    Ex:
        resolve_uri('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        resolve_uri('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        resolve_uri('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        resolve_uri('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """

    # TODO: Raise a NameError if the requested content is not present
    # under webroot.

    # TODO: Fill in the appropriate content and mime_type give the URI.
    # See the assignment guidelines for help on "mapping mime-types", though
    # you might need to create a special case for handling make_time.py
    content = b"not implemented"
    mime_type = b"not implemented"

    local_path = os.path.join('webroot', uri[1:])

    if os.path.isfile(local_path):
        content = retrieve_bytes(uri[1:])
        mime_type = retrieve_mimetype(uri[1:])
    elif os.path.isdir(local_path):
        mime_type = b"text/plain"
        files = uri
        for item in os.listdir(local_path):
            files += ", " + item
        content = files.encode()
    else:
        raise NameError

    assert isinstance(content, bytes)
    assert isinstance(mime_type, bytes)

    return content, mime_type


def server(log_buffer=sys.stderr):
    """
    main loop
    """
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            response = b'' # just adding this up here in case I ctrl+C
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(16)
                    print('received "{0}"'.format(data), file=log_buffer)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        print("breaking request.")
                        break

                print()
                print("Request received:\n{}\n\n".format(request))


                try:
                    path = parse_request(request)
                    print("path is: ", path)

                    # note if i don't strip the leading / then the 'webroot'
                    # portion will not be added.
                    # if path[0] == '/':
                    #     path = path[1:]
                    # local_path = os.path.join('webroot', path)
                    # print("local path is", local_path)
                    # body = b''
                    # with open(local_path, 'rb') as f:
                    #     print('f.read()', f.read())
                        # body = f.read().encode()

                    content, mime_type = resolve_uri(path)
                    response = response_ok(
                        body=content,
                        mimetype=mime_type
                    )

                    # response = b"HTTP/1.1 200 OK\r\n" + \
                    #     b"Content-Type: text\r\n" + \
                    #     b"\r\n" + \
                    #     b"This is a very simple text file.\n" + \
                    #     b"Just to show that we can server it up.\n" + \
                    #     b"It is three lines long.\n"
                except NameError:
                    response = response_not_found()

                except NotImplementedError:
                    response = response_method_not_allowed()
                # if data:
                #     print('sending data back to client', file=log_buffer)
                #     conn.sendall(data)
                # else:
                #     msg = 'no more data from {0}:{1}'.format(*addr)
                #     print(msg, log_buffer)
                #     break
                conn.sendall(response)
            except:
                traceback.print_exc()
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
