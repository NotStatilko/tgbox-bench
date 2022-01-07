#!/usr/bin/env python3
#github.com/NotStatilko/tgbox-bench

def progress_callback(current: int, total: int) -> None:
    percent = str(round(current/total*100,2))
    cur_time = strftime('%H:%M:%S')

    if len(percent.split('.')[-1]) == 1: percent += '0'
    print(f'@ Prepare and upload file / {percent}% / {cur_time}\r', end='')

try:
    print('\n! Please DO NOT open any programs during test.')
    print('\n@ Loading benchmark modules...')
    
    import psutil
    
    if psutil.virtual_memory().available < 1.6e+9:
        print(
            '''\nE: You don\'t have enough RAM to run this benchmark,\n'''
            '''   the minimum is 1.6GB, please close some programs. Thanks.'''
        )
        input('\n@ Press Ctrl+C to exit ')

    import tgbox
    
    from io import BytesIO
    from tgbox import sync
    from os import urandom

    from getpass import getpass
    from time import time, strftime
    from speedtest import Speedtest

    from platform import (
        processor, python_version
    )
    print('@ Receiving actual net speed with SpeedTest...')

    s = Speedtest()
    s.get_servers()
    s.get_best_server()
    s.download()
    s.upload()
    s.results.share()
    st_results = s.results.dict()

    ping = st_results['ping']
    upload = round(st_results['upload'] / 1e+6, 1)
    download = round(st_results['download'] / 1e+6, 1) 

    print(
        '''\n@ OK! Now we\'re need to log-in into your\n'''
        '''  Telegram account to make TGBOX and upload 1GB file.'''
    ) 
    tg_phone = input('\n> Phone number: ')

    ta = tgbox.api.TelegramAccount(phone_number=tg_phone)
    sync(ta.connect()) # Connecting to Telegram servers

    sync(ta.send_code_request()) # Sending log-in code request
    tg_code = input('>> Received code: ')

    print('\n! If you don\'t set password, then just press Enter')
    tg_password = getpass('>>> Password (hidden input): ')

    print('\n@ Trying to log-in...') # Trying to logging-in
    sync(ta.sign_in(password=tg_password, code=tg_code))
    
    print('@ Successful! Making TGBOX...') 
    
    # Make random BaseKey for one session
    basekey = tgbox.keys.BaseKey(urandom(32))
    tgbox_name = 'benchTGBOX_' + str(int(time()))

    erb = sync(tgbox.api.make_remote_box(ta, tgbox_name))
    dlb = sync(tgbox.api.make_local_box(erb, ta, basekey))
    drb = sync(erb.decrypt(dlb=dlb))
    
    print('@ Allocating 1GB in RAM...')
    pseudo_file = BytesIO()

    for _ in range(10):
        pseudo_file.write(bytearray(100000000))
    
    print('@ Prepare and upload file...\r', end='')
    
    start_time = time()

    ff = sync(dlb.make_file(pseudo_file))
    rbf = sync(drb.push_file(ff, progress_callback))
    
    total_time = time() - start_time
    del pseudo_file

    print('\n\nGood! Logging out...')
    sync(ta.log_out())
    
    tgbox_upload = round(((1e+9 / total_time) * 8) / 1024**2, 1)
    cpu = processor() if processor() else 'UNKNOWN'

    print(
        '\n'*100 + '''-- RESULTS ----------------------------------\n'''

        f'''\n # SpeedTest Ping: {ping}'''
        f'''\n # SpeedTest Upload speed: {upload}Mbps'''
        f'''\n # SpeedTest Download speed: {download}Mbps\n'''
        
        f'''\n # TGBOX Upload speed: {tgbox_upload}Mbps'''
        f'''\n # TGBOX Version: {tgbox.constants.VERSION}\n'''
        

        f'''\n # PYTHON_VER:      {python_version()}'''
        f'''\n # SYSTEM_CPU:      {cpu}'''
        f'''\n # FAST_TELETHON:   {tgbox.crypto.FAST_TELETHON}'''
        f'''\n # FAST_ENCRYPTION: {tgbox.crypto.FAST_ENCRYPTION}'''
        f'''\n # FAST_EVENT_LOOP: {tgbox.FAST_EVENT_LOOP}\n\n'''

        '''---------------------------------------------\n\n'''

        '''@ Thank you very much for testing this!\n'''
        '''  Please, make a screenshot and send it to the author.\n'''
        '''  Email: thenonproton@pm.me, Telegram: @not_statilko\n'''

        '''\n! You can leave now RemoteBox Channel from your\n'''
        '''  Telegram account and remove LocalBox file (benchTGBOX).'''
    )
    input('\n@ Press Ctrl+C to exit ')

except Exception as e:
    print(f'E: Oops! Error founded. {e}')
    input('\n@ Press Ctrl+C to exit ')
