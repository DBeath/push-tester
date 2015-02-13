from .. import app
from flask.ext.assets import Bundle, Environment

bundles = {
	'main_js': Bundle(
		'js/jquery-2.1.3.min.js',
		'js/moment.min.js',
		'js/bootstrap.min.js',
		'js/bootstrap-datetimepicker.min.js',
		output='gen/main.js'),

	'main_css': Bundle(
		'css/bootstrap.min.css',
		'css/bootstrap-datetimepicker.min.css',
		'css/font-awesome.min.css',
		'css/custom-style.css',
		output='gen/main.css') 
}

assets = Environment(app)

assets.register(bundles)
