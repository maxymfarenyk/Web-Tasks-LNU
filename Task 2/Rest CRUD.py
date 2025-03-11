from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bookstore.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Моделі даних
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    country = db.Column(db.String(50))
    books = db.relationship('Book', backref='author', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    publication_date = db.Column(db.Date)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    reviews = db.relationship('Review', backref='book', cascade='all, delete-orphan')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    reviewer_name = db.Column(db.String(100))
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Створення бази даних
with app.app_context():
    db.create_all()


# Допоміжні функції
def serialize_author(author):
    return {
        'id': author.id,
        'name': author.name,
        'birth_date': author.birth_date.isoformat() if author.birth_date else None,
        'country': author.country,
        'created_at': author.created_at.isoformat(),
        'updated_at': author.updated_at.isoformat()
    }


def serialize_book(book, include_reviews=False):
    data = {
        'id': book.id,
        'title': book.title,
        'description': book.description,
        'publication_date': book.publication_date.isoformat() if book.publication_date else None,
        'author_id': book.author_id,
        'created_at': book.created_at.isoformat(),
        'updated_at': book.updated_at.isoformat()
    }

    if include_reviews:
        data['reviews'] = [serialize_review(review) for review in book.reviews]

    return data


def serialize_review(review):
    return {
        'id': review.id,
        'content': review.content,
        'rating': review.rating,
        'reviewer_name': review.reviewer_name,
        'book_id': review.book_id,
        'created_at': review.created_at.isoformat(),
        'updated_at': review.updated_at.isoformat()
    }


# API для авторів (Authors)
@app.route('/api/authors', methods=['GET'])
def get_authors():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')

    query = Author.query

    # Сортування
    if hasattr(Author, sort_by):
        column = getattr(Author, sort_by)
        if sort_order == 'desc':
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))

    # Пагінація
    authors = query.paginate(page=page, per_page=per_page)

    response = {
        'items': [serialize_author(author) for author in authors.items],
        'total': authors.total,
        'pages': authors.pages,
        'page': page
    }

    return jsonify(response)


@app.route('/api/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    author = Author.query.get_or_404(author_id)
    return jsonify(serialize_author(author))


@app.route('/api/authors', methods=['POST'])
def create_author():
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400

    author = Author(
        name=data['name'],
        birth_date=datetime.fromisoformat(data['birth_date']) if 'birth_date' in data and data['birth_date'] else None,
        country=data.get('country')
    )

    db.session.add(author)
    db.session.commit()

    return jsonify(serialize_author(author)), 201


@app.route('/api/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    author = Author.query.get_or_404(author_id)
    data = request.get_json()

    if 'name' in data:
        author.name = data['name']
    if 'birth_date' in data:
        author.birth_date = datetime.fromisoformat(data['birth_date']) if data['birth_date'] else None
    if 'country' in data:
        author.country = data['country']

    db.session.commit()

    return jsonify(serialize_author(author))


@app.route('/api/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    author = Author.query.get_or_404(author_id)

    db.session.delete(author)
    db.session.commit()

    return '', 204


# API для книг (Books)
@app.route('/api/books', methods=['GET'])
def get_books():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    author_id = request.args.get('author_id', type=int)

    query = Book.query

    # Фільтрація за автором
    if author_id:
        query = query.filter_by(author_id=author_id)

    # Сортування
    if hasattr(Book, sort_by):
        column = getattr(Book, sort_by)
        if sort_order == 'desc':
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))

    # Пагінація
    books = query.paginate(page=page, per_page=per_page)

    response = {
        'items': [serialize_book(book) for book in books.items],
        'total': books.total,
        'pages': books.pages,
        'page': page
    }

    return jsonify(response)


@app.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    include_reviews = request.args.get('include_reviews', 'false').lower() == 'true'

    return jsonify(serialize_book(book, include_reviews=include_reviews))


@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()

    if not data or 'title' not in data or 'author_id' not in data:
        return jsonify({'error': 'Title and author_id are required'}), 400

    # Перевірка наявності автора
    author = Author.query.get(data['author_id'])
    if not author:
        return jsonify({'error': f"Author with id {data['author_id']} not found"}), 404

    book = Book(
        title=data['title'],
        description=data.get('description'),
        publication_date=datetime.fromisoformat(data['publication_date']) if 'publication_date' in data and data[
            'publication_date'] else None,
        author_id=data['author_id']
    )

    db.session.add(book)
    db.session.commit()

    return jsonify(serialize_book(book)), 201


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    if 'title' in data:
        book.title = data['title']
    if 'description' in data:
        book.description = data['description']
    if 'publication_date' in data:
        book.publication_date = datetime.fromisoformat(data['publication_date']) if data['publication_date'] else None
    if 'author_id' in data:
        # Перевірка наявності автора
        author = Author.query.get(data['author_id'])
        if not author:
            return jsonify({'error': f"Author with id {data['author_id']} not found"}), 404
        book.author_id = data['author_id']

    db.session.commit()

    return jsonify(serialize_book(book))


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)

    db.session.delete(book)
    db.session.commit()

    return '', 204


# API для відгуків (Reviews)
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    book_id = request.args.get('book_id', type=int)

    query = Review.query

    # Фільтрація за книгою
    if book_id:
        query = query.filter_by(book_id=book_id)

    # Сортування
    if hasattr(Review, sort_by):
        column = getattr(Review, sort_by)
        if sort_order == 'desc':
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))

    # Пагінація
    reviews = query.paginate(page=page, per_page=per_page)

    response = {
        'items': [serialize_review(review) for review in reviews.items],
        'total': reviews.total,
        'pages': reviews.pages,
        'page': page
    }

    return jsonify(response)


@app.route('/api/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    review = Review.query.get_or_404(review_id)
    return jsonify(serialize_review(review))


@app.route('/api/reviews', methods=['POST'])
def create_review():
    data = request.get_json()

    if not data or 'content' not in data or 'book_id' not in data:
        return jsonify({'error': 'Content and book_id are required'}), 400

    # Перевірка наявності книги
    book = Book.query.get(data['book_id'])
    if not book:
        return jsonify({'error': f"Book with id {data['book_id']} not found"}), 404

    review = Review(
        content=data['content'],
        rating=data.get('rating'),
        reviewer_name=data.get('reviewer_name'),
        book_id=data['book_id']
    )

    db.session.add(review)
    db.session.commit()

    return jsonify(serialize_review(review)), 201


@app.route('/api/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    review = Review.query.get_or_404(review_id)
    data = request.get_json()

    if 'content' in data:
        review.content = data['content']
    if 'rating' in data:
        review.rating = data['rating']
    if 'reviewer_name' in data:
        review.reviewer_name = data['reviewer_name']
    if 'book_id' in data:
        # Перевірка наявності книги
        book = Book.query.get(data['book_id'])
        if not book:
            return jsonify({'error': f"Book with id {data['book_id']} not found"}), 404
        review.book_id = data['book_id']

    db.session.commit()

    return jsonify(serialize_review(review))


@app.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    db.session.delete(review)
    db.session.commit()

    return '', 204


# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True)