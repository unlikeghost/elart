from  app import create_app

app = create_app()

if __name__ == '__main__':
    # app.run(debug=True)

    app.run(host="192.168.0.9",
            port=5000,
            debug=True)