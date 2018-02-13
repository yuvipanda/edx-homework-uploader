import os
import argparse
import yaml
from jinja2 import Environment, FileSystemLoader
from CommonMark import commonmark
from tornado import httpserver, ioloop, web

class HomeWorkHandler(web.RequestHandler):
    def render_template(self, name, **extra_ns):
        """Render an HTML page"""
        ns = {
            'static_url': self.static_url,
            'commonmark': commonmark
        }
        ns.update(extra_ns)
        template = self.settings['jinja2_env'].get_template(name)
        html = template.render(**ns)
        self.write(html)

    def get(self, hw):
        homework_definitions = self.settings['homework_definitions']
        if hw not in homework_definitions:
            raise web.HTTPError(404)

        homework = homework_definitions[hw]
        self.render_template('main.html', homework=homework)


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'homework_definitions',
        help='Path to YAML file containing homework definitions'
    )

    args = argparser.parse_args()

    with open(args.homework_definitions) as f:
        homework_definitions = yaml.safe_load(f)

    jinja2_env = Environment(loader=FileSystemLoader([
        os.path.join(os.path.dirname(__file__), 'templates')
    ]), autoescape=True)

    settings = {
        'jinja2_env': jinja2_env,
        'homework_definitions': homework_definitions,
        'static_path': os.path.join(os.path.dirname(__file__), "static"),
    }

    application = web.Application([
        (r"/(\w+)", HomeWorkHandler),
    ], **settings)

    http_server = httpserver.HTTPServer(application)
    http_server.listen(9595)
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()