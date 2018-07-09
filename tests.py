#!/usr/bin/env python3

import unittest
import subprocess
import http.client
import os

# helper functions
from http_server import retrieve_mimetype
from http_server import retrieve_bytes

"""
python -m unittest -v tests.py
python3 -m unittest -v tests.WebTestCase.test_root_index
python3 -m unittest -v tests.WebTestCase

"""

class WebTestCase(unittest.TestCase):
    """tests for the echo server and client"""

    def setUp(self):
        self.server_process = subprocess.Popen(
            [
                "python",
                "http_server.py"
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def tearDown(self):
        self.server_process.kill()
        self.server_process.communicate()

    def get_response(self, url):
        """
        Helper function to get a response from a given url, using http.client
        """

        conn = http.client.HTTPConnection('localhost:10000')
        conn.request('GET', url)

        response = conn.getresponse()

        conn.close()

        return response

    def test_retrieve_mimetype(self):
        self.assertEqual(b'text/plain', retrieve_mimetype('/sample.txt'))
        self.assertEqual(b'image/png', retrieve_mimetype('images/sample.png'))
        self.assertEqual(b'image/jpeg', retrieve_mimetype('/images/sample.jpg'))
        self.assertEqual(b'image/vnd.microsoft.icon', retrieve_mimetype('images/sample.ico'))
        self.assertEqual(b'text/html', retrieve_mimetype('test.html'))

    def test_retrieve_bytes(self):

        expected = \
            b"This is a very simple text file.\n" + \
            b"Just to show that we can server it up.\n" + \
            b"It is three lines long.\n"

        result = retrieve_bytes('sample.txt')
        self.assertTrue(isinstance(result, bytes))
        self.assertEqual(expected, result)

    def test_get_sample_text_content(self):
        """
        A call to /sample.txt returns the correct body
        """
        file = 'sample.txt'

        # local_path = os.path.join('webroot', *file.split('/'))
        local_path = os.path.join('webroot', file)

        web_path = '/' + file
        error_comment = "Error encountered while visiting " + web_path

        # <http.client.HTTPResponse object at 0x101bcb4e0>
        response = self.get_response(web_path)

        print()
        print("test local path:::", local_path)
        print("test response", response)

        # note you only
        # print("test response.read()", response.read())
        print("test getcode", response.getcode())
        print()
        # print("test response.read()", response.

        self.assertEqual(response.getcode(), 200, error_comment)

        with open(local_path, 'rb') as f:
            file_contents = f.read()

        print("test file_contents:", file_contents)
        print()
        self.assertEqual(file_contents, response.read(), error_comment)

    def test_get_sample_text_mime_type(self):
        """
        A call to /sample.txt returns the correct mimetype
        """
        file = 'sample.txt'

        web_path = '/' + file
        error_comment = "Error encountered while visiting " + web_path

        response = self.get_response(web_path)

        self.assertEqual(response.getcode(), 200, error_comment)
        self.assertEqual(response.getheader('Content-Type'), 'text/plain', error_comment)

    def test_get_sample_scene_balls_jpeg(self):
        """
        A call to /images/Sample_Scene_Balls.jpg returns the correct body
        """
        file = 'images/Sample_Scene_Balls.jpg'

        local_path = os.path.join('webroot', *file.split('/'))
        web_path = '/' + file
        error_comment = "Error encountered while visiting " + web_path

        response = self.get_response(web_path)

        self.assertEqual(response.getcode(), 200, error_comment)

        with open(local_path, 'rb') as f:
            self.assertEqual(f.read(), response.read(), error_comment)

    def test_get_sample_scene_balls_jpeg_mime_type(self):
        """
        A call to /images/Sample_Scene_Balls.jpg returns the correct mimetype
        """
        file = 'images/Sample_Scene_Balls.jpg'

        web_path = '/' + file
        error_comment = "Error encountered while visiting " + web_path

        response = self.get_response(web_path)

        self.assertEqual(response.getcode(), 200, error_comment)
        self.assertEqual(response.getheader('Content-Type'), 'image/jpeg', error_comment)

    def test_get_sample_1_png(self):
        """
        A call to /images/sample_1.png returns the correct body
        """
        file = 'images/sample_1.png'

        local_path = os.path.join('webroot', *file.split('/'))
        web_path = '/' + file
        error_comment = "Error encountered while visiting " + web_path

        response = self.get_response(web_path)

        self.assertEqual(response.getcode(), 200, error_comment)

        with open(local_path, 'rb') as f:
            self.assertEqual(f.read(), response.read(), error_comment)

    def test_get_sample_1_png_mime_type(self):
        """
        A call to /images/sample_1.png returns the correct mimetype
        """
        file = 'images/sample_1.png'

        web_path = '/' + file
        error_comment = "Error encountered while visiting " + web_path

        response = self.get_response(web_path)

        self.assertEqual(response.getcode(), 200, error_comment)
        self.assertEqual(response.getheader('Content-Type'), 'image/png', error_comment)

    def test_get_404(self):
        """
        A call to /asdf.txt (a file which does not exist in webroot) yields a 404 error
        """
        file = 'asdf.txt'

        web_path = '/' + file
        error_comment = "Error encountered while visiting " + web_path

        response = self.get_response(web_path)

        self.assertEqual(response.getcode(), 404, error_comment)

    def test_images_index(self):
        """
        A call to /images/ yields a list of files in the images directory
        """

        directory = 'images'
        local_path = os.path.join('webroot', directory)
        web_path = '/' + directory
        error_comment = "Error encountered while visiting " + web_path

        response = self.get_response(web_path)
        body = response.read().decode()

        for path in os.listdir(local_path):
            self.assertIn(path, body, error_comment)

    def test_root_index(self):
        """
        A call to / yields a list of files in the images directory
        """

        directory = ''
        local_path = os.path.join('webroot', directory)
        web_path = '/' + directory
        error_comment = "Error encountered while visiting " + web_path

        response = self.get_response(web_path)
        body = response.read().decode()

        for path in os.listdir(local_path):
            self.assertIn(path, body, error_comment)



if __name__ == '__main__':
    unittest.main()
