import requests as requests
from flask import Flask, request, jsonify, abort
from flask_marshmallow import Marshmallow
from settings import Settings
from client.model import Client, WishList, User, db
from flask_jwt_extended import create_access_token, jwt_required, JWTManager
from werkzeug.exceptions import BadRequest, Conflict, InternalServerError, Unauthorized, NotFound

HTTP_200_OK = 200
HTTP_401_UNAUTHORIZED = 401  # colocar em arquivo de config?
HTTP_201_OK = 201
HTTP_500_ERROR = 500

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = Settings.SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = Settings.SECRET_KEY
app.config['JWT_SECRET_KEY'] = Settings.JWT_SECRET_KEY
db.init_app(app)
ma = Marshmallow(app)
jwt = JWTManager(app)


class ClientSchema(ma.Schema):
    class Meta:
        fields = ('id', 'name', 'email')


client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password_hash')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


@app.route('/login', methods=['POST'])
def login():
    if 'username' not in request.json or 'password' not in request.json:
        abort(HTTP_401_UNAUTHORIZED, {'error': 'Credenciais inválidas'})
    username = request.json['username']
    password = request.json['password']

    try:
        user = User.query.filter_by(username=username).first()
        if user is None:
            raise Unauthorized('Usuário não encontrado')
        if not user.check_password(password):
            raise Unauthorized('Usuário ou senha incorreta')
        access_token = create_access_token(identity=user.id)
        return access_token, HTTP_200_OK

    except Unauthorized as e:
        raise e

    except Exception as e:
        app.logger.error(f"Erro durante a autenticação: {str(e)}")
        abort(HTTP_500_ERROR, {'error': 'Erro durante a autenticação'})


@app.route('/register', methods=['POST'])
def register():
    if 'username' not in request.json or 'password' not in request.json:
        raise BadRequest('Os campos "username" e "password" são obrigatórios.')
    username = request.json['username']
    password = request.json['password']

    try:
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise Conflict('Nome de usuário já existe.')
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuário registrado com sucesso'}), HTTP_201_OK

    except Exception as e:
        db.session.rollback()
        raise InternalServerError(f'Erro durante o registro do usuário: {str(e)}')


@app.route('/clients', methods=['POST'])
@jwt_required()
def add_client():
    try:
        if 'name' not in request.json or 'email' not in request.json:
            raise BadRequest('Os campos "name" e "email" são obrigatórios.')
        name = request.json['name']
        email = request.json['email']
        new_client = Client(name=name, email=email)
        db.session.add(new_client)
        db.session.commit()
        return client_schema.jsonify(new_client), HTTP_201_OK

    except Exception as e:
        db.session.rollback()
        raise InternalServerError(f'Erro durante a criação do cliente: {str(e)}')


@app.route('/clients', methods=['GET'])
@jwt_required()
def get_clients():
    try:
        all_clients = Client.query.all()
        if not all_clients:
            raise NotFound('Não foram encontrados clientes.')
        result = clients_schema.dump(all_clients)
        return jsonify(result), HTTP_200_OK

    except NotFound as e:
        raise e

    except Exception as e:
        raise InternalServerError(f'Erro ao buscar clientes: {str(e)}')


@app.route('/clients/<id_client>', methods=['GET'])
@jwt_required()
def get_client(id_client):
    try:
        client = Client.query.get(id_client)
        if not client:
            raise NotFound(f'Cliente com o ID {id_client} não encontrado.')
        result = client_schema.dump(client)
        return jsonify(result), HTTP_200_OK

    except Exception as e:
        raise InternalServerError(f'Erro ao buscar cliente: {str(e)}')


@app.route('/clients/<id_client>', methods=['PUT'])
@jwt_required()
def update_client(id_client):
    try:
        client = Client.query.get(id_client)
        if not client:
            raise NotFound(f'Cliente com o ID {id_client} não encontrado.')
        if 'name' in request.json:
            client.name = request.json['name']
        if 'email' in request.json:
            client.email = request.json['email']
        db.session.commit()
        updated_client = client_schema.dump(client)
        return jsonify(updated_client), HTTP_200_OK

    except BadRequest as e:
        raise BadRequest(f'Dados inválidos: {str(e)}')

    except Exception as e:
        raise InternalServerError(f'Erro ao atualizar cliente: {str(e)}')


@app.route('/clients/<id_client>', methods=['DELETE'])
@jwt_required()
def delete_client(id_client):
    try:
        client = Client.query.get(id_client)
        if not client:
            raise NotFound(f'Cliente com o ID {id_client} não encontrado.')
        db.session.delete(client)
        db.session.commit()
        return jsonify({'message': f'Cliente com o ID {id_client} foi deletado com sucesso.'}), HTTP_200_OK

    except NotFound as e:
        raise e

    except Exception as e:
        raise InternalServerError(f'Erro ao deletar cliente: {str(e)}')


class WishListSchema(ma.Schema):
    class Meta:
        fields = ('id_product', 'title', 'price', 'image', 'reviewScore')


wish_list_schema = WishListSchema()
wish_lists_schema = WishListSchema(many=True)


def check_product_exists(product_id):
    url = f'http://challenge-api.luizalabs.com/api/product/{product_id}/'
    response = requests.get(url)
    return response.status_code == HTTP_200_OK


def get_product_details(id_product):
    url = f'http://challenge-api.luizalabs.com/api/product/{id_product}/'
    response = requests.get(url)
    if response.status_code == HTTP_200_OK:
        product_data = response.json()
        product_details = {
            'id_product': product_data['id'],
            'title': product_data['title'],
            'price': product_data['price'],
            'image': product_data['image']
        }
        if product_data.get('reviewScore'):
            product_details['reviewScore'] = product_data.get('reviewScore')
        return product_details
    else:
        return None


@app.route('/wish-list/<int:client_id>', methods=['GET'])
@jwt_required()
def get_wish_list(client_id):
    try:
        wish_list_items = WishList.query.filter_by(client_id=client_id).all()
        product_details_list = []
        for item in wish_list_items:
            product_details = get_product_details(item.product_id)
            if product_details:
                product_details_list.append(product_details)
        return jsonify(product_details_list), HTTP_200_OK

    except Exception as e:
        raise InternalServerError(f'Erro ao obter lista de desejos: {str(e)}')


@app.route('/wish-list/<int:client_id>', methods=['POST'])
@jwt_required()
def add_to_wish_list(client_id):
    try:
        product_id = request.json.get('product_id')
        if not check_product_exists(product_id):
            raise NotFound('O produto não existe e não pode ser adicionado à lista de desejos')
        existing_item = WishList.query.filter_by(client_id=client_id, product_id=product_id).first()
        if existing_item:
            return jsonify({'message': 'Este produto já está na lista de desejos'}), HTTP_200_OK
        new_item = WishList(client_id=client_id, product_id=product_id)
        db.session.add(new_item)
        db.session.commit()
        return jsonify({'message': 'Produto adicionado à lista de desejos'}), HTTP_201_OK

    except NotFound as e:
        raise e

    except Exception as e:
        raise InternalServerError(f'Erro ao adicionar produto à lista de desejos: {str(e)}')


@app.route('/wish-list/<int:client_id>/<product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_wish_list(client_id, product_id):
    try:
        item = WishList.query.filter_by(client_id=client_id, product_id=product_id).first()
        if item:
            db.session.delete(item)
            db.session.commit()
            return jsonify({'message': f'Item removido da lista de desejos do cliente {client_id}'}), HTTP_200_OK
        else:
            raise NotFound('Item não encontrado na lista de desejos')
    except NotFound as e:
        raise e
    except Exception as e:
        raise InternalServerError(f'Erro ao remover item da lista de desejos: {str(e)}')

# if __name__ == '__main__':
#     app.run(debug=True)
