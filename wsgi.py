from webapps import create_app

#  import venv

app = create_app()
# main update
if __name__ == "__main__":
    app.run(host="0.0.0.0")
