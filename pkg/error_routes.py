from flask import render_template
from pkg import app,db



"""creating error handling pages"""
@app.errorhandler(404)
def mypagenotfounderror(error):
    return render_template('error/404error.html', error=error), 404

@app.errorhandler(503)
def maintainance(error):
    return render_template('error/503error.html', error=error), 503

@app.errorhandler(500)
def internalservererror(error):
    return render_template('error/500error.html', error=error), 500
