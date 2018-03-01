import os
import argparse
import sys
import yaml
from jinja2 import Environment, FileSystemLoader
from CommonMark import commonmark
from tornado import httpserver, ioloop, web
from homeworkupload.validator import LTILaunchValidator, LTILaunchValidationError


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

    def post(self, hw):
        # FIXME: Run a process that cleans up old nonces every other minute
        consumers = self.settings['consumers']
        validator = LTILaunchValidator(consumers)

        args = {}
        for k, values in self.request.body_arguments.items():
            # Convert everything to strings rather than bytes
            args[k] = values[0].decode() if len(values) == 1 else [v.decode() for v in values]


        try:
            if validator.validate_launch_request(
                    self.request.full_url(),
                    self.request.headers,
                    args
            ):
                user_id = self.get_body_argument('user_id')
        except LTILaunchValidationError as e:
            raise web.HTTPError(401, e.message)

        homework_definitions = self.settings['homework_definitions']
        if hw not in homework_definitions:
            raise web.HTTPError(404)

        self.render_template('main.html', homework=homework_definitions[hw])

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument(
        'homework_definitions',
        help='Path to YAML file containing homework definitions'
    )

    args = argparser.parse_args()

    if 'COOKIE_SECRET' not in os.environ:
        print('Set a 32byte hex-encoded value as COOKIE_SECRET environment variable first!')
        sys.exit(1)

    if 'LTI_PASSPORT' not in os.environ:
        print('Set an EdX formatted LTI Passport as LTI_PASSPORT environment variable first!')
        sys.exit(1)

    passport_split = os.environ['LTI_PASSPORT'].split(':')
    consumers = {passport_split[1]: passport_split[2]}
    with open(args.homework_definitions) as f:
        homework_definitions = yaml.safe_load(f)

    jinja2_env = Environment(loader=FileSystemLoader([
        os.path.join(os.path.dirname(__file__), 'templates')
    ]), autoescape=True)

    settings = {
        'jinja2_env': jinja2_env,
        'homework_definitions': homework_definitions,
        'static_path': os.path.join(os.path.dirname(__file__), "static"),
        'cookie_secret': os.environ['COOKIE_SECRET'],
        'consumers': consumers
    }

    application = web.Application([
        (r"/(\w+)", HomeWorkHandler),
    ], **settings)

    http_server = httpserver.HTTPServer(application)
    http_server.listen(9595)
    ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()