"""
    Ventas casa por casa - Equipo 1
    ✅ 1. Debe poder autenticarse a la aplicación como dueño de la tienda,
       o registrar nueva tienda (Usuario, Contraseña, Correo, Nombre de la Tienda)

    ✅ 2. El dueño de la tienda puede agregar, eliminar, editar,
       y buscar clientes (Nombre, Dirección, Teléfono, Correo electrónico)

    ✅ 3. El dueño de la tienda puede agregar, eliminar, editar, y buscar productos
       (Nombre del producto, descripción, cantidad de productos, precio de costo, precio de venta, fotografía por URL)

    ✅ 4. El dueño de la tienda puede registrar una venta, seleccionando al cliente
       y productos que va a vender, los cuales deben ser descontados del inventario.

    ✅ 5. El dueño puede ver lo que a vendido por, día, por mes, por año o en un periodo dado.

    ✅ 6. El dueño puede cerrar la sesión y salirse de la aplicación.
"""

from flask import (
    Flask,
    redirect,
    url_for,
    g,
    session,
    request,
    render_template
)
import mysql.connector

import mysql.connector

connectet_to_db = False
try:
    mydb = mysql.connector.connect(
                                    host="localhost", 
                                    user="root",
                                    passwd="rootpassword",
                                    port=3306
                                    )
    print(mydb)
    mycursor = mydb.cursor()
    mycursor.execute("use ventascasaxcasas")
    connectet_to_db = True
except:
    print("It was not possible to connect to the database")

app = Flask(__name__,
            template_folder='web/templates',
            static_folder='web/static',)

app.secret_key = 'thisisareallycoolpasswordyeeeeeeep'


class User:
    def __init__(self, id, username, store_id, storename, image):
        print(id, username, store_id, storename)
        self.id = id
        self.username = username
        self.store_id = store_id
        self.storename = storename
        self.image = image
    
    def __str__(self) -> str:
        return f"{self.id}, {self.username}, {self.store_id}, {self.storename}, {self.image}"


@app.before_request
def before_request():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    g.user = None
    if 'user_id' in session:
        mycursor.execute(f"""SELECT
                                u.user_id,
                                u.username, 
                                s.store_id,
                                s.storename,
                                u.image
                            from users u
                            left join stores s
                            on u.user_id = s.user_id
                            where u.user_id = {session['user_id']} """)
        user_data = mycursor.fetchone()
        g.user = User(*user_data)

@app.route('/')
def main():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if g.user:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login')
@app.route('/login/')
def login():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if g.user:
        return redirect(url_for('dashboard'))
    username = request.args.get('username', '')
    modal = request.args.get('modal', '')
    alertmodal = request.args.get('myalertmodal', '')
    message = request.args.get('mymessage', '')

    return render_template('login.html', myusername=username, mymodal=modal, myalertmodal=alertmodal, mymessage=message)

@app.route('/login/validate', methods=['POST', 'GET'])
def validate_user():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if request.method == 'POST':
        mycursor.execute(f"SELECT COUNT(*) FROM users where username like '{request.form.get('username')}'")
        user_count = mycursor.fetchone()[0]
        if user_count > 0:
            mycursor.execute(f"""SELECT
                                u.user_id,
                                u.username, 
                                s.store_id,
                                s.storename,
                                u.image,
                                u.password_hash
                                from users u
                                left join stores s
                            on u.user_id = s.user_id
                            where u.username like  '{request.form.get('username')}'""")
            user_data = mycursor.fetchone()
            passowrd_from_db = user_data[-1]
            if request.form.get('password') == passowrd_from_db:
                print(*user_data[0:-1])
                g.user = User(*user_data[0:-1])
                session['user_id'] = g.user.id
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('login', myalertmodal='block', mymessage="⚠️ Verifica que tu usuario/contraseña sean los correctos ⚠️"))
        else:
            return redirect(url_for('login', myalertmodal='block', mymessage="🚫 Ups!, ese usuario no esta registrado 🚫"))
    else:
        return redirect('/login', code=302)

@app.route('/signup')
@app.route('/signup/')
def signup(modal='none'):
    if g.user:
        return redirect(url_for('dashboard'))
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    return render_template('signup.html', modal=modal)

@app.route('/signup/validate', methods=['POST', 'GET'])
def signup_validate():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if request.method == 'POST':
        #return f"{request.form.get('user')} {request.form.get('pswd2')}"
        mycursor.execute(f"SELECT COUNT(*) FROM users where username like '{request.form.get('username')}'")
        myresult = mycursor.fetchone()
        if myresult[0] == 0:
            username = request.form.get('username')
            mail = request.form.get('email')
            password_hash = request.form.get('password')
            query_insert_user = "INSERT INTO users (username, password_hash, mail) VALUES (%s, %s, %s)"
            val = (username, password_hash, mail)
            mycursor.execute(query_insert_user, val)
            mydb.commit()
            user_id = mycursor.lastrowid

            storename = request.form.get('storename')
            query_insert_table = "INSERT INTO stores (storename, user_id) VALUES (%s, %s)"
            val = (storename, user_id)
            mycursor.execute(query_insert_table, val)
            mydb.commit()

            return redirect(url_for('login', username=username, modal='block'))
        else:
            return render_template('/signup.html', modal="block")
            #"""<h1>Ups!, Ya existe un usuario con ese nombre</h1>
            #        <a href='/signup'>regresar</a>"""
    else:
        return redirect('/signup', code=302)

@app.route('/dashboard', methods=['POST', 'GET'])
def dashboard():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))

    mycursor.execute(f"""
                        SELECT SUM(p.quantity*pro.sellingprice) as total FROM sales s
                        LEFT JOIN product_in_sale p on s.sale_id=p.sale_id
                        LEFT JOIN products pro on pro.product_id = p.product_id
                        LEFT JOIN clients c on c.client_id=s.client_id 
                        WHERE s.user_id = {g.user.id} AND s.created_at >= DATE(NOW())
    """)
    day = mycursor.fetchone()[0]

    mycursor.execute(f"""
                        SELECT SUM(p.quantity*pro.sellingprice) as total FROM sales s
                        LEFT JOIN product_in_sale p on s.sale_id=p.sale_id
                        LEFT JOIN products pro on pro.product_id = p.product_id
                        LEFT JOIN clients c on c.client_id=s.client_id 
                        WHERE s.user_id = {g.user.id} AND s.created_at >= DATE(NOW()) - INTERVAL 7 DAY;
    """)
    week = mycursor.fetchone()[0]

    mycursor.execute(f"""
                        SELECT SUM(p.quantity*pro.sellingprice) as total FROM sales s
                        LEFT JOIN product_in_sale p on s.sale_id=p.sale_id
                        LEFT JOIN products pro on pro.product_id = p.product_id
                        LEFT JOIN clients c on c.client_id=s.client_id 
                        WHERE s.user_id = {g.user.id} AND s.created_at >= DATE(NOW()) - INTERVAL 30 DAY;
    """)
    month = mycursor.fetchone()[0]

    if request.method == 'POST':
        start = request.form.get('start')
        end = request.form.get('end')
        query = f"SELECT SUM(p.quantity*pro.sellingprice) as total FROM sales s LEFT JOIN product_in_sale p on s.sale_id=p.sale_id LEFT JOIN products pro on pro.product_id = p.product_id LEFT JOIN clients c on c.client_id=s.client_id WHERE s.user_id = {g.user.id} AND s.created_at >= '{start}' AND s.created_at <= '{end}';"
        print("🎄🎄🎄🎄🎄", query)
        mycursor.execute(query)
        custom = mycursor.fetchone()[0]
        print("CUSTOOOOOOOOOOOOOOOOOOM:", custom)
        return render_template('dashboard.html', day=day, week=week, month=month, custom=f"Las ventas de {start} a {end} son de {custom}$")

    else:
        return render_template('dashboard.html', day=day, week=week, month=month, custom="Las ventas de ####/##/## a ####/##/## son de XXX$")


@app.route('/account', methods=['POST', 'GET'])
def account():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    
    if request.method == 'POST':
        mycursor.execute(f"UPDATE users SET mail='{request.form.get('mail')}', image='{request.form.get('image')}' WHERE user_id = {g.user.id};")
        mydb.commit()
        mycursor.execute(f"UPDATE stores SET storename='{request.form.get('storename')}' WHERE store_id = {g.user.store_id};")
        mydb.commit()
        return redirect(url_for('account', modal='block'))
    else:
        mycursor.execute(f"SELECT mail FROM users where user_id like '{g.user.id}'")
        myresult = mycursor.fetchone()[0]
        print("------------------>", myresult)
        print(g.user)
        modal = request.args.get('modal', 'none')
        return render_template('account.html', modal=modal, email=myresult)

@app.route('/exit')
def exit():
    session.pop('user_id', None)
    return redirect('/')

@app.route('/products')
def products():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    print(g.user.id)
    mycursor.execute(f"SELECT * FROM products where user_id={g.user.id};")
    products = mycursor.fetchall()
    print("PRODUCTOS::::::::::::::::::::", products)
    modal = request.args.get('modal', 'none')
    alertmodal = request.args.get('alertmodal', 'none')
    return render_template('products.html', products=products, modal=modal, alertmodal=alertmodal)

@app.route('/products/public')
@app.route('/products/public/<user_id>')
def products_public(user_id=None):
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if user_id == None:
        return redirect(url_for('main'))
    mycursor.execute(f"SELECT * FROM products where user_id={user_id};")
    products = mycursor.fetchall()
    if products == []:
        return redirect(url_for('main'))
        
    mycursor.execute(f"SELECT s.storename FROM stores s LEFT JOIN users u ON u.user_id = s.user_id where u.user_id={user_id};")
    storename = mycursor.fetchall()[0][0]

    print("PRODUCTOS::::::::::::::::::::", products)
    modal = request.args.get('modal', 'none')
    alertmodal = request.args.get('alertmodal', 'none')
    return render_template('products_public.html', products=products, modal=modal, alertmodal=alertmodal, storename=storename)


@app.route('/products/new', methods=['POST', 'GET'])
def products_new():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    if request.method == 'POST':
        productname = request.form.get('productname')
        description = request.form.get('description')
        stock = request.form.get('stock')
        costprice = request.form.get('costprice')
        sellingprice = request.form.get('sellingprice')
        user_id = g.user.id
        image = request.form.get('image')

        query_insert_table = "INSERT INTO products (productname, description, stock, costprice, sellingprice, user_id, image) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        val = (productname, description, stock, costprice, sellingprice, user_id, image)
        mycursor.execute(query_insert_table, val)
        mydb.commit()
        return redirect(url_for('products', modal='block', alertmodal="none"))
    else:
        return render_template('products_new.html')

@app.route('/products/actions', methods=['POST'])
def products_actions():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    if request.method == 'POST':
        if request.form.get('action') == "edit":
            return render_template("products_edit.html", product_id=request.form.get('product_id'),
                                                        productname=request.form.get('productname'),
                                                        description=request.form.get('description'),
                                                        stock=request.form.get('stock'),
                                                        costprice=request.form.get('costprice'),
                                                        sellingprice=request.form.get('sellingprice'),
                                                        image=request.form.get('image'),
                                                        modal="none")
        elif request.form.get('action') == "update":
            print("updating...............")
            query = "UPDATE products SET productname=%s, description=%s, stock=%s, costprice=%s, sellingprice=%s, image=%s WHERE product_id = %s;"

            productname = request.form.get('productname')
            description = request.form.get('description')
            stock = request.form.get('stock')
            costprice = request.form.get('costprice')
            sellingprice = request.form.get('sellingprice')
            image = request.form.get('image')
            product_id = request.form.get('product_id')

            val = (productname, description, stock, costprice, sellingprice, image, product_id)
            mycursor.execute(query, val)
            mydb.commit()
            return render_template("products_edit.html", product_id=request.form.get('product_id'),
                                                        productname=request.form.get('productname'),
                                                        description=request.form.get('description'),
                                                        stock=request.form.get('stock'),
                                                        costprice=request.form.get('costprice'),
                                                        sellingprice=request.form.get('sellingprice'),
                                                        image=request.form.get('image'),
                                                        modal="block")
        elif request.form.get('action') == "delete":
            mycursor.execute(f"DELETE FROM products WHERE product_id = {request.form.get('product_id')};")
            mydb.commit()
            return redirect(url_for('products', modal='none', alertmodal="block"))


@app.route('/clients')
def clients():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    mycursor.execute(f"SELECT * FROM clients where user_id={g.user.id};")
    clients = mycursor.fetchall()
    modal = request.args.get('modal', 'none')
    alertmodal = request.args.get('alertmodal', 'none')
    return render_template('clients.html', clients=clients, modal=modal, alertmodal=alertmodal)

@app.route('/clients/actions', methods=['POST'])
def clients_actions():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    if request.method == 'POST':
        if request.form.get('action') == "edit":
            return render_template("clients_edit.html", client_id=request.form.get('client_id'),
                                                        clientname=request.form.get('clientname'),
                                                        mail=request.form.get('mail'),
                                                        phonenumber=request.form.get('phonenumber'),
                                                        address=request.form.get('address'),
                                                        modal="none")
        elif request.form.get('action') == "update":
            query = "UPDATE clients SET clientname=%s, mail=%s, address=%s, phonenumber=%s WHERE client_id = %s;"

            clientname = request.form.get('clientname')
            mail = request.form.get('mail')
            client_id = request.form.get('client_id')
            address = request.form.get('address')
            phonenumber = request.form.get('phonenumber')

            val = (clientname, mail, address, phonenumber, client_id)
            mycursor.execute(query, val)
            mydb.commit()
            return render_template("clients_edit.html", client_id=client_id,
                                                        clientname=clientname,
                                                        mail=mail,
                                                        address=address,
                                                        phonenumber=phonenumber,
                                                        modal="block")
        elif request.form.get('action') == "delete":
            mycursor.execute(f"DELETE FROM clients WHERE client_id = {request.form.get('client_id')};")
            mydb.commit()
            sale_id = mycursor.execute(f"SELECT sale_id FROM sales WHERE client_id = {request.form.get('client_id')};")
            mycursor.execute(f"DELETE FROM product_in_sale WHERE sale_id = {sale_id};")
            mydb.commit()
            mycursor.execute(f"DELETE FROM sales WHERE sale_id = {sale_id};")
            mydb.commit()
            return redirect(url_for('clients', modal='none', alertmodal="block"))

@app.route('/clients/new', methods=['POST', 'GET'])
def clients_new():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    if request.method == 'POST':
        clientname = request.form.get('clientname')
        mail = request.form.get('mail')
        address = request.form.get('address')
        phonenumber = request.form.get('phonenumber')
        query_insert_table = "INSERT INTO clients (clientname, mail, user_id, address, phonenumber) VALUES (%s, %s, %s, %s, %s)"
        val = (clientname, mail, g.user.id, address, phonenumber)
        mycursor.execute(query_insert_table, val)
        mydb.commit()
        return redirect(url_for('clients', modal='block', alertmodal="none"))
    else:
        return render_template('clients_new.html')


@app.route('/sales')
def sales():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    print(g.user.id)
    mycursor.execute(f"""
                    SELECT s.client_id, c.clientname, s.sale_id, s.salename, SUM(p.quantity*pro.sellingprice) as total FROM sales s
                    LEFT JOIN product_in_sale p on s.sale_id=p.sale_id
                    LEFT JOIN products pro on pro.product_id = p.product_id
                    LEFT JOIN clients c on c.client_id=s.client_id 
                    WHERE s.user_id = {g.user.id}
                    GROUP BY s.client_id, c.clientname, s.sale_id, s.salename;
    """)
    sales = mycursor.fetchall()
    print("PRODUCTOS::::::::::::::::::::", sales)
    modal = request.args.get('modal', 'none')
    alertmodal = request.args.get('alertmodal', 'none')
    return render_template('sales.html', sales=sales, modal=modal, alertmodal=alertmodal)

@app.route('/sales/new', methods=['POST', 'GET'])
def sales_new():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    if request.method == 'POST':
        products_id = request.form.getlist('products_id[]')
        quantity = request.form.getlist('quantity[]')
        client_id = request.form.get('client_id')
        salename = request.form.get('salename')

        query = "INSERT INTO sales (salename, user_id, client_id) VALUES (%s, %s, %s)"
        val = (salename, g.user.id, client_id)
        mycursor.execute(query, val)
        mydb.commit()
        sale_id = mycursor.lastrowid

        i = 0
        for product in products_id:
            query = "INSERT INTO product_in_sale (product_id, quantity, sale_id) VALUES (%s, %s, %s)"
            val = (product, quantity[i], sale_id)
            mycursor.execute(query, val)
            mydb.commit()
            i += 1
        
        i = 0
        for product in products_id:
            print(f"UPDATE products SET stock = stock - {quantity[i]} where product_id= {product}")
            mycursor.execute(f"UPDATE products SET stock = stock - {quantity[i]}")
            mydb.commit()
            
        return redirect(url_for('sales', modal='block', alertmodal="none"))
    else:
        mycursor.execute(f"SELECT client_id, clientname FROM clients WHERE user_id={g.user.id}")
        clients = mycursor.fetchall()
        mycursor.execute(f"SELECT product_id, productname, stock FROM products WHERE user_id={g.user.id} AND stock>0")
        products = mycursor.fetchall()
        print(products)
        return render_template('sales_new.html', products=products, clients=clients)

@app.route('/sales/actions', methods=['POST'])
def sales_actions():
    if connectet_to_db == False: return "<H1 style='font-family:Arial'>No se pudo conectar a la base de datos</H1> Verifique la conexión"
    if not g.user:
        return redirect(url_for('main'))
    if request.method == 'POST':
        if request.form.get('action') == "delete":
            sale_id = request.form.get('sale_id')
            mycursor.execute(f"DELETE FROM product_in_sale WHERE sale_id = {sale_id};")
            mydb.commit()
            mycursor.execute(f"DELETE FROM sales WHERE sale_id = {sale_id};")
            mydb.commit()
            return redirect(url_for('sales', modal='none', alertmodal="block"))

if __name__ == '__main__':
    app.run(debug=True,port=8000)