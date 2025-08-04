from config import app, db
from routes import init_routes
from filters import register_filters
from models.models import criar_usuario_inicial, EquipeInteligente, Formulario
from migrations import migrate  # Importando o Flask-Migrate

# Registrar filtros customizados
register_filters(app)

# Contexto global para carregar menus dinâmicos
@app.before_request
def carregar_menus_dinamicos():
    """Carrega os menus dinâmicos da tabela EquipeInteligente e Formulario"""
    try:
        # Busca todas as equipes com menu_ordem > 0, ordenadas por menu_ordem
        menus_dinamicos = EquipeInteligente.query.filter(
            EquipeInteligente.menu_ordem > 0
        ).order_by(EquipeInteligente.menu_ordem).all()
        
        # Busca todos os formulários ativos com menu_ordem > 0, ordenados por menu_ordem
        formularios_dinamicos = Formulario.query.filter(
            Formulario.ativo == True,
            Formulario.menu_ordem > 0
        ).order_by(Formulario.menu_ordem).all()
        
        # Adiciona os menus à sessão para uso nos templates
        app.jinja_env.globals['menus'] = menus_dinamicos
        app.jinja_env.globals['formularios'] = formularios_dinamicos
    except Exception as e:
        # Em caso de erro, define menus como lista vazia
        app.jinja_env.globals['menus'] = []
        app.jinja_env.globals['formularios'] = []
        print(f"Erro ao carregar menus dinâmicos: {e}")

init_routes(app)



if __name__ == '__main__':
    # E chame isso dentro de um contexto de aplicação:
    with app.app_context():
        
        db.create_all()
        criar_usuario_inicial()
        
    app.run(debug=True) 