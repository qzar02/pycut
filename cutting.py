import clr    
import sys
import json
curdir = os.path.dirname(os.path.abspath(__file__))
ReferenceToFileAndPath(os.path.join(curdir, "CutGLib.dll"))
from CutGLib import CutEngine 

def readfile():
    """
    Método que usa o arquivo da linha de comando e o lê como um json
    """
    try:
        file_input = os.path.join( os.getcwd(), sys.argv[1] )
        return json.loads(open(file_input).read())
    except:
        raise Exception("Falha ao abrir e carregar o arquivo JSON de entrada.")

def writefile(data):
    """
    Método que recebe o @data e escreve um json num arquivo 
    """
    try:
        file_output = os.path.join( os.getcwd(), sys.argv[2] )
        open(file_output, 'w').write( json.dumps(data) )
    except:
        raise Exception("Falha ao abrir e escrever o arquivo JSON de saída.")

def cutting(params):
    """
    Método principal para executar otimização de recorte.
    Recebe um dicionário @params contendo os dados do painel 
    e dimensões dos recortes. 
    Retorna um dicionário com os recortes otimizados  
    """
    calculator = CutEngine()

    calculator.AddStock(float(params['W']), float(params['H']), 100)

    for part in params['items']:
        calculator.AddPart(
            float(part['w']), 
            float(part['h']) , 
            part['q'], 
            part['r']
        )    
    result = calculator.Execute()

    if result:
        raise Exception("Falha ao executar otimização. {}".format(result))
    else:
        data = {'cuts': [], 'parts': []}
        
        for icut in range(calculator.GetCutsCount()):
            p = calculator.GetCut(icut)
            if p[0]:
                data['cuts'].append({
                    'stock': p[1],
                    'x0': p[2],
                    'y0': p[3],
                    'x1': p[4],
                    'y1': p[5],
                    'index': icut
                })

        for ipart in range(calculator.PartCount):
            p = calculator.GetResultPart(ipart)
            if p[0]:
                data['parts'].append({
                    'stock': p[1],
                    'w': p[2],
                    'h': p[3],
                    'x': p[4],
                    'y': p[5],
                    'rotated': p[6],
                    'index': ipart
                })
    return data

def run():
    if len(sys.argv)!=2:
        raise Exception("Uso: ipy cutting.py [arquivo_entrada.json] [arquivo_saida.json]")
    
    params = readfile()
    
    data = cutting( params )
    
    writefile( data )


if __name__ == '__main__':
    run()    

