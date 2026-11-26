"""Compatibility launcher; application code lives in sql_frontend.py and sql_backend.py."""

from sql_frontend import QueryApp


if __name__ == "__main__":
    QueryApp().mainloop()
