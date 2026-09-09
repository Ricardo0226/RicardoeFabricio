from flask import Flask, render_template, jsonify, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'labinfo',
    'database': 'labagenda'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def get_laboratorios():
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT numero, descriçao, status FROM lab")
        laboratorios = cursor.fetchall()
        cursor.close()
        return laboratorios
    except Error as e:
        print(f"Erro ao buscar laboratórios: {e}")
        return []
    finally:
        connection.close()

def get_professores():
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT matricula, nome, area FROM professor")
        professores = cursor.fetchall()
        cursor.close()
        return professores
    except Error as e:
        print(f"Erro ao buscar professores: {e}")
        return []
    finally:
        connection.close()

def get_disciplinas_por_professor(matricula_professor):
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT d.codigo, d.nome, d.ch
            FROM disciplina d
            JOIN professor_disciplina pd ON d.codigo = pd.codigo_disciplina
            WHERE pd.matricula_professor = %s
        """, (matricula_professor,))
        disciplinas = cursor.fetchall()
        cursor.close()
        return disciplinas
    except Error as e:
        print(f"Erro ao buscar disciplinas: {e}")
        return []
    finally:
        connection.close()

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/index')
def index():
    laboratorios = get_laboratorios()
    professores = get_professores()
    
    return render_template('index.html', 
                         laboratorios=laboratorios,
                         professores=professores)

@app.route('/api/disciplinas/<matricula>')
def api_disciplinas(matricula):
    disciplinas = get_disciplinas_por_professor(matricula)
    return jsonify(disciplinas)



def salvar_agendamento(laboratorio, professor_matricula, disciplina_nome, dia_semana, horario_periodo):
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        delete_query = """
            DELETE FROM agendamento 
            WHERE laboratorio = %s AND dia_semana = %s AND horario_periodo = %s
        """
        cursor.execute(delete_query, (laboratorio, dia_semana, horario_periodo))
        
        insert_query = """
            INSERT INTO agendamento (laboratorio, professor_matricula, disciplina_nome, dia_semana, horario_periodo)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (laboratorio, professor_matricula, disciplina_nome, dia_semana, horario_periodo))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Erro ao salvar agendamento: {e}")
        return False
    finally:
        connection.close()

def get_agendamentos_por_lab(laboratorio):
    connection = get_db_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT professor_matricula as professor, disciplina_nome as disciplina, dia_semana as dia, horario_periodo as horario
            FROM agendamento
            WHERE laboratorio = %s
        """, (laboratorio,))
        agendamentos = cursor.fetchall()
        cursor.close()
        return agendamentos
    except Error as e:
        print(f"Erro ao buscar agendamentos: {e}")
        return []
    finally:
        connection.close()


def inserir_lab(capacidade, numero, descricao, status='aberto'):
    connection = get_db_connection()
    if not connection:
        return False
    try:
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO lab (capacidade, numero, descriçao, status)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(insert_query, (capacidade, numero, descricao, status))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Erro ao inserir laboratório: {e}")
        return False
    finally:
        connection.close()

def limpar_agendamentos_por_lab(laboratorio):
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        delete_query = "DELETE FROM agendamento WHERE laboratorio = %s"
        cursor.execute(delete_query, (laboratorio,))
        connection.commit()
        cursor.close()
        return True
    except Error as e:
        print(f"Erro ao limpar agendamentos: {e}")
        return False
    finally:
        connection.close()


@app.route('/api/lab/<laboratorio>/status', methods=['GET', 'POST'])
def api_lab_status(laboratorio):
    connection = get_db_connection()
    if not connection:
        return jsonify({"success": False, "message": "Erro de conexão"}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        if request.method == 'GET':
            cursor.execute("SELECT numero, status FROM lab WHERE numero = %s", (laboratorio,))
            row = cursor.fetchone()
            cursor.close()
            if row:
                return jsonify({"numero": row['numero'], "status": row.get('status', 'aberto')}), 200
            else:
                return jsonify({}), 404

        # POST -> atualizar status
        data = request.get_json()
        new_status = data.get('status')
        if new_status not in ('aberto', 'fechado', 'manutenção'):
            return jsonify({"success": False, "message": "Status inválido"}), 400

        update_query = "UPDATE lab SET status = %s WHERE numero = %s"
        cursor.execute(update_query, (new_status, laboratorio))
        connection.commit()
        cursor.close()
        return jsonify({"success": True}), 200
    except Error as e:
        print(f"Erro ao acessar/atualizar status: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        connection.close()

@app.route('/api/agendamentos/salvar', methods=['POST'])
def api_salvar_agendamento():
    data = request.get_json()
    
    professor_matricula = data.get('professor')
    disciplina_nome = data.get('disciplina')
    dia_semana = data.get('dia')
    horario_periodo = data.get('horario')
    laboratorio = data.get('laboratorio')
    
    if salvar_agendamento(laboratorio, professor_matricula, disciplina_nome, dia_semana, horario_periodo):
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Falha ao salvar agendamento"}), 500

@app.route('/api/agendamentos/<laboratorio>', methods=['GET'])
def api_get_agendamentos(laboratorio):
    agendamentos = get_agendamentos_por_lab(laboratorio)
    return jsonify(agendamentos)

@app.route('/api/agendamentos/<laboratorio>', methods=['DELETE'])
def api_limpar_agendamentos(laboratorio):
    if limpar_agendamentos_por_lab(laboratorio):
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Falha ao limpar agendamentos"}), 500

@app.route('/agenda')
def agenda():
    lab_id = request.args.get('lab_id', type=int)
    laboratorios = get_laboratorios()
    return render_template('agenda.html', laboratorios=laboratorios, lab_id=lab_id)

@app.route('/menu')
def menu():
    laboratorios = get_laboratorios()
    return render_template('menu.html', laboratorios=laboratorios)


@app.route('/menu/adicionar', methods=['GET', 'POST'])
def newlab():
    if request.method == 'POST':
        numero = request.form.get('numero')
        capacidade = request.form.get('capacidade')
        descricao = request.form.get('descricao')

        if not numero:
            return render_template('newlab.html', error='Número do laboratório é obrigatório')

        sucesso = inserir_lab(capacidade or '', numero, descricao or '')
        if sucesso:
            return redirect(url_for('menu'))
        else:
            return render_template('newlab.html', error='Falha ao inserir laboratório no banco')

    return render_template('newlab.html')
