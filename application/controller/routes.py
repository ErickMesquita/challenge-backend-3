from application.wsgi import app


@app.get("/teste")
def teste():
	return "<h1>Teste</h1><h4>Funciona!!!</h4>"
