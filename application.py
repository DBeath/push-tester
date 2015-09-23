from push_tester import create_app

application = create_app('config.ProductionConfig')

if __name__ == '__main__':
    application.run()
