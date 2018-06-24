import http.server
import re

import pdoc.doc
import pdoc.render
import pdoc.extract


class DocHandler(http.server.BaseHTTPRequestHandler):
    def render(self) -> str:
        if self.path == "/":
            out = pdoc.render.html_index(self.server.roots, self.server.args.link_prefix)
        elif self.path == "/favicon.ico":
            self.send_response(404)
            return None
        else:
            out = self.html()
            if out is None:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                err = "Module <code>%s</code> not found." % self.import_path
                return err
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        return out

    def do_HEAD(self):
        self.render()
        if not out:

        if self.path != "/":
            out = self.html()
            if out is None:
                self.send_response(404)
                self.end_headers()
                return

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        if self.path == "/":
            out = pdoc.render.html_index(self.server.roots, self.server.args.link_prefix)
        elif self.path == "/favicon.ico":
            return None
        else:
            out = self.html()
            if out is None:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                err = "Module <code>%s</code> not found." % self.import_path
                self.wfile.write(err.encode("utf-8"))
                return

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(out.encode("utf-8"))

    def html(self):
        """
        Retrieves and sends the HTML belonging to the path given in
        URL. This method is smart and will look for HTML files already
        generated and account for whether they are stale compared to
        the source code.
        """
        # Deny favico shortcut early.
        if self.path == "/favicon.ico":
            return None
        return pdoc.render.html_module(pdoc.extract.extract_module(self.import_path))

    @property
    def import_path(self):
        pieces = self.clean_path.split("/")
        if pieces[-1].startswith(pdoc.render.html_package_name):
            pieces = pieces[:-1]
        if pieces[-1].endswith(pdoc.render.html_module_suffix):
            pieces[-1] = pieces[-1][: -len(pdoc.render.html_module_suffix)]
        return ".".join(pieces)

    @property
    def clean_path(self):
        new, _ = re.subn("//+", "/", self.path)
        if "#" in new:
            new = new[0 : new.index("#")]
        return new.strip("/")

    def address_string(self):
        return "%s:%s" % (self.client_address[0], self.client_address[1])


class DocServer(http.server.HTTPServer):
    def __init__(self, addr, args, roots):
        self.args = args
        self.roots = roots
        super().__init__(addr, DocHandler)
