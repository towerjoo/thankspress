from app import app
from flask import render_template

@app.route('/public-pages')
@app.route('/public-pages/')
@app.route('/public-pages/discover')
@app.route('/public-pages/discover/')
def public_page_most_thanks_received():
    return render_template('public_page/public_pages_discover.html',
        title = 'Public Page',
        message = 'Public page')

@app.route('/public-pages/<int:public_page_id>')
@app.route('/public-pages/<int:public_page_id>/')
def public_page(public_page_id = None):
    if public_page_id != None:
        return render_template('public_page/public_pages_timeline.html', 
            title = 'Public Page')
    return render_template('404.html'), 404