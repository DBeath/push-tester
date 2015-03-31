from push_tester import create_app

app = create_app('config.ProductionConfig')

if __name__ == '__main__':
    app.run()
