from flask_script import Command, Option
from fiwareglancesync.app.settings.settings import WORKERS, PIDFILE, LOGLEVEL, PORT, HOST
from distutils.dir_util import mkpath
import sys
import os
from gunicorn import version_info
from gunicorn.app.base import Application
from fiwareglancesync.app.settings.settings import logger_api


class GunicornServer(Command):
    """
    Run the GlanceSync server application within Gunicorn.
    """

    def __init__(self, host=HOST, port=PORT, workers=WORKERS, **options):
        """
        Default constructor of the class.

        :param host: The host in which the gunicorn service will be up.
        :param port: The port of the gunicorn service.
        :param workers: The number of concurrent workers to be launched.
        :param options: Any other options to be taking into account like
                        -H, -p, -w.
        :return: Nothing.
        """
        self.port = port
        self.host = host
        self.workers = workers
        self.server_options = options

    def get_options(self):
        """
        Get the list of options defined in the execution of the application
        with the command 'gunicornservice'.

        :return: List of defined Options (-H, -p, -w).
        """
        return (
            Option('-H', '--host',
                   dest='host',
                   default=self.host,
                   help='IP address or hostname of the Glancesync server.'),

            Option('-p', '--port',
                   dest='port',
                   type=int,
                   default=self.port,
                   help='Port in which the GlanceSync server is running'),

            Option('-w', '--workers',
                   dest='workers',
                   type=int,
                   default=self.workers,
                   help='Number of concurrent workers to be launched, usually 2*core numbers+1.'),
        )

    def handle(self, app, host, port, workers):
        """
        Method to manage the creation of an GUnicorn Application.

        :param app: The app of the GlanceSync-API
        :param host: The host in which the gunicorn service will be up.
        :param port: The port of the gunicorn service.
        :param workers: The number of concurrent workers to be launched.
        :return: Nothing
        """
        bind = "%s:%s" % (host, str(port))

        workers = WORKERS
        pid_file = PIDFILE
        loglevel = LOGLEVEL

        # We have to be sure that the directory exist in order
        # to write there the pid file.
        mkpath(os.path.dirname(pid_file))

        if version_info < (0, 9, 0):
            raise RuntimeError("Unsupported gunicorn version! Required > 0.9.0")
        else:
            class FlaskApplication(Application):
                def init(self, parser, opts, args):
                    return {
                        'bind': bind,
                        'workers': workers,
                        'pidfile': pid_file,
                        'loglevel': loglevel,
                    }

                def load(self):
                    return app

            # Do not pass any cmdline options to gunicorn
            sys.argv = sys.argv[:2]

            logger_api.info("Logging to stderr with loglevel '%s'" % loglevel)
            logger_api.info("Starting gunicorn...")

            FlaskApplication().run()
