from  managerzk.app import create_app

app = create_app('release')

if __name__ == '__main__':
    app.run()