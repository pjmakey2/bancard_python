import requests
import urllib
import md5
import subprocess
iframeb = """
<! DOCTYPE html>
<html lang='en'>
 <head>
 <meta charset='UTF-8'>
 <title>iFrame</title>
<script
  src="https://code.jquery.com/jquery-2.2.4.min.js"
  integrity="sha256-BbhdlvQf/xTY9gja0Dq3HiwQF8LaCRTXxZKRutelT44="
  crossorigin="anonymous"></script>
 <script

   src='http://localhost/bancard/bancardV2.js'></script>
 </head>
 <script type='application/javascript'>
 styles = {{
 'form-background-color': '#001b60',
 'button-background-color': '#4faed1',
 'button-text-color': '#fcfcfc',
 'button-border-color': '#dddddd',
 'input-background-color': '#fcfcfc',
 'input-text-color': '#111111',
 'input-placeholder-color': '#111111'
 }};
 window. onload = function () {{
 Bancard.Cards. createForm ('iframe-container', '{}',
styles);
 }};
 </script>
 <body>
 <h1 style='text-align: center'>iFrame vPos</h1>
 <div style='height: 300px; width: 500px; margin: auto' id='iframe-container' ></div>

 </body>
</html>
"""

HEADERS = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
    'Content-Type': 'application/json'
}
# Nombre:
# MasterCard
# Número:
# Vencimiento: 8/21
# Código de seguridad:
# 258
# url = 'https://vpos.service.sandbox:4485/vpos/api/0.3/cards/new'

public_key = ''
private_key = ''
user_id = 'xxx'
card_id = 'xxx'
correo = 'xxx@xxx.com'
telefono = 'xxx'
metodo = 'request_user_cards'
# metodo = 'request_new_card'

main_url = 'vpos.infonet.com.py:8888'

def generate_token(private_key, card_id, user_id, metodo, public_key, telefono, correo):
    if metodo == 'request_user_cards':
        ll = [private_key, user_id, metodo]        

        djson =  {
            "public_key": public_key,
            "operation": {
                "token": md5.md5(''.join(map(str, ll))).hexdigest(),
            },
            "test_client": False
        }
        url = 'https://{}/vpos/api/0.3/users/{}/cards'.format(main_url, user_id)
    if metodo == 'request_new_card':
        ll = [private_key, card_id, user_id, metodo]
        djson = {
            "public_key": public_key,
            "operation": {
                "token": md5.md5(''.join(map(str, ll))).hexdigest(),
                "card_id": card_id,
                "user_id": user_id,
                "user_cell_phone": telefono,
                "user_mail": correo,
                # "return_url": "https://comercios.bancard.com.py/services/vpos/test_case_new_card/result"
                "return_url": "http://159.65.188.177:5000/"
            },
            "test_client": False
        }
        url = 'https://{}/vpos/api/0.3/cards/new'.format(main_url)
    return djson, url


data, url = generate_token(private_key, card_id, user_id, 'request_new_card', public_key, telefono, correo)
resp = requests.post(url, json=data, headers=HEADERS)
respc = resp.json()
if respc and respc.get('status') == 'success':
    fname = '/var/www/html/bancard/iframe_bancard_{}.html'.format(card_id)
    with open(fname, 'w') as iff:
        iff.write(iframeb.format(respc.get('process_id')))
    cmd = '/usr/bin/google-chrome {}'.format(fname)
    print cmd
    subprocess.Popen(cmd, shell=True)
    
data, url = generate_token(private_key, card_id, user_id, 'request_user_cards', public_key, telefono, correo)
resp = requests.post(url, json=data, headers=HEADERS)
print resp.text, 'LISTANDO'
