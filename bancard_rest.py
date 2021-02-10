#coding: utf-8
import argparse
import requests
import urllib
import md5
import subprocess
HEADERS = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
    'Content-Type': 'application/json'
}
public_key = 'n0kgCvDGAbsNP7ddBcdbdDcmWCDKqoCO'
private_key = '9PA6EbH6tlRoQltQYOJT9xBNHyUhqJashcni2G73'
user_id = '9661000'
card_id = '8601010000000013'
ccv = None
vto = '8/21'
seguridad = 258
correo = 'xxx@xxx.com'
telefono = 'xxx'
metodo = 'request_user_cards'
# metodo = 'request_new_card'
main_url = 'vpos.infonet.com.py:8888'

bcs = requests.Session()

def create_new_car(*args, **kwargs):
    qa = {
        u'¿Dónde recibe su extracto de algunas de sus tarjetas de crédito?': "Brasilia 765 c/ Siria",
        u'¿Dónde recibís tu extracto de algunas de tus tarjetas de crédito?': "Brasilia 765 c/ Siria",
        u'¿Cuál es tu mes de nacimiento?': "Dec, Feb, Set",
        u'¿Cuál fue su última transacción?': "2017/11/28 15:54:48 - Stock - 6000.00",
        u'Cual fue su ultima transaccion?': "2017/11/28 15:54:48 - Stock - 6000.00",
        u'¿algunas de estas es tu tarjeta de crédito?': ["Medalla - Credicard - 4058", "Medalla - Mastercad - 5789"],
        u'¿algunas de estas es tu tarjeta de débito?': ["Medalla - Credicard - 4058", "Medalla - Mastercad - 5789"],
        u'¿Alguna de tus tarjetas de débito termina con estos números?':  ["Medalla - Credicard - 4058", "Medalla - Mastercad - 5789"],
    }
    card_id = kwargs.get('card_id')
    vto = kwargs.get('vto')
    ccv = kwargs.get('ccv')
    user_id = kwargs.get('user_id')
    #check_payload = {'card_number': card_id}
    #check_data = 'https://vpos.infonet.com.py:8888/cards/card_data'
    #{type: "credit"}
    #check_rsp = bcs.get(check_data, json=check_payload, header=HEADERS)
    data, url = generate_token(private_key, card_id, user_id, 'request_new_card', public_key, telefono, correo)
    resp = bcs.post(url, json=data, headers=HEADERS)
    check_rsp = resp.json()
    month, year = vto.split('/')
    confirm_payload = {
        'card_number': card_id,
        'exp_month': month.zfill(2),
        'exp_year': year,
        'ccv': ccv,
        'commission_info': False,
        'additional_data': '',
        'ci': user_id,
        'process_id': check_rsp.get('process_id'),
        #'is_test_client': False
    }
    print(confirm_payload)
    
    confirm_url = 'https://vpos.infonet.com.py:8888/checkout/register_card'
    confirm_rsp = bcs.post(confirm_url, params=confirm_payload, headers=HEADERS)
    if confirm_rsp.get('message')  == "add_new_card_fail":
        return {'error': 'MSG:{} DETAILS:{}'.format(confirm_rsp.get('message'), confirm_rsp.get('details') )}
    #{"message":"add_new_card_success","return_url":"http://159.65.188.177:5000/","validation_type":"KYC"}
    if confirm_rsp.get('validation_type') == 'KYC':
        qa_url = 'https://vpos.infonet.com.py:8888/checkout/register_card/kyc/question'
        qa_rspt = bcs.get(qa_url, params={'process_id': check_rsp.get('process_id') })
        qa_rsp = qa_rspt.json()
        qa_payload = {'process_id': check_rsp.get('process_id')}
        answer = qa.get(qa_rsp.get('question').get('text'))
        if not answer:
            return {'error': 'MSG: La pregunta no se encuentra DETAILS: {}'.format(qa_rspt)}
        #{"question":{"text":"¿Dónde recibís tu extracto de algunas de tus tarjetas de crédito?",
        # "type":"SELECTION","options":["HUMAITA 145 - EDIF.PLANETA - P3","AV.EUSEBIO AYALA 3755","BRASILIA 765 C/ SIRIA"]}}
        strike = 0
        rsk = {"kyc_status":"OK"}
        while rsk.get('kyc_status') == 'OK':
            if answer:
                if isinstance(answer, list):
                    #{u'question': {u'options': [u'COOP. LAMBARE - CREDICARD - 5856',
                    #                            u'MEDALLA - MASTERCAD - 5789',
                    #                            u'BNF - VISA - 7789'],
                    # u'text': u'\xbfAlguna de tus tarjetas de d\xe9bito termina con estos n\xfameros?',
                    # u'type': u'SELECTION'}}
                    for option in qa_rsp.get('question').get('options'):
                        for ans in answer:
                            if ans.lower() == option.lower():
                                answer = ans
                                break
                send_aw = 'https://vpos.infonet.com.py:8888/checkout/register_card/kyc/answer'
                send_rsp = bcs.post(send_aw, params={'answer': answer, 
                                                     'process_id': check_rsp.get('process_id'),
                                                     "return_url": "http://159.65.188.177:5000/"
                })
                print(send_rsp.text)
                send_rsp = send_rsp.json()
                if send_rsp.get('kyc_status') == 'GRANTED':
                    return {'exitos': 'MSG: Tarjeta guardada con exitos'}
                if strike >= 8:
                    return {'error': 'MSG: Numeros de intentos superados'}
                #If {"kyc_status":"GRANTED"} then your done
                """ answer: BRASILIA 765 C/ SIRIA
                process_id: mbum2IbW8j-0q2dWWn63
                return_url: https://comercios.bancard.com.py/services/vpos/test_case_new_card/result """
                #POST

def delete_card(*args, **kwargs):
    card_id = kwargs.get('card_id')
    user_id = kwargs.get('user_id')
    number_card = int(kwargs.get('number_card'))
    data, url = generate_token(private_key, card_id, user_id, 'request_user_cards', public_key, '', '')
    resp = bcs.post(url, json=data, headers=HEADERS)
    if resp.json().get('status') == 'success':
        if not resp.json().get('cards'): return {'exitos': 'MSG: No existen tarjetas para borrar'}
        alias_token = resp.json().get('cards')[number_card].get('alias_token')
        print resp.json()
        ll = [private_key, 'delete_card', user_id, alias_token]
        print ll
        djson =  {
            "public_key": public_key,
            "operation": {
                "token": md5.md5(''.join(map(str, ll))).hexdigest(),
                "alias_token": alias_token,
                'card_number': card_id,
                'commission_info': False,
                'ci': user_id,                
            },
            "test_client": True
        }
        print(djson)
        url = 'https://{}/vpos/api/0.3/users/{}/cards'.format(main_url, user_id)
        print url
        resp = bcs.delete(url, json=djson, headers=HEADERS)
        print(resp.text)
delete_card(card_id=8601010000000013,user_id=9661000, number_card=0)

def generate_token(private_key, card_id, user_id, metodo, public_key, telefono, correo, card_token=None):
    if metodo == 'delete_card':
        ll = [private_key, metodo, user_id]

        djson =  {
            "public_key": public_key,
            "operation": {
                "token": md5.md5(''.join(map(str, ll))).hexdigest(),
                "alias_token": card_token
            },
            "test_client": True
        }
        url = 'https://{}/vpos/api/0.3/users/{}/cards'.format(main_url, user_id)
    
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


if __name__ == '__main__':
    data, url = generate_token(private_key, card_id, user_id, 'request_new_card', public_key, telefono, correo)
    resp = requests.post(url, json=data, headers=HEADERS)
    respc = resp.json()
    print respc
    """ if respc and respc.get('status') == 'success':
        fname = '/var/www/html/bancard/iframe_bancard_{}.html'.format(card_id)
        with open(fname, 'w') as iff:
            iff.write(iframeb.format(respc.get('process_id')))
        cmd = '/usr/bin/google-chrome {}'.format(fname)
        print cmd
        subprocess.Popen(cmd, shell=True)
        
    data, url = generate_token(private_key, card_id, user_id, 'request_user_cards', public_key, telefono, correo)
    resp = requests.post(url, json=data, headers=HEADERS)
    print resp.text, 'LISTANDO'
    data, url = generate_token(private_key, card_id, user_id, 'delete_card', public_key, telefono, correo,
                            resp.json().get('cards')[0].get('alias_token')
    )
    resp = requests.post(url, json=data, headers=HEADERS)
    print resp.text, 'DELETE'     """



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
# Nombre:
# MasterCard
# Numero:
# Vencimiento: 8/21
# Codigo de seguridad:
# 258
# url = 'https://vpos.service.sandbox:4485/vpos/api/0.3/cards/new'
# public_key = '3msJMmy2WkKaxLc54zN8reEi9LEYvgVT'
# private_key = 'DhcwTEUNHpQtOsJ9p,zHNGoRSbrOWlEd0zRCB,eZ'
#user_id = '4675564'