#coding: utf-8
import argparse
import requests
import urllib
import md5
import subprocess
import random
import socket
import struct

HEADERS = {
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
    'Content-Type': 'application/json',
     'Status Code': 200,
     'Remote Address': socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff))),
     'Referrer Policy': 'origin',
}

bcs = requests.Session()


def request_user_cards(**kwargs):
    url = kwargs.get('url')
    metodo = kwargs.get('metodo')
    private_key = kwargs.get('private_key')
    public_key = kwargs.get('public_key')
    version = kwargs.get('version')    
    user_id = kwargs.get('user_id')
    test_client = kwargs.get('test_client')
    ll = [private_key, user_id, metodo]        
    djson =  {
        "public_key": public_key,
        "operation": {
            "token": md5.md5(''.join(map(str, ll))).hexdigest(),
        },
        "test_client": test_client
    }
    url = 'https://{}/vpos/api/{}/users/{}/cards'.format(url, version, user_id)
    return (djson, url)

def request_new_card(**kwargs):
    url = kwargs.get('url')
    metodo = kwargs.get('metodo')
    private_key = kwargs.get('private_key')
    public_key = kwargs.get('public_key')
    version = kwargs.get('version')    
    user_id = kwargs.get('user_id')
    card_id = kwargs.get('card_id')    
    phone = kwargs.get('phone')
    mail = kwargs.get('mail')
    test_client = kwargs.get('test_client')    
    return_url = kwargs.get('return_url')
    ll = [private_key, card_id, user_id, metodo]
    djson = {
        "public_key": public_key,
        "operation": {
            "token": md5.md5(''.join(map(str, ll))).hexdigest(),
            "card_id": card_id,
            "user_id": user_id,
            "user_cell_phone": phone,
            "user_mail": mail,
            "return_url": return_url
        },
        "test_client": test_client
    }
    url = 'https://{}/vpos/api/{}/cards/new'.format(url, version)
    return (djson, url)

def create_new_car(**kwargs):
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
    test_client = kwargs.get('test_client')
    main_url = kwargs.get('url')
    return_url = kwargs.get('return_url')
    data, url = request_new_card(**kwargs)
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
        'is_test_client': test_client
    }
    confirm_url = 'https://{}/checkout/register_card'.format(main_url)
    send_aw = 'https://{}/checkout/register_card/kyc/answer'.format(main_url)
    qa_url = 'https://{}/checkout/register_card/kyc/question'.format(main_url)

    confirm_rsp = bcs.post(confirm_url, params=confirm_payload, headers=HEADERS)
    if confirm_rsp.get('message')  == "add_new_card_fail":
        return {'error': 'MSG:{} DETAILS:{}'.format(confirm_rsp.get('message'), confirm_rsp.get('details') )}
    if confirm_rsp.get('validation_type') == 'KYC':
        qa_rspt = bcs.get(qa_url, params={'process_id': check_rsp.get('process_id') })
        qa_rsp = qa_rspt.json()
        answer = qa.get(qa_rsp.get('question').get('text'))
        if not answer:
            return {'error': 'MSG: La pregunta no se encuentra DETAILS: {}'.format(qa_rspt)}
        strike = 0
        rsk = {"kyc_status":"OK"}
        while rsk.get('kyc_status') == 'OK':
            if answer:
                if isinstance(answer, list):
                    for option in qa_rsp.get('question').get('options'):
                        for ans in answer:
                            if ans.lower() == option.lower():
                                answer = ans
                                break
                send_rsp = bcs.post(send_aw, params={'answer': answer, 
                                                     'process_id': check_rsp.get('process_id'),
                                                     "return_url": return_url
                })
                send_rsp = send_rsp.json()
                if send_rsp.get('kyc_status') == 'GRANTED':
                    return {'exitos': 'MSG: Tarjeta guardada con exitos'}
                if strike >= 8:
                    return {'error': 'MSG: Numeros de intentos superados'}

def delete_card(*args, **kwargs):
    card_id = kwargs.get('card_id')
    user_id = kwargs.get('user_id')
    private_key = kwargs.get('private_key')
    public_key = kwargs.get('public_key')
    version = kwargs.get('version')
    number_card = int(kwargs.get('number_card'))
    main_url = kwargs.get('url')
    data, url = request_user_cards(**kwargs)
    resp = bcs.post(url, json=data, headers=HEADERS)
    if resp.json().get('status') == 'success':
        if not resp.json().get('cards'): return {'exitos': 'MSG: No existen tarjetas para borrar'}
        #Todo:
        #Ask the user wich card want's to deleted
        alias_token = resp.json().get('cards')[number_card].get('alias_token')
        ll = [private_key, 'delete_card', user_id, alias_token]
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
        url = 'https://{}/vpos/api/{}/users/{}/cards'.format(main_url,version, user_id)
        resp = bcs.delete(url, json=djson, headers=HEADERS)
        if resp.get('status')  == 'success':
            return {'error': 'MSG:{} Tarjeta {} borrada'.format(card_id)}
    return {'success': 'MSG: No se llevo a cabo ninguna accion'}
