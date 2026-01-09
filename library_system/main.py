import os
import secrets
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
 
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'library.db')

db = SQLAlchemy(app)
tokens = {}
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    full_name = db.Column(db.String(120))
    """
        def __init__(self,id,username,password,email,full_name):
            self.id = id
            self.username = username
            self.password = password
            self.email = email
            self.full_name = full_name
    """


@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    #init호출
    new_user = User(username=data['username'], password=data['password'], email=data['email'], full_name=data['full_name'])
    db.session.add(new_user)
    db.session.commit()
    return {"message": "회원가입 성공"}, 201
@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.password == data['password']:
        access_token = secrets.token_hex(16)
        tokens[access_token] = user.username
        return {
            "access_token": access_token,
            "message": "로그인 성공"
        }, 200

    return {"message": "로그인 실패"}, 401



class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    isbn = db.Column(db.String(20))
    category = db.Column(db.String(50))
    total_copies = db.Column(db.Integer, default=1)

@app.route('/books', methods=['POST'])
def add_book():

    auth_header = request.headers.get('Authorization')
    if not auth_header or "Bearer " not in auth_header:
        return {"message": "인증 토큰이 없습니다."}, 401
    token = auth_header.split(" ")[1]
    if token not in tokens:
        return {"message": "유효하지 않은 토큰입니다."}, 401  #토큰 인증

    data = request.get_json()
    new_book = Book(title=data['title'],author=data['author'],isbn=data['isbn'],category=data['category'],total_copies=data['total_copies'])
    db.session.add(new_book)
    db.session.commit()
    return {"message": "책 등록 성공"}, 201
@app.route('/books', methods=['GET'])
def search_books():
    category = request.args.get('category')
    available = request.args.get('available')

    query = Book.query
    if category:
        query = query.filter_by(category=category)
    books = query.all()
    result = []
    for book in books:
        result.append({"id": book.id,"title": book.title,"author": book.author,"category": book.category})
    return {"books": result}, 200




class Loan(db.Model):
    __tablename__ = 'loans'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    loan_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    is_returned = db.Column(db.Boolean, default=False)

@app.route('/loans', methods=['POST'])
def add_loan():
    auth_header = request.headers.get('Authorization')
    if not auth_header or "Bearer " not in auth_header:
        return {"message": "인증 토큰이 없습니다."}, 401
    token = auth_header.split(" ")[1]
    if token not in tokens:
        return {"message": "유효하지 않은 토큰입니다."}, 401  #토큰 인증

    data = request.get_json()
    book_id = data.get('book_id')
    user_id = data.get('user_id')
    book = Book.query.get(book_id)
    if not book:
        return {"message": "해당 책을 찾을 수 없습니다."}, 404
    if book.total_copies <= 0:
        return {"message": "현재 대여 가능한 재고가 없습니다."}, 400
    new_loan = Loan(user_id=user_id, book_id=book_id)
    book.total_copies -= 1
    db.session.add(new_loan)
    db.session.commit()
    return {"message": "대여 완료되었습니다."}, 201

@app.route('/users/me/loans', methods=['GET'])
def get_my_loans():
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(" ")[1]
    username = tokens.get(token)
    user = User.query.filter_by(username=username).first()
    my_loans = Loan.query.filter_by(user_id=user.id).all()
    return {
        "loans": [
            {
                "book_id": loan.book_id,
                "loan_date": str(loan.loan_date)
            } for loan in my_loans
        ]
    }, 200





if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)











