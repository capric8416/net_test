import base64
import json

import requests

from public import Public

if __name__ == '__main__':
    # init public
    pub = Public()
    # random generate aes key & sign
    encrypt_b64_key, key_sign = pub.gen_aes_keys()

    # start http client session
    session = requests.Session()

    host = 'http://127.0.0.1:8000/'

    # put encrypted aes key in header just for 1st request
    # put aes key sign for all requests
    other_headers = {'i': key_sign, 'mimetype': 'text/plain'}
    first_only_headers = {'k': encrypt_b64_key}
    first_only_headers.update(other_headers)

    # fetch decoder features
    path1 = pub.aes_encrypt('/decoder/features')
    resp1 = session.get(url=host + path1, headers=first_only_headers)
    assert resp1.status_code == 200
    data1 = json.loads(pub.aes_decrypt(resp1.text))
    print(data1)

    # set hot spot name
    path2 = pub.aes_encrypt('/hot_spot?name=test')
    resp2 = session.patch(url=host + path2, headers=other_headers)
    assert resp2.status_code == 200
    data2 = json.loads(pub.aes_decrypt(resp2.text))
    print(data2)

    # connect wifi
    path3 = pub.aes_encrypt('/wifi')
    request_data = pub.aes_encrypt(
        json.dumps({
            'wifi_name': 'name',
            'wifi_encryption': 'wpa2_psk',
            'wifi_password': 'password'
        })
    )
    resp3 = session.post(url=host + path3, headers=other_headers, data=request_data)
    assert resp3.status_code == 200
    data3 = json.loads(pub.aes_decrypt(resp3.text))
    print(data3)

    # error 1: path is not encoded by base64
    path4 = '/error/x1/info'
    resp4 = session.get(url=host + path4, headers=other_headers)
    assert resp4.status_code == 400
    data4 = json.loads(resp4.text)
    print(data4)

    # error 2: path is not encrypted by aes
    path5 = base64.b64encode('/error/x2'.encode()).decode()
    resp5 = session.get(url=host + path5, headers=other_headers)
    assert resp5.status_code == 400
    data5 = json.loads(resp5.text)
    print(data5)

    # error 3: path not found
    path6 = pub.aes_encrypt('/error/x3')
    resp6 = session.get(url=host + path6, headers=other_headers)
    assert resp6.status_code == 404
    data6 = json.loads(resp6.text)
    print(data6)

    # error 4: invalid aes key
    pub.gen_aes_keys()
    path7 = pub.aes_encrypt('/error/x4')
    resp7 = session.get(url=host + path7, headers=other_headers)
    assert resp7.status_code == 400
    data7 = json.loads(resp7.text)
    print(data7)
