from app import create_app

# O ponto de entrada da aplicação
app = create_app()

if __name__ == '__main__':
    # Roda a aplicação na porta 5000 e host 0.0.0.0 (padrão Docker)
    app.run(debug=True, host='0.0.0.0', port=5000)