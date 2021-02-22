import binascii
import json
import traceback

from flask import Flask, request, Response
from werkzeug.datastructures import Headers

from private import Private

app = Flask(__name__)

keys = {}


def get_decoder_features(pvt, path, body):
    print(path)
    _ = body

    return Response(
        status=200,
        mimetype='text/plain',
        headers=Headers({'e': 1}),
        response=pvt.aes_encrypt(
            json.dumps(
                {
                    'resolution': {
                        'width': 1920,
                        'height': 1080
                    },
                    'fps': 60,
                    'bitrate': 8000
                }
            )
        )
    )


def patch_hot_spot(pvt, path, body):
    print(path)
    _ = body

    return Response(
        status=200,
        mimetype='text/plain',
        headers=Headers({'e': 1}),
        response=pvt.aes_encrypt(
            json.dumps(
                {
                    'message': 'set hot spot name success'
                }
            )
        )
    )


def post_wifi(pvt, path, body):
    print(path)
    print(pvt.aes_decrypt(body.decode()))

    return Response(
        status=200,
        mimetype='text/plain',
        headers=Headers({'e': 1}),
        response=pvt.aes_encrypt(
            json.dumps(
                {
                    'message': 'connect wifi success'
                }
            )
        )
    )


@app.route('/', defaults={'cipher_path': ''})
@app.route('/<path:cipher_path>', methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'])
def dispatch(cipher_path):
    # check aes key sign
    aes_key_sign = request.headers.get('i', '')
    if len(aes_key_sign) != 40:
        return Response(
            status=400,
            mimetype='application/json',
            headers=Headers({'e': 0}),
            response=json.dumps({'message': 'invalid i'})
        )

    # check encrypted aes key
    encrypt_b64_key = request.headers.get('k', '')
    if aes_key_sign in keys:
        if len(encrypt_b64_key) != 0:
            return Response(
                status=400,
                mimetype='application/json',
                headers=Headers({'e': 0}),
                response=json.dumps({'message': 'do not need k'})
            )
        # get private
        pvt = keys[aes_key_sign]
    else:
        # init private
        pvt = Private()
        if len(encrypt_b64_key) != 684:
            return Response(
                status=400,
                mimetype='application/json',
                headers=Headers({'e': 0}),
                response=json.dumps({'message': 'invalid k'})
            )

        try:
            # decrypt aes key
            pvt.get_aes_key(encrypt_b64_key)
        except ValueError:
            traceback.print_exc()
            return Response(
                status=400,
                mimetype='application/json',
                headers=Headers({'e': 0}),
                response=json.dumps({'message': 'invalid rsa key'})
            )

        # store aes key
        keys[aes_key_sign] = pvt

    try:
        path = pvt.aes_decrypt(cipher_path)
    except binascii.Error:
        traceback.print_exc()
        return Response(
            status=400,
            mimetype='application/json',
            headers=Headers({'e': 0}),
            response=json.dumps({'message': 'path is not encoded'})
        )
    except ValueError:
        traceback.print_exc()
        return Response(
            status=400,
            mimetype='application/json',
            headers=Headers({'e': 0}),
            response=json.dumps({'message': 'path is not encrypted'})
        )

    if path is None:
        return Response(
            status=400,
            mimetype='application/json',
            headers=Headers({'e': 0}),
            response=json.dumps({'message': 'invalid aes key'})
        )
    elif path.startswith('/decoder/features'):
        return get_decoder_features(pvt=pvt, path=path, body=request.data)
    elif path.startswith('/hot_spot'):
        return patch_hot_spot(pvt=pvt, path=path, body=request.data)
    elif path.startswith('/wifi'):
        return post_wifi(pvt=pvt, path=path, body=request.data)
    else:
        return Response(
            status=404,
            mimetype='application/json',
            headers=Headers({'e': 0}),
            response=json.dumps({'message': 'path not found'})
        )


if __name__ == '__main__':
    app.run(port=8000)
