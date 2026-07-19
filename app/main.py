"""Small Flask application used as a target for security scanners.

The SQL injection and reflected XSS are deliberate learning fixtures. They are
marked with LAB-VULNERABILITY comments so nobody mistakes them for production
code.
"""

import sqlite3

from flask import Flask, jsonify, request
from markupsafe import Markup


PRODUCTS = (
    (1, "Keyboard", 75),
    (2, "Mouse", 35),
    (3, "Monitor", 240),
)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/")
    def index():
        # HTML links give a DAST spider an explicit, reproducible attack surface.
        # Without links or an API specification, a scanner may never discover
        # query parameters such as q and name.
        return """
        <h1>Security Pipeline Lab</h1>
        <p>Intentionally vulnerable. Local training use only.</p>
        <ul>
          <li><a href="/health">Health check</a></li>
          <li><a href="/search?q=demo">Search demo</a></li>
          <li><a href="/products?name=Keyboard">Product demo</a></li>
        </ul>
        """

    @app.get("/health")
    def health():
        return jsonify(status="ok")

    @app.get("/search")
    def search():
        query = request.args.get("q", "")

        # LAB-VULNERABILITY: reflected Cross-Site Scripting (XSS).
        # Markup declares user-controlled input safe, so HTML is not escaped.
        return Markup(f"<h1>Search results for: {query}</h1>")

    @app.get("/products")
    def products():
        name = request.args.get("name", "")
        connection = sqlite3.connect(":memory:")
        connection.execute(
            "CREATE TABLE products (id INTEGER, name TEXT, price INTEGER)"
        )
        connection.executemany("INSERT INTO products VALUES (?, ?, ?)", PRODUCTS)

        # LAB-VULNERABILITY: SQL injection caused by string interpolation.
        # Production code must use a parameterized query instead.
        sql = f"SELECT id, name, price FROM products WHERE name = '{name}'"
        rows = connection.execute(sql).fetchall()
        connection.close()
        return jsonify(rows)

    return app


if __name__ == "__main__":
    # Loopback-only binding reduces the chance of accidental network exposure.
    create_app().run(host="127.0.0.1", port=8080, debug=False)
