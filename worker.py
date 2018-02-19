from celery import Celery
from tempfile import mkstemp
from subprocess import call
import requests
import os
import json

CELERY_BROKER_URL = 'amqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'mongodb://localhost:27017'

celery = Celery('worker', 
    backend=CELERY_RESULT_BACKEND, 
    broker=CELERY_BROKER_URL
)

@celery.task
def cutting_for_test_on_linux(params):
    result = {
        'parts': [
            {'stock': 0, 'rotated': True, 'x': 150.0, 'y': 0.0, 'h': 200.0, 'index': 0, 'w': 300.0}, 
            {'stock': 0, 'rotated': False, 'x': 0.0, 'y': 0.0, 'h': 400.0, 'index': 1, 'w': 150.0}, 
            {'stock': 0, 'rotated': True, 'x': 150.0, 'y': 300.0, 'h': 200.0, 'index': 2, 'w': 100.0}, 
            {'stock': 0, 'rotated': False, 'x': 350.0, 'y': 0.0, 'h': 320.0, 'index': 3, 'w': 130.0}
        ], 
        'cuts': [
            {'index': 0, 'y1': 400.0, 'stock': 0, 'x0': 0.0, 'y0': 400.0, 'x1': 600.0}, 
            {'index': 1, 'y1': 400.0, 'stock': 0, 'x0': 150.0, 'y0': 0.0, 'x1': 150.0}, 
            {'index': 2, 'y1': 400.0, 'stock': 0, 'x0': 350.0, 'y0': 0.0, 'x1': 350.0}, 
            {'index': 3, 'y1': 400.0, 'stock': 0, 'x0': 480.0, 'y0': 0.0, 'x1': 480.0}, 
            {'index': 4, 'y1': 300.0, 'stock': 0, 'x0': 150.0, 'y0': 300.0, 'x1': 350.0}, 
            {'index': 5, 'y1': 320.0, 'stock': 0, 'x0': 350.0, 'y0': 320.0, 'x1': 480.0}
        ], 
        'params': {
            'W': 600, 'H': 850,
            'parts': [
                {'h': 200, 'id': 'Part1', 'q': 1, 'w': 300, 'r': True}, 
                {'h': 400, 'id': 'Part2', 'q': 1, 'w': 150, 'r': False}, 
                {'h': 200, 'id': 'Part3', 'q': 1, 'w': 100, 'r': True}, 
                {'h': 320, 'id': 'Part4', 'q': 1, 'w': 130, 'r': True}
            ]
        }
    }
    return result

@celery.task
def cutting_from_cutglib(params):
    """
    Task que recebe um dicionario @params escreve num arquivo 
    e chama a execução do script em ironpython para fazer a 
    otimização de corte.
    """
    # cria os arquivos temporarios com nomes únicos de entrada e saída
    fparams, fname = mkstemp(suffix='.json', text=True)
    fdout, fout = mkstemp(suffix='.json', text=True)
    os.close(fparams)
    os.close(fdout)
    
    open(fname, 'w').write(json.dumps(params))

    call('ipy64 cutting.py {} {}'.format(fname, fout))

    data = json.loads(open(fout).read())
    
    os.remove(fout)
    os.remove(fname)

    return data
