import mysql.connector
from datetime import date

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

def add_product(name, quantity, description, baked_date):
    conn = create_connection()
    cursor = conn.cursor()
    query = "INSERT INTO products (name, quantity, description, baked_date) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (name, quantity, description, baked_date))
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
    for (product_id, name, quantity, description, baked_date) in cursor:
        print(f"ID: {product_id}, 
              Name: {name}, 
              Quantity: {quantity}, 
              Description: {description}, 
              Baked Date: {date.today()}")
    cursor.close()
    conn.close()

# Example usage
if __name__ == "__main__":
    add_product("Conchas", 25, "Conchas de vainilla, fresa y chocolate", date.today() )
    record_sale(2, 5)
    display_inventory()