from config import app, db
from routes import init_routes
from filters import register_filters
from models.models import criar_usuario_inicial

# Registrar filtros customizados
register_filters(app)

init_routes(app)

if __name__ == '__main__':
    # E chame isso dentro de um contexto de aplicação:
    with app.app_context():
        
        db.create_all()
        criar_usuario_inicial()
        
    app.run(debug=True) 