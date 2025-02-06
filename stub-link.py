import os
import re
import time

from flask import Flask
from wikmd.config import WikmdConfig
from urllib.parse import quote_plus
from werkzeug.utils import safe_join


class Plugin:
    def __init__(self, flask_app: Flask, config: WikmdConfig, web_dep):
        self.name = "stub-link"
        self.plugname = "stub-link"
        self.flask_app = flask_app
        self.config = config
        self.this_location = os.path.dirname(__file__)
        self.web_dep = web_dep

    def get_plugin_name(self) -> str:
        """
        returns the name of the plugin
        """
        return self.name

    def process_md(self, md: str) -> str:
        """
        returns the md file after process the input file
        """
        return md

    def process_html(self, html: str) -> str:
        """
        returns the html file after process the input file
        """
        return self.search_for_page_implementation(html)

    def request_html(self, get_html_callback):
        self.get_html = get_html_callback

    def search_for_page_implementation(self, file: str) -> str:
        """
        search for [[ stub: some text ]] in "file" and turn it into a search term
        """
        # ?s to handle a term that may be broken up across multiple lines.
        stubs = re.findall(r"\[\[\s*stub:\s*((?s).*?)\s*\]\]", file)
        result = file
        for stub in stubs:
            # If the term spans multiple lines, swap out the newline with a space.
            normalized_stub = stub.replace('\n', ' ')
            # See if an article exists or not
            md_file_path = safe_join(self.config.wiki_directory, f"{normalized_stub}.md")
            is_article = False
            try:
                # TODO Is there a better indicator, like a real search or lookup API? Does Wikmd handle nested paths, and if so, how does this plugin handle them?
                mod = "Last modified: %s" % time.ctime(os.path.getmtime(md_file_path))
                is_article = True
            except:
                pass

            if is_article:
                integrate_html = f"<a href=\"{normalized_stub}\">{normalized_stub}</a>"
            else:
                integrate_html = f"<a style=\"color: orangered\" href=\"/search?q={quote_plus(normalized_stub)}\">{normalized_stub} [?]</a>"
            # integrate the page into this one.
            result = re.sub(r"\[\[\s*stub:\s*"+stub+r"\s*\]\]", integrate_html, result)

        return result

