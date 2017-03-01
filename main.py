"""
Details the various flask endpoints for processing and retrieving
command details as well as a swagger spec endpoint
"""

from multiprocessing import Process, Queue
import sys, os
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_swagger import swagger
from werkzeug import utils
from db import session, engine
from base import Base, Command
from command_parser import get_valid_commands, process_command_output

app = Flask(__name__)

def queryToDict(model):
    """ Converts Base model to dict """
    return {c.name: getattr(model, c.name) for c in model.__table__.columns}


@app.route('/commands', methods=['GET'])
def get_command_output():
    """
    Returns as json the command details that have been processed
    ---
    tags: [commands]
    responses:
      200:
        description: Commands returned OK
      400:
        description: Commands not found
    """
    # if request.method=='GET':
        # return 'Command Outputs shall be displayed here'
        # return render_template('cmd_parse_get')
        # return redirect(url_for('make_db'))

    items = session.query(Command)

    if items :
        dbQuery = [queryToDict(i) for i in items]

        print("**************************************** DB output starts here ********************************")

        for i in dbQuery:
            print i

        print("**************************************** DB output ends here ********************************")

    return render_template('cmd_parse_get.html')
    # return jsonify(commands)



@app.route('/commands', methods=['POST'])
def process_commands():
    """
    Processes commmands from a command list
    ---
    tags: [commands]S
    parameters:
      - name: filename
        in: formData
        description: filename of the commands text file to parse
        required: true
        type: string
    responses:
      200:
        description: Processing OK
    """

    fi = request.args.get('file')
    nxt = request.form['check']

    if nxt == "yes":
        return redirect(url_for('make_db'))
    elif nxt == "no":
        return redirect(url_for('drop_db'))
    else:
        queue = Queue()
        get_valid_commands(queue, fi)
        processes = [Process(target=process_command_output, args=(queue,))
                     for num in range(2)]
        for process in processes:
            process.start()
        for process in processes:
            process.join()

        return 'Successfully processed commands.'


@app.route('/database', methods=['POST', 'GET'])
def make_db():
    """
    Creates database schema
    ---
    tags: [db]
    responses:
      200:
        description: DB Creation OK
    """
    Base.metadata.create_all(engine)
    return 'Database creation successful.'


@app.route('/drop', methods=['POST', 'GET'])
def drop_db():
    """
    Drops all db tables
    ---
    tags: [db]
    responses:
      200:
        description: DB table drop OK
    """
    Base.metadata.drop_all(engine)
    return 'Database deletion successful.'

@app.route('/', methods=['GET','POST'])
def index():

    if request.method == 'GET':
        return render_template('index.html')

    elif request.method == 'POST':

        if 'file' in request.files:
            f = request.files['file']
            f.save(utils.secure_filename(f.filename))
            # session['file'] = f.filename
            # request.args['file'] = f.filename
            session.__setattr__('file',f.filename)
            request.__setattr__('file',f.filename)
            return render_template('view_parse.html')
        else:
            # return app.route('/commands',methods=['GET'])
            # return 'Here'
            # return redirect(url_for('get_command_output'))
            return redirect(url_for('process_commands'))

    else:
        return app.route('/spec')


@app.route('/spec')
def swagger_spec():
    """
    Display the swagger formatted JSON API specification.
    ---
    tags: [docs]
    responses:
      200:
        description: OK status
    """
    spec = swagger(app)
    spec['info']['title'] = "Nervana cloud challenge API"
    spec['info']['description'] = ("Nervana's cloud challenge " +
                                   "for interns and full-time hires")
    spec['info']['license'] = {
        "name": "Nervana Proprietary License",
        "url": "http://www.nervanasys.com",
    }
    spec['info']['contact'] = {
        "name": "Nervana Systems",
        "url": "http://www.nervanasys.com",
        "email": "info@nervanasys.com",
    }
    spec['schemes'] = ['http']
    spec['tags'] = [
        {"name": "db", "description": "database actions (create, delete)"},
        {"name": "commands", "description": "process and retrieve commands"}
    ]
    return jsonify(spec)

if __name__ == '__main__':
    """
    Starts up the flask server
    """
    port = 8070
    use_reloader = True

    # provides some configurable options
    for arg in sys.argv[1:]:
        if '--port' in arg:
            port = int(arg.split('=')[1])
        elif '--use_reloader' in arg:
            use_reloader = arg.split('=')[1] == 'true'

    app.run(port=port, debug=True, use_reloader=use_reloader)



