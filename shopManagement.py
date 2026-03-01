import tkinter as tk
from tkinter import *
from tkinter import messagebox
import mysql.connector
from datetime import datetime

# ---------------- DATABASE SETUP ---------------- #

def connect_db():
    return mysql.connector.connect(
        user="root",
        password="Keeki@041004",
        host="localhost",
        database="Shop"
    )

db = mysql.connector.connect(user="root",
                             password="Keeki@041004",
                             host="localhost")
cursor = db.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS Shop")
db.close()

db = connect_db()
cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS products(
    date VARCHAR(20),
    prodName VARCHAR(50) PRIMARY KEY,
    prodPrice INT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS sale(
    custName VARCHAR(50),
    date VARCHAR(20),
    prodName VARCHAR(50),
    qty INT,
    price INT
)
""")

db.commit()
db.close()

# ---------------- LOGIN SYSTEM ---------------- #

def login():
    username = user_entry.get()
    password = pass_entry.get()

    if username == "admin" and password == "1234":
        messagebox.showinfo("Login Success", "Welcome Admin")
        login_win.destroy()
        admin_panel()
    else:
        messagebox.showerror("Error", "Invalid Credentials")

def admin_login():
    global login_win, user_entry, pass_entry
    login_win = Toplevel()
    login_win.title("Admin Login")
    login_win.geometry("350x250")
    login_win.configure(bg="#d4f4dd")

    Label(login_win, text="Admin Login",
          font=("Arial", 16, "bold"),
          bg="#d4f4dd").pack(pady=10)

    Label(login_win, text="Username", bg="#d4f4dd").pack()
    user_entry = Entry(login_win)
    user_entry.pack()

    Label(login_win, text="Password", bg="#d4f4dd").pack()
    pass_entry = Entry(login_win, show="*")
    pass_entry.pack()

    Button(login_win, text="Login",
           bg="#27ae60", fg="white",
           command=login).pack(pady=15)

# ---------------- ADMIN FEATURES ---------------- #

def add_product():
    win = Toplevel()
    win.title("Add Product")
    win.configure(bg="#d4f4dd")

    Label(win, text="Add Product",
          font=("Arial", 14, "bold"),
          bg="#d4f4dd").pack(pady=10)

    Label(win, text="Date", bg="#d4f4dd").pack()
    date = Entry(win)
    date.pack()

    Label(win, text="Product Name", bg="#d4f4dd").pack()
    name = Entry(win)
    name.pack()

    Label(win, text="Price", bg="#d4f4dd").pack()
    price = Entry(win)
    price.pack()

    def save():
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO products VALUES(%s,%s,%s)",
                       (date.get(), name.get(), int(price.get())))
        db.commit()
        db.close()
        messagebox.showinfo("Success", "Product Added")
        win.destroy()

    Button(win, text="Save",
           bg="#2ecc71", fg="white",
           command=save).pack(pady=10)

def update_product():
    win = Toplevel()
    win.title("Update Product")
    win.configure(bg="#d4f4dd")

    Label(win, text="Update Product",
          font=("Arial", 14, "bold"),
          bg="#d4f4dd").pack(pady=10)

    Label(win, text="Product Name", bg="#d4f4dd").pack()
    name = Entry(win)
    name.pack()

    Label(win, text="New Price", bg="#d4f4dd").pack()
    price = Entry(win)
    price.pack()

    def update():
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("UPDATE products SET prodPrice=%s WHERE prodName=%s",
                       (int(price.get()), name.get()))
        db.commit()
        db.close()
        messagebox.showinfo("Success", "Product Updated")
        win.destroy()

    Button(win, text="Update",
           bg="#3498db", fg="white",
           command=update).pack(pady=10)

def search_product():
    win = Toplevel()
    win.title("Search Product")
    win.configure(bg="#d4f4dd")

    Label(win, text="Search Product",
          font=("Arial", 14, "bold"),
          bg="#d4f4dd").pack(pady=10)

    Label(win, text="Enter Product Name", bg="#d4f4dd").pack()
    name = Entry(win)
    name.pack()

    def search():
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM products WHERE prodName=%s",
                       (name.get(),))
        result = cursor.fetchone()
        db.close()

        if result:
            messagebox.showinfo("Found",
                                f"Date: {result[0]}\nPrice: ₹{result[2]}")
        else:
            messagebox.showerror("Not Found", "Product not found")

    Button(win, text="Search",
           bg="#8e44ad", fg="white",
           command=search).pack(pady=10)

# ---------------- BILLING + RECEIPT ---------------- #

def new_customer():
    win = Toplevel()
    win.title("Billing")
    win.configure(bg="#f9d5e5")

    Label(win, text="Billing",
          font=("Arial", 14, "bold"),
          bg="#f9d5e5").pack(pady=10)

    Label(win, text="Customer Name", bg="#f9d5e5").pack()
    cname = Entry(win)
    cname.pack()

    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    db.close()

    entries = []

    for item in products:
        frame = Frame(win, bg="#f9d5e5")
        frame.pack()

        Label(frame, text=f"{item[1]} - ₹{item[2]}",
              bg="#f9d5e5").pack(side=LEFT, padx=10)

        qty = Entry(frame, width=5)
        qty.pack(side=LEFT)
        entries.append((item, qty))

    def generate_bill():
        total = 0
        receipt_text = "------ SHOP RECEIPT ------\n"
        receipt_text += f"Customer: {cname.get()}\n"
        receipt_text += f"Date: {datetime.now()}\n\n"

        db = connect_db()
        cursor = db.cursor()

        for item, qty in entries:
            if qty.get() != "":
                quantity = int(qty.get())
                price = int(item[2])
                amount = quantity * price
                total += amount

                receipt_text += f"{item[1]} x {quantity} = ₹{amount}\n"

                cursor.execute(
                    "INSERT INTO sale VALUES(%s,%s,%s,%s,%s)",
                    (cname.get(), datetime.now(),
                     item[1], quantity, amount)
                )

        receipt_text += "\n--------------------------\n"
        receipt_text += f"Total: ₹{total}"

        db.commit()
        db.close()

        # Save receipt to file
        filename = f"receipt_{cname.get()}.txt"
        with open(filename, "w") as f:
            f.write(receipt_text)

        messagebox.showinfo("Receipt Generated",
                            f"Receipt saved as {filename}")

    Button(win, text="Generate Receipt",
           bg="#e74c3c", fg="white",
           command=generate_bill).pack(pady=15)

# ---------------- PANELS ---------------- #

def admin_panel():
    panel = Toplevel()
    panel.title("Admin Panel")
    panel.configure(bg="#d4f4dd")

    Label(panel, text="Admin Panel",
          font=("Arial", 16, "bold"),
          bg="#d4f4dd").pack(pady=10)

    Button(panel, text="Add Product",
           bg="#2ecc71", fg="white",
           width=20, command=add_product).pack(pady=5)

    Button(panel, text="Update Product",
           bg="#3498db", fg="white",
           width=20, command=update_product).pack(pady=5)

    Button(panel, text="Search Product",
           bg="#8e44ad", fg="white",
           width=20, command=search_product).pack(pady=5)

def user_panel():
    panel = Toplevel()
    panel.title("User Panel")
    panel.configure(bg="#f9d5e5")

    Label(panel, text="User Panel",
          font=("Arial", 16, "bold"),
          bg="#f9d5e5").pack(pady=10)

    Button(panel, text="New Customer",
           bg="#c0392b", fg="white",
           width=20, command=new_customer).pack(pady=15)

# ---------------- MAIN WINDOW ---------------- #

root = tk.Tk()
root.title("Shop Management System")
root.geometry("500x400")
root.configure(bg="#a8d8ea")

Label(root, text="Shop Management System",
      font=("Arial", 18, "bold"),
      bg="#a8d8ea").pack(pady=30)

Button(root, text="Admin Login",
       bg="#27ae60", fg="white",
       width=20, height=2,
       command=admin_login).pack(pady=15)

Button(root, text="User Panel",
       bg="#c0392b", fg="white",
       width=20, height=2,
       command=user_panel).pack(pady=15)

root.mainloop()
