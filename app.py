from flask import Flask
from flask import flash
from flask import render_template
from flask import request
from flask import jsonify
# if the worker is running on windows use the 
# import below to use the cutglib
#from worker import cutting_from_cutglib as task_cutting

#if it is to test the worker in linux use the 
#import below to use a preprocessed optimization.
from worker import cutting_for_test_on_linux as task_cutting

from cerberus import Validator
import yaml

app = Flask('pycut')
app.debug = True    

schema_data_input_yaml = """
W: 
    type: integer
    required: True
H: 
    type: integer
    required: True
parts:
    type: list
    required: True
    schema: 
        type: dict
        schema: 
            w: 
                type: integer
                required: True
            h: 
                type: integer
                required: True
            q: 
                type: integer
                default: 1
            r: 
                type: boolean
                default: True
            id:
                type: string
                required: True
"""
validator_input = Validator(yaml.load(schema_data_input_yaml))


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/run', methods=['POST'])
def run():
    try:
        data = yaml.load(request.data)
        if not data or not validator_input.validate(data):
            raise Exception("Formato de dados de entrada inválido")
        
        data = validator_input.normalized(data)
        task = task_cutting.apply_async([data])
    
    except Exception as err:
        return jsonify({'status': 'ERROR', 'error': str(err)})

    else:
        return jsonify({'task_id': task.id })



@app.route('/status/<task_id>')
def status(task_id):
    task = task_cutting.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
        }
    else:
        response = {
            'state': task.state,
            'result': task.info,
        }
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8080, debug=True, threaded=True)    