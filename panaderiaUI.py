import tkinter as tk
from tkcalendar import Calendar, DateEntry
from dateutil.parser import parse
from tkinter import ttk
import mysql.connector
from datetime import date, datetime
#$import pandas as pd

# Assuming create_connection, add_product, record_sale, and display_inventory functions are defined here (from previous steps)

def create_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin1234",
            database="inventario_panaderia"
        )
        print("Connected to Database")
        return conn
    except mysql.connector.Error as e:
        print(f"Error: {e}")

def add_product(name, quantity, description, creation_date):
    conn = create_connection()
    cursor = conn.cursor()
    query = "INSERT INTO products (name, quantity, description, creation_date) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, quantity, description, creation_date))
    conn.commit()
    cursor.close()
    conn.close()

def record_sale(product_id, quantity_sold):
    """Records a sale."""
    conn = create_connection()
    cursor = conn.cursor()
    # Update product quantity
    update_query = "UPDATE products SET quantity = quantity - %s WHERE product_id = %s"
    cursor.execute(update_query, (quantity_sold, product_id))
    # Insert sale record
    sale_query = "INSERT INTO sales (product_id, quantity_sold, sale_date) VALUES (%s, %s, %s)"
    cursor.execute(sale_query, (product_id, quantity_sold, date.today()))
    conn.commit()
    cursor.close()
    conn.close()

def display_inventory():
    """Displays the current inventory."""
    conn = create_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM products"
    cursor.execute(query)
    for (product_id, name, quantity, description) in cursor:
        print(f"ID: {product_id}, Name: {name}, Quantity: {quantity}, Description: {description}")
    cursor.close()
    conn.close()

class InitialScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("LA VENCEDORA")
        self.root.geometry("300x320")

        tk.Label(self.root, text="Bienvenido al sistema de inventario de La Vencedora", padx=10, pady=20).pack()

        self.launch_button = tk.Button(self.root, text="Administrar Inventario", command=self.open_inventory)
        self.launch_button.pack(pady=15)

        self.launch_button = tk.Button(self.root, text="Abrir Data", command=self.open_see_data)
        self.launch_button.pack(pady=15)

        self.launch_button = tk.Button(self.root, text="Abrir Finanzas", command=self.open_finances)
        self.launch_button.pack(pady=15)

        
    def open_inventory(self):
        self.inventory_window = tk.Toplevel(self.root)
        app = InventoryApp(self.inventory_window)

    def open_see_data(self):
        self.data_window = tk.Toplevel(self.root)
        app = DataApp(self.data_window)

    def open_finances(self):
        self.finances_window = tk.Toplevel(self.root)
        app = FinancesApp(self.finances_window)

class InventoryApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("1200x800")
        self.sort_direction = True  # True for ascending, False for descending


        # Add product frame
        add_product_frame = tk.Frame(self.root)
        add_product_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(add_product_frame, text="Nombre:").pack(side=tk.LEFT, padx=(0, 5))
        self.name_entry = tk.Entry(add_product_frame)
        self.name_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(add_product_frame, text="Cantidad:").pack(side=tk.LEFT, padx=(0, 5))
        self.quantity_entry = tk.Entry(add_product_frame)
        self.quantity_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(add_product_frame, text="Descripción:").pack(side=tk.LEFT, padx=(0, 5))
        self.description_entry = tk.Entry(add_product_frame)
        self.description_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(add_product_frame, text="Fecha:").pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry = DateEntry(add_product_frame)
        self.date_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(add_product_frame, text="Añadir al inventario", command=self.add_product).pack(side=tk.LEFT, padx=(10, 0))

        # Display inventory
        self.tree = ttk.Treeview(self.root, columns=("Name", "Quantity", "Description", "CreationDate"), show='headings')
        self.tree.heading("Name", text="Name", command=lambda: self.treeview_sort_column("Name", False))
        self.tree.heading("Quantity", text="Quantity", command=lambda: self.treeview_sort_column("Quantity", True))
        self.tree.heading("CreationDate", text="Fecha de Creación", command=lambda: self.treeview_sort_column("CreationDate", False))
        self.tree.heading("Description", text="Description", command=lambda: self.treeview_sort_column("Description", False))

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_inventory()


    def treeview_sort_column(self, col, is_numeric_sort=False):
        """Sort treeview contents when a column header is clicked."""
        # Retrieve all items from the treeview
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        # Sort the list in ascending or descending order
        l.sort(reverse=self.sort_direction, key=lambda t: int(t[0]) if is_numeric_sort else t[0])

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # Reverse the sort direction for the next sort operation
        self.sort_direction = not self.sort_direction

    def add_product(self):
        name = self.name_entry.get()
        quantity = self.quantity_entry.get()
        description = self.description_entry.get()
        selected_date = self.date_entry.get()
        formatted_date = parse(selected_date)
        add_product(name, int(quantity), description, formatted_date)
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.refresh_inventory()

    def refresh_inventory(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = create_connection()
        cursor = conn.cursor()
        query = "SELECT name, quantity, description, creation_date FROM products"
        cursor.execute(query)
        for row in cursor:
            self.tree.insert('', tk.END, values=row)
        cursor.close()
        conn.close()


class DataApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventory Management System")
        self.root.geometry("800x600")
        self.sort_direction = True  # True for ascending, False for descending

        # Frame for filter entries
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        #Filter Name
        tk.Label(filter_frame, text="Filtrar por Nombre:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_name_entry = tk.Entry(filter_frame)
        self.filter_name_entry.pack(side=tk.LEFT, padx=(0, 10))
        #tk.Button(filter_frame, text="Aplicar Filtro", command=self.apply_filters).pack(side=tk.LEFT, padx=(10, 0))

        #Filter Date
        tk.Label(filter_frame, text="Filtrar por Fecha:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_date_entry = DateEntry(filter_frame)
        self.filter_date_entry.delete(0, tk.END)
        self.filter_date_entry.pack(side=tk.LEFT, padx=(0, 10))


        tk.Button(filter_frame, text="Aplicar Filtro", command=self.apply_filters).pack(side=tk.LEFT, padx=(10, 0))
        tk.Button(filter_frame, text="Ver Todo", command=self.see_all).pack(side=tk.LEFT, padx=(10, 0))

        

        self.tree = ttk.Treeview(self.root, columns=("Name", "Quantity", "Description", "CreationDate"), show='headings')
        self.tree.heading("Name", text="Nombre", command=lambda: self.treeview_sort_column("Name", False))
        self.tree.heading("Quantity", text="Cantidad", command=lambda: self.treeview_sort_column("Quantity", True))
        self.tree.heading("CreationDate", text="Fecha de Creación", command=lambda: self.treeview_sort_column("CreationDate", False))
        self.tree.heading("Description", text="Descripción", command=lambda: self.treeview_sort_column("Description", False))

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_inventory()


    def treeview_sort_column(self, col, is_numeric_sort=False):
        """Sort treeview contents when a column header is clicked."""
        # Retrieve all items from the treeview
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        # Sort the list in ascending or descending order
        l.sort(reverse=self.sort_direction, key=lambda t: int(t[0]) if is_numeric_sort else t[0])

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # Reverse the sort direction for the next sort operation
        self.sort_direction = not self.sort_direction

    def apply_filters(self):
        filter_name = self.filter_name_entry.get()
        selected_date = self.filter_date_entry.get()
        if selected_date != '':
            formatted_date = parse(selected_date)
            print('formatted_date 1 ', formatted_date)
        else: 
            formatted_date = date.today()
            print('formatted_date 2 ', formatted_date)
        print("filter_name =======> " , filter_name)
        print("formatted_date =======> " , formatted_date.strftime('%Y-%m-%d'))
        if filter_name != '' and selected_date != '':
            print('filter_name != '' and selected_date != ') 
            self.refresh_inventory(filter_name, formatted_date.strftime('%Y-%m-%d'))
        if filter_name == '' and selected_date != '':
            print('filter_name == '' and selected_date != ' ' ---------') 
            self.refresh_inventory("", filter_name)
        if filter_name != '' and selected_date == '':
            print('filter_name != '' and selected_date == '':') 
            self.refresh_inventory(filter_name)
    
    def see_all(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT name, quantity, description, creation_date FROM products "
        cursor.execute(query)

        self.filter_name_entry.delete(0, tk.END)
        self.filter_date_entry.delete(0, tk.END)

        for row in cursor:
            self.tree.insert('', tk.END, values=row)
        cursor.close()
        conn.close()

    def refresh_inventory(self, filter_name="", filter_date=""):
        # Clear the treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = create_connection()
        cursor = conn.cursor()

        query = "SELECT name, quantity, description, creation_date FROM products WHERE "
        #cursor.execute(query,  ('%' + filter_name + '%', filter_date))

        
        if(filter_name != "" and filter_date == "") :
            print('1')
            query = query + "(name LIKE %s) "
            cursor.execute(query, ('%' + filter_name + '%',))
        if (filter_date != "" and filter_name == ""):
            print('2')
            query = query + "(creation_date = %s)"
            cursor.execute(query, (filter_date, ))
        if(filter_date != "" and filter_name != ""):
            print('3')
            query = query + "(name LIKE %s) AND (creation_date = %s)"
            print("QUERY =======> " , query)
            cursor.execute(query, ('%' + filter_name + '%', filter_date))

        """ query = "SELECT name, quantity, description, creation_date FROM products WHERE (name LIKE %s) "
        if(filter_date != ""):
            query = query + " OR (creation_date = %s)" 
        cursor.execute(query, ('%' + filter_name + '%', filter_date))"""

        """
        if filter_name != '':
            query = "SELECT name, quantity, description, creation_date FROM products WHERE name LIKE %s"
            cursor.execute(query, ('%' + filter_name + '%',))
         if filter_date != '':
            query = "SELECT name, quantity, description, creation_date FROM products WHERE creation_date = %s"
            cursor.execute(query, (filter_date ,)) """
        #query = "SELECT name, quantity, description FROM products WHERE name LIKE %s"
        #cursor.execute(query, ('%' + filter_name + '%',))
        #cursor.execute(query, (filter_name ,))
        for row in cursor:
            self.tree.insert('', tk.END, values=row)
        cursor.close()
        conn.close()

class FinancesApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Finances System")
        self.root.geometry("800x600")

        # Add product frame
        add_product_frame = tk.Frame(self.root)
        add_product_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(add_product_frame, text="Nombre:").pack(side=tk.LEFT, padx=(0, 5))
        self.name_entry = tk.Entry(add_product_frame)
        self.name_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(add_product_frame, text="Cantidad:").pack(side=tk.LEFT, padx=(0, 5))
        self.quantity_entry = tk.Entry(add_product_frame)
        self.quantity_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(add_product_frame, text="Descripción:").pack(side=tk.LEFT, padx=(0, 5))
        self.description_entry = tk.Entry(add_product_frame)
        self.description_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(add_product_frame, text="Añadir al inventario", command=self.add_product).pack(side=tk.LEFT, padx=(10, 0))

        # Display inventory
        self.tree = ttk.Treeview(self.root, columns=("Name", "Quantity", "Description", "CreationDate"), show='headings')
        self.tree.heading("Name", text="Nombre")
        self.tree.heading("Quantity", text="Cantidad")
        self.tree.heading("Description", text="Descripción")
        self.tree.heading("CreationDate", text="Fecha de Creación")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.refresh_inventory()


if __name__ == "__main__":
    root = tk.Tk()
    initial_screen = InitialScreen(root)
    root.mainloop()
