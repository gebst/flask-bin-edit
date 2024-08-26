from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory
import os
from fileManager import BinaryFile, WinOlsFile

app = Flask(__name__)
app.secret_key = '3d6f45a5fc12445dbac2f59c3b6c7cb1'

ALLOWED_EXTENSIONS = {'winolsskript', 'bin'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def hello_world():
    bins = os.listdir('./uploads/bin')
    return render_template('index.html', bins=bins)

@app.route("/upload_winols", methods=['GET', 'POST'])
def upload_winols():
    if request.method == 'POST':
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            flash('File saved')
            file.save(os.path.join('./uploads/winols', file.filename))
            return redirect(url_for('upload_winols'))
        else:
            flash('File not allowed')
            return redirect(request.url)
    
    return render_template('upload_winols.html')

@app.route("/upload_bin", methods=['GET', 'POST'])
def upload_bin():
    
    if request.method == 'POST':
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            flash('File saved')
            file.save(os.path.join('./uploads/bin', file.filename))
            return redirect('/show_tunes/' + file.filename)
        else:
            flash('File not allowed')
            return redirect(request.url)

    return render_template('upload_bin.html')

@app.route("/show_tunes/<bin_file>", methods=['GET'])
def show_tunes(bin_file, script_file=None):
    matches = []
    if(bin_file):
        bin_name = bin_file
        bin_file = BinaryFile(os.path.join('./uploads/bin', bin_file))
        for script in os.listdir('./uploads/winols'):
            winols_file = WinOlsFile(os.path.join('./uploads/winols', script))
            match = bin_file.compare_winols_file(winols_file)
            matches.append({'file': script, 'match': match})
    
    matches.sort(key=lambda x: x['match'], reverse=True)
    return render_template('show_tunes.html', matches=matches, bin_name=bin_name)

@app.route("/apply_tune/<bin_file>/<script_file>", methods=['GET'])
def apply_tune(bin_file, script_file):
    original_file_name = bin_file
    bin_file = BinaryFile(os.path.join('./uploads/bin', bin_file))
    winols_file = WinOlsFile(os.path.join('./uploads/winols', script_file))
    bin_file.apply_winols_file(winols_file)
    bin_file.save_file(os.path.join('./uploads/tuned', original_file_name ))
    return redirect('/download_tuned/'+original_file_name)

@app.route("/download_tuned/<file>", methods=['GET'])
def download_tuned(file):
    return send_from_directory(os.path.join('./uploads/tuned'), file)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)