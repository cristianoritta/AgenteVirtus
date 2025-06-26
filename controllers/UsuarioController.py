from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models.models import Usuario
from config import db

class UsuarioController:
    @staticmethod
    def index():
        usuarios = Usuario.query.all()
        return render_template('admin/usuarios.html', usuarios=usuarios)
    
    @staticmethod
    def minhaconta():
        usuario = Usuario.query.get(1)
        
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            telefone = request.form['telefone']
            
            usuario.nome = nome
            usuario.email = email
            usuario.telefone = telefone
            db.session.commit()
            
        return render_template('admin/minhaconta.html', usuario=usuario)
    
    @staticmethod
    def novo():
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            
            if not nome or not email:
                flash('Por favor, preencha todos os campos!', 'error')
                return redirect(url_for('novo_usuario'))
            
            # Verificar se o email já existe
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                flash('Este email já está cadastrado!', 'error')
                return redirect(url_for('novo_usuario'))
            
            novo_usuario = Usuario(nome=nome, email=email)
            db.session.add(novo_usuario)
            db.session.commit()
            
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('usuarios'))
        
        return render_template('novo_usuario.html')
    
    @staticmethod
    def ver(id):
        usuario = Usuario.query.get_or_404(id)
        now = datetime.utcnow()
        return render_template('ver_usuario.html', usuario=usuario, now=now)
    
    @staticmethod
    def editar(id):
        usuario = Usuario.query.get_or_404(id)
        
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            
            if not nome or not email:
                flash('Por favor, preencha todos os campos!', 'error')
                return redirect(url_for('editar_usuario', id=id))
            
            # Verificar se o email já existe (exceto para o usuário atual)
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente and usuario_existente.id != id:
                flash('Este email já está cadastrado!', 'error')
                return redirect(url_for('editar_usuario', id=id))
            
            usuario.nome = nome
            usuario.email = email
            db.session.commit()
            
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('ver_usuario', id=id))
        
        return render_template('editar_usuario.html', usuario=usuario)
    
    @staticmethod
    def deletar(id):
        usuario = Usuario.query.get_or_404(id)
        db.session.delete(usuario)
        db.session.commit()
        flash('Usuário deletado com sucesso!', 'success')
        return redirect(url_for('usuarios'))
    
    @staticmethod
    def api_usuarios():
        usuarios = Usuario.query.all()
        return jsonify([{
            'id': u.id,
            'nome': u.nome,
            'email': u.email,
            'data_criacao': u.data_criacao.isoformat()
        } for u in usuarios])