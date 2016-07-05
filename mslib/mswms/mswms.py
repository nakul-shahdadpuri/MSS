#!/usr/bin/env python


import paste.httpserver
import argparse
import logging
from wms import mss_wms_settings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="hostname",
                        default="127.0.0.1", dest="host")
    parser.add_argument("--port", help="port", dest="port", default="8081")
    parser.add_argument("--threadpool", help="threadpool", dest="use_threadpool", action="store_true", default=False)
    parser.add_argument("--logfile", help="if set to a name log output goes to that file", dest="logfile",
                        default=None)
    args = parser.parse_args()

    if args.logfile is not None:
        # Log everything to "logfile".
        # TODO: Change this to write to a rotating log handler (so that the file size
        #  is kept constant). (mr, 2011-02-25)
        logging.basicConfig(filename=args.logfile,
                            level=logging.DEBUG,
                            format="%(asctime)s %(funcName)19s || %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")
    else:
        # Log everything, and send it to stderr.
        # See http://docs.python.org/library/logging.html for more information
        # on the Python logging module.
        logging.basicConfig(level=logging.DEBUG,
                            # format="%(levelname)s %(asctime)s %(funcName)19s || %(message)s",
                            format="%(asctime)s %(funcName)19s || %(message)s",
                            datefmt="%Y-%m-%d %H:%M:%S")

    from mslib.mswms.wms import application
    if mss_wms_settings.enable_basic_http_authentication:
        logging.debug("Enabling basic HTTP authentication. Username and "
                      "password required to access the service.")

        from paste.auth.basic import AuthBasicHandler
        import hashlib

        realm = 'Mission Support Web Map Service'

        def authfunc(environ, username, password):
            for u, p in mss_wms_settings.allowed_users:
                if (u == username) and (p == hashlib.md5(password).hexdigest()):
                    return True
            return False

        application = AuthBasicHandler(application, realm, authfunc)

    paste.httpserver.serve(application, host=args.host, port=args.port, use_threadpool=args.use_threadpool)

if __name__ == '__main__':
    main()