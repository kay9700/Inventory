import tkinter as tk
from tkcalendar import Calendar, DateEntry
from dateutil.parser import parse
from tkinter import ttk
import mysql.connector
from datetime import date, datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#$import pandas as pd


dulce_std_price = 7
dulce_stores_price = 6
blanco_price = 5
telera_price = 7.5
torta_price = 5

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
        self.root.title("Data System")
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
        #self.filter_date_entry.delete(0, tk.END)
        self.filter_date_entry.pack(side=tk.LEFT, padx=(0, 10))


        tk.Button(filter_frame, text="Aplicar Filtro", command=self.apply_filters).pack(side=tk.LEFT, padx=(10, 0))
        tk.Button(filter_frame, text="Ver Todo", command=self.see_all).pack(side=tk.LEFT, padx=(10, 0))

        tk.Button(filter_frame, text="Gráfica", command=self.open_graph).pack(side=tk.RIGHT, padx=(10, 0))
        

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
        formatted_date = parse(selected_date)
        print("selected_date ------> ", selected_date)
        print("formatted_date ------> ", formatted_date)
        self.refresh_inventory(filter_name, formatted_date)
    
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

        query = "SELECT name, quantity, description, creation_date FROM products WHERE name LIKE %s OR (creation_date = %s) "

        filter_values = ('%' + filter_name + '%', filter_date)


        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(query, filter_values)

        for row in cursor:
            self.tree.insert('', tk.END, values=row)
        cursor.close()
        conn.close()

    def open_graph(self):
        print("abriendo gáficas")
        self.graph_window = tk.Toplevel(self.root)
        app = GraphApp(self.graph_window)


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph")
        self.root.geometry("800x600")

        # Filters Graph product frame
        filter_frame = tk.Frame(self.root)
        filter_frame.pack(fill=tk.X, padx=10, pady=5)

        #Filter Date
        tk.Label(filter_frame, text="Fecha Inicial:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_start_date_entry = DateEntry(filter_frame)
        self.filter_start_date_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Label(filter_frame, text="Fecha Final:").pack(side=tk.LEFT, padx=(0, 5))
        self.filter_end_date_entry = DateEntry(filter_frame)
        self.filter_end_date_entry.pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(filter_frame, text="Buscar", command=self.update_graph).pack(side=tk.RIGHT, padx=(10, 0))

        # Placeholder for the canvas (will be set in update_graph)
        self.graph_canvas = None

        # Initial graph update
        self.update_graph(self.root)

        ###############################################################

        # Filters Graph product frame
        graph_frame = tk.Frame(self.root)
        graph_frame.pack(fill=tk.X, padx=10, pady=5)

        

    def update_graph(self, graph_frame=None):
        start_date = self.filter_start_date_entry.get() if self.filter_start_date_entry else ""
        end_date = self.filter_end_date_entry.get() if self.filter_end_date_entry else ""
        
        #Fetch for data
        data = self.fetch_data_for_graph(parse(start_date), parse(end_date))
        names = [row[0] for row in data]
        quantities = [row[1] for row in data]

        # Create figure for plotting
        fig, ax = plt.subplots()
        ax.bar(names, quantities)

        # Add titles and labels
        ax.set_title('Inventory Quantity by Item')
        ax.set_xlabel('Item Name')
        ax.set_ylabel('Quantity')

        if self.graph_canvas:
            self.graph_canvas.get_tk_widget().destroy()

        # Embedding the matplotlib plot in the Tkinter window
        self.graph_canvas = FigureCanvasTkAgg(fig, master=graph_frame if graph_frame else self.graph_canvas.get_tk_widget().master)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def fetch_data_for_graph(self, filter_date_from="", filter_date_to=""):
        conn = create_connection()
        cursor = conn.cursor()
        query = "SELECT name, SUM(quantity) FROM products WHERE creation_date >= %s AND creation_date <= %s GROUP BY name"
        filter_values = (filter_date_from, filter_date_to)

        cursor.execute(query, filter_values)
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data


class FinancesApp:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Finances System")
        self.root.geometry("500x400")

        #Date entry
        date_entry_frame = tk.Frame(self.root)
        date_entry_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(date_entry_frame, text="Seleccionar Fecha:").pack(side=tk.LEFT, padx=(0, 5))
        self.date_entry_input = DateEntry(date_entry_frame)
        self.date_entry_input.pack(side=tk.LEFT, padx=(0, 10))

        #Current Data display
        display_current_data_frame = tk.Frame(self.root)
        display_current_data_frame.pack(fill=tk.X, padx=10, pady=5)


        self.stringTest = 120
        tk.Label(display_current_data_frame, text="Total pan hecho:", bg="#D7CDBD").pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(display_current_data_frame, text=self.stringTest).pack(side=tk.LEFT, padx=(0, 5))

        #Filter Name
        store_sold_frame = tk.Frame(self.root)
        store_sold_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(store_sold_frame, text="Tienda:").pack(side=tk.LEFT, padx=(0, 5))
        self.store_sold_input = tk.Entry(store_sold_frame)
        self.store_sold_input.pack(side=tk.LEFT, padx=15)

        #Filter Name
        spare_frame = tk.Frame(self.root)
        spare_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(spare_frame, text="Sobrante:").pack(side=tk.LEFT, padx=(0, 5))
        self.spare_input = tk.Entry(spare_frame)
        self.spare_input.pack(side=tk.LEFT, padx=2)

        #Filter Name
        home_frame = tk.Frame(self.root)
        home_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(home_frame, text="Casa:").pack(side=tk.LEFT, padx=(0, 5))
        self.home_input = tk.Entry(home_frame)
        self.home_input.pack(side=tk.LEFT, padx=24)

        #Button Get Results
        get_result_frame = tk.Frame(self.root)
        get_result_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Button(get_result_frame, text="Obtener", command=self.get_kpi).pack(side=tk.LEFT, padx=50)

        #Display Results Dulce
        display_result_frame = tk.Frame(self.root)
        display_result_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stringSoldTest = tk.StringVar(value="0")
        
        tk.Label(display_result_frame, text="Cantidad Vendida (Dulce): ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(display_result_frame, textvariable=self.stringSoldTest).pack(side=tk.LEFT, padx=(0, 5))

        self.resultString = tk.StringVar(value="0")
        
        tk.Label(display_result_frame, text="Result: ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        self.value_label = tk.Label(display_result_frame, textvariable=self.resultString).pack(side=tk.LEFT, padx=(0, 5))

        #Display Results Tiendas
        display_tiendas_result_frame = tk.Frame(self.root)
        display_tiendas_result_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stringTiendasSoldTest = tk.StringVar(value="0")
        
        tk.Label(display_tiendas_result_frame, text="Cantidad Vendida (Tiendas): ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(display_tiendas_result_frame, textvariable=self.stringTiendasSoldTest).pack(side=tk.LEFT, padx=(0, 5))

        self.resultTiendasString = tk.StringVar(value="0")
        
        tk.Label(display_tiendas_result_frame, text="Result: ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        self.value_label = tk.Label(display_tiendas_result_frame, textvariable=self.resultTiendasString).pack(side=tk.LEFT, padx=(0, 5))


        #Display Results Blanco
        display_blanco_result_frame = tk.Frame(self.root)
        display_blanco_result_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stringBlancoSoldTest = tk.StringVar(value="0")
        
        tk.Label(display_blanco_result_frame, text="Cantidad Vendida (Blanco): ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(display_blanco_result_frame, textvariable=self.stringBlancoSoldTest).pack(side=tk.LEFT, padx=(0, 5))

        self.resultBlancoString = tk.StringVar(value="0")
        
        tk.Label(display_blanco_result_frame, text="Result: ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        self.value_label = tk.Label(display_blanco_result_frame, textvariable=self.resultBlancoString).pack(side=tk.LEFT, padx=(0, 5))

        #Display Results Telera
        display_Telera_result_frame = tk.Frame(self.root)
        display_Telera_result_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stringTeleraSoldTest = tk.StringVar(value="0")
        
        tk.Label(display_Telera_result_frame, text="Cantidad Vendida (Telera): ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(display_Telera_result_frame, textvariable=self.stringTeleraSoldTest).pack(side=tk.LEFT, padx=(0, 5))

        self.resultTeleraString = tk.StringVar(value="0")
        
        tk.Label(display_Telera_result_frame, text="Result: ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        self.value_label = tk.Label(display_Telera_result_frame, textvariable=self.resultTeleraString).pack(side=tk.LEFT, padx=(0, 5))

        #Display Results Torta
        display_Torta_result_frame = tk.Frame(self.root)
        display_Torta_result_frame.pack(fill=tk.X, padx=10, pady=5)

        self.stringTortaSoldTest = tk.StringVar(value="0")
        
        tk.Label(display_Torta_result_frame, text="Cantidad Vendida (Torta): ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        tk.Label(display_Torta_result_frame, textvariable=self.stringTortaSoldTest).pack(side=tk.LEFT, padx=(0, 5))

        self.resultTortaString = tk.StringVar(value="0")
        
        tk.Label(display_Torta_result_frame, text="Result: ", bg="#33DB1B").pack(side=tk.LEFT, padx=(10, 5))
        self.value_label = tk.Label(display_Torta_result_frame, textvariable=self.resultTortaString).pack(side=tk.LEFT, padx=(0, 5))

        #self.get_kpi()

    def get_metrics(self):

        print("selected_date", parse(self.date_entry.get()))

        query = "SELECT name, quantity, description, creation_date FROM products WHERE creation_date = %s "

        filter_values = (parse(self.date_entry.get()),)

        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute(query, filter_values)

        for row in cursor:
            self.tree.insert('', tk.END, values=row)
        cursor.close()
        conn.close()

    def get_kpi(self):
        current = int(self.resultString.get())
        #self.resultString.set(str(current + 1))
        print(current)
        
        
        total_made = int(self.stringTest)
        stores = int(self.store_sold_input.get())
        spare = int(self.spare_input.get())
        home = int(self.home_input.get())
        dulce_total_sold = total_made - stores - spare - home
        dulce_total_sold_price = dulce_total_sold * dulce_std_price

        telera_total_sold = 53
        telera_total_sold_price = telera_total_sold * telera_price
        blanco_total_sold = 43
        blanco_total_sold_price = blanco_total_sold * blanco_price
        tienda_total_sold = 56
        tienda_total_sold_price = tienda_total_sold * dulce_stores_price
        torta_total_sold = 32
        torta_total_sold_price = torta_total_sold * torta_price

        self.stringSoldTest.set(str(dulce_total_sold))
        self.stringTeleraSoldTest.set(str(telera_total_sold))
        self.stringBlancoSoldTest.set(str(blanco_total_sold))
        self.stringTiendasSoldTest.set(str(tienda_total_sold))
        self.stringTortaSoldTest.set(str(torta_total_sold))

        self.resultString.set(str(dulce_total_sold_price))
        self.resultTeleraString.set(str(telera_total_sold_price))
        self.resultBlancoString.set(str(blanco_total_sold_price))
        self.resultTiendasString.set(str(tienda_total_sold_price))
        self.resultTortaString.set(str(torta_total_sold_price))
        
        #return dulce_total_sold

    def get_data_per_date(self):

        print("getting data from: ", self.date_entry_input)
        
""" dulce_std_price = 7
dulce_stores_price = 6
blanco_price = 5
telera_price = 7.5
torta_price = 5 """

    

if __name__ == "__main__":
    root = tk.Tk()
    initial_screen = InitialScreen(root)
    root.mainloop()
