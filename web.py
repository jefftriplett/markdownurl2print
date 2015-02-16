import markdown
import os
import redis
import requests
import requests_cache

from bs4 import BeautifulSoup
from flask import Flask, Markup, render_template, request
from flask_bootstrap import Bootstrap


app = Flask(__name__)
Bootstrap(app)


def find_title(soup):
    # Determine the page title from the first heading
    title = soup.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    if title:
        return title.string
    return None


@app.route('/')
def homepage():
    url = request.args.get('url')
    clear = request.args.get('clear', False)

    if clear:
        requests_cache.clear()

    if url:
        req = requests.get(url)
        content = req.text

        if content:
            content = markdown.markdown(content)
            soup = BeautifulSoup(content)
            title = find_title(soup)
            images = soup.find_all('img')
            for image in images:
                try:
                    css_class = image['class']
                except KeyError:
                    css_class = ''

                image['class'] = ' '.join([css_class, 'img-responsive']).strip()

            context = {
                'title': title,
                'content': Markup(soup),
            }
            return render_template('index.html', **context)

    return 'I should make a homepage. For now append ?url= to the page which contains markdown.'


if __name__ == '__main__':
    redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
    redis = redis.from_url(redis_url)
    requests_cache.install_cache('demo_cache', backend='redis', connection=redis, expire_after=1800)

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
