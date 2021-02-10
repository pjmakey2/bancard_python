import argparse

def opts(*args, **kwargs):
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-url', help='Url of the pos platform', nargs='?')
    parser.add_argument('-private_key',help='Private key giving by the bank', nargs='?')
    parser.add_argument('-public_key', help='Public key giving by the bank', nargs='?')
    parser.add_argument('-user_id', help='Usually the social number of the person who use the system', nargs='?')
    parser.add_argument('-card_id', help='The credit / debit card', nargs='?')
    parser.add_argument('-ccv', help='The passcode for the credit / debit card', nargs='?')
    parser.add_argument('-expire', help='When the credit / debit card expire', nargs='?')
    parser.add_argument('-mail', help='The mail of the owner of the card', nargs='?')
    parser.add_argument('-phone', help='The phone number of the owner of the card', nargs='?')
    parser.add_argument('-return_url', help='A listenner for the bank api respond', nargs='?')    
    parser.add_argument('-action', choices=['request_new_card', 'request_user_cards', 'delete_card'], nargs='?')
    parser.add_argument('-test_client', help='Pass this as 1 if you do not want the platforma validate your testing', nargs='?')    
    parser.add_argument('-settings', help='Read the configuration from a file, you have an example in settgins-inc.py', nargs='?')
    parser.add_argument('-settings_key', help='If the settings.py have encryption, you need to provide a key', nargs='?')
    parser.add_argument('-path_key', help='Path of the gpg key', nargs='?')
    return parser.parse_args()

if __name__ == '__main__':
    args = opts()
