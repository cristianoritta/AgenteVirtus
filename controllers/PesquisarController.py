from flask import render_template, request, jsonify
import tempfile
import controllers.IaController as IaController
import os
from datetime import datetime


class PesquisarController:
    @staticmethod
    def pesquisar():
        """Página para pesquisar no banco de dados"""
        expressao = request.form.get('pesquisar-expressao')
        print(expressao)
        
        return render_template('pesquisar/pesquisar.html', expressao=expressao)
