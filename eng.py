# -*- coding: UTF-8 -*-
import os
from flask import Flask, g, render_template, request, jsonify, url_for, send_file, redirect
from models import db_session, Shop, PWZ, Product, Order, User, Categorie, OrderItems, Zakazi
import settings
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import uuid
from datetime import datetime

app = Flask(__name__, template_folder="templates")

app.config['SECRET_KEY'] = str(uuid.uuid4())
manager = LoginManager(app)

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        user = User.query.filter_by(name=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('Wpage', page_name='index'))  # Измените на вашу главную страницу
        else:
            # В случае неверного логина или пароля, вы можете вернуть ошибку или перенаправить обратно на страницу входа
            return render_template('login', error='Invalid username or password')
    return render_template("login.html")

@app.route("/logout/")
@login_required
def logout():
    logout_user()
    return redirect(url_for('Wpage', page_name='index'))  # Измените на вашу главную страницу

@app.route("/registration/", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        email = request.form['email']
        # Дополнительная логика проверки, например, проверка уникальности имени пользователя и т.д.
        new_user = User(name=username, password=password, mail=email)
        db_session.add(new_user)
        db_session.commit()
        login_user(new_user)
        return redirect(url_for('Wpage'))  # Исправлено
    return render_template("registration.htm")


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.htm'), 404

@app.route("/tovaru/")
def Wpage():
    categories = db_session.query(Categorie).all()
    products = db_session.query(Product).all()
    return render_template('tovaru.htm', page_name='Товары', categories=categories, product=products, is_male=False)

@app.route("/men/")
def Mpage():
    categories = db_session.query(Categorie).all()
    products = db_session.query(Product).all()
    return render_template("tovaru.htm", page_name="men", categories=categories, product=products, is_male=True)

@app.route("/orders/")
def Orders():
    orders = db_session.query(Order).all().filterby(userid=current_user.id).all()
    zakazi = db_session.query(Zakazi).all()
    return render_template("Orders.html", page_name="men", orders=orders, zakazi=zakazi, is_male=True)


@app.route("/bucket/")
@login_required
def Bucketpage():
    user_id = current_user.id
    user_bucket = db_session.query(OrderItems).filter(OrderItems.id_user == user_id).all()
    total_price = sum(item.product.cost for item in user_bucket)

    return render_template("bucket.htm", page_name="bucket", bucket=user_bucket, total_price=total_price)

@app.route("/bucket/", methods=['POST'])
@login_required
def Bucketpage_form():
    if request.method == 'POST':
        # Получаем данные из формы
        delivery_option = request.form.get('type')
        address = request.form.get('address')
        recipient = request.form.get('recipient')
        payment_method = request.form.get('payment')
        delivery_date_str = request.form.get('delivery_date')
        delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()

        # Получаем все элементы корзины текущего пользователя
        user_id = current_user.id
        user_bucket = db_session.query(OrderItems).filter(OrderItems.id_user == user_id).all()
        summa = sum([item.product_cost * item.product_quantity for item in user_bucket])

        # Создаем новый заказ
        new_order = Order(
            delivery_type=delivery_option,
            address=address,
            delivery_date=delivery_date,
            total=summa
        )

        # Добавляем заказ в базу данных
        db_session.add(new_order)
        db_session.flush()  # Flush чтобы получить идентификатор только что созданного заказа
        order_id = new_order.id

        # Добавляем товары из корзины в таблицу Zakazi
        for item in user_bucket:
            # Получаем количество товара из формы
            #quantity = int(request.form.get(f'quantity_{item.product.id}', 1))
            new_zakazi = Zakazi(
                id_user=item.id_user,
                id_order=order_id,
                id_product=item.id_product,
                product_cost=item.product_cost,
                product_quantity=item.product_quantity,
                product=item.product
            )
            db_session.add(new_zakazi)

        # Удаляем все элементы корзины пользователя
        db_session.query(OrderItems).filter(OrderItems.id_user == user_id).delete()

        db_session.commit()

    return redirect(url_for("Wpage"))





@app.route("/tovaru/card/<int:id>/")
def card_by_id(id):
    item = db_session.query(Product).filter(Product.id == id).first()
    return render_template("card.htm", card_item=item)

@app.route("/tovaru/<int:category_id>/")
def prod_by_categ(category_id):
    item = db_session.query(Product).filter(Product.category_id == category_id).all()
    return render_template("tovaru.htm", page_name="tovar", product=item)

@app.route("/category/<int:category_id>/")
def show_category(category_id):
    # Получаем продукты определенной категории из базы данных
    products = db_session.query(Product).filter(Product.category_id == category_id).all()
    # Получаем информацию о категории
    category = db_session.query(Categorie).all()  # Здесь должен быть список категорий, а не одиночный объект
    return render_template("category.htm", category=category, products=products, is_male=False)



@app.route("/add_item/")
@login_required
def add_item_to_cart():
    # Получаем id товара и id пользователя из запроса
    item_id = request.args.get("item_id")
    user_id = current_user.id

    existing_item = db_session.query(OrderItems).filter(OrderItems.id_product == item_id, OrderItems.id_user == user_id).first()

    if existing_item:
        pass
    else:
        # Если товара еще нет в корзине, получаем информацию о товаре и создаем новый объект OrderItems
        product = db_session.query(Product).filter(Product.id == item_id).first()
        new_item = OrderItems(id_user=user_id, id_product=item_id, product=product, product_cost=product.cost)
        db_session.add(new_item)
        db_session.commit()

    # После добавления товара в корзину, перенаправляем пользователя на ту же страницу
    return redirect(request.referrer)

from flask import request, jsonify

@app.route("/update_quantity/<int:item_id>", methods=['POST'])
@login_required
def update_quantity(item_id):
    # Получаем количество товаров из формы
    new_quantity = int(request.form.get(f'quantity_{item_id}'))

    # Находим объект корзины для текущего пользователя и товара
    bucket_item = db_session.query(OrderItems).filter(OrderItems.id_product == item_id, OrderItems.id_user == current_user.id).first()

    # Проверяем, существует ли такой объект корзины
    if bucket_item:
        # Обновляем количество товаров в корзине
        bucket_item.product_quantity = new_quantity
        db_session.commit()
        return redirect(url_for('Bucketpage'))  # Перенаправляем пользователя обратно на страницу корзины
    else:
        # Если объект корзины не найден, вернем ошибку или выполним другие действия
        return "Item not found in bucket", 404


@app.route("/remove_from_bucket/<int:item_id>", methods=['POST'])
@login_required
def remove_item_from_bucket(item_id):
    # Получаем id текущего пользователя
    user_id = current_user.id

    # Находим объект заказа, соответствующий пользователю и товару
    order_item = db_session.query(OrderItems).filter(OrderItems.id_product == item_id, OrderItems.id_user == user_id).first()

    # Проверяем, существует ли такой объект заказа
    if order_item:
        # Удаляем объект заказа из базы данных
        db_session.delete(order_item)
        db_session.commit()
        return redirect(url_for('Bucketpage'))  # Перенаправляем пользователя обратно на страницу корзины
    else:
        # Если объект заказа не найден, вернем ошибку или выполним другие действия
        return render_template('error.html', message='Item not found in bucket'), 404




@app.route("/<page_name>/")
def main(page_name):
    return render_template(page_name + ".htm")

@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5057, debug=True)
