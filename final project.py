import re
import mysql.connector
from mysql.connector import Error

def connect_db():
    """Establishes connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",      # Change to your MySQL username
            password="1234",  # Change to your MySQL password
            database="stadium_booking"
        )
        return connection
    except Error as e:
        print(f"Database Connection Error: {e}")
        return None

def book_ticket():
    """Books a new ticket and saves it to the database."""
    conn = connect_db()
    if not conn:
        return
        
    cursor = conn.cursor()
    print("\n--- Book a Ticket ---")
    customer_name = input("Enter Customer Name: ").strip()
    match_name = input("Enter Match Name: ").strip()
    seat_number = input("Enter Seat Number (A1-A10, B1-B10, C1-C10, D1-D10, F1-F10): ").strip().upper()
    
    # Validates seats from A1-A10, B1-B10, C1-C10, D1-D10, F1-F10
    if not re.match(r"^[ABCDF]([1-9]|10)$", seat_number):
        print("No such seats available. Booking canceled.")
        cursor.close()
        conn.close()
        return

    print("Ticket Types: 1. VIP (₹150) | 2. Premium (₹90) | 3. Standard (₹40)")
    type_choice = input("Select Ticket Type (1-3): ").strip()
    
    types = {"1": ("VIP", 150.00), "2": ("Premium", 90.00), "3": ("Standard", 40.00)}
    if type_choice not in types:
        print("Invalid choice. Booking canceled.")
        cursor.close()
        conn.close()
        return
        
    ticket_type, price = types[type_choice]
    
    try:
        query = """INSERT INTO tickets (customer_name, match_name, seat_number, ticket_type, price) 
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (customer_name, match_name, seat_number, ticket_type, price))
        conn.commit()
        print(f"Success! Ticket successfully booked for {customer_name} at seat {seat_number}.")
    except Error as e:
        if e.errno == 1062:  # Duplicate entry error code for unique seat_number
            print(f"Error: Seat {seat_number} is already booked!")
        else:
            print(f"Error booking ticket: {e}")
    finally:
        cursor.close()
        conn.close()

def view_tickets():
    """Displays all booked tickets."""
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    query = "SELECT ticket_id, customer_name, match_name, seat_number, ticket_type, price FROM tickets"
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        if not records:
            print("\nNo tickets booked yet.")
            return
            
        print(f"\n{'ID':<5} | {'Customer':<20} | {'Match':<20} | {'Seat':<6} | {'Type':<10} | {'Price':<8}")
        print("-" * 78)
        for row in records:
            print(f"{row[0]:<5} | {row[1]:<20} | {row[2]:<20} | {row[3]:<6} | {row[4]:<10} | ₹{row[5]:<7}")
    except Error as e:
        print(f"Error fetching tickets: {e}")
    finally:
        cursor.close()
        conn.close()

def cancel_ticket():
    """Cancels/removes a ticket by its ID."""
    conn = connect_db()
    if not conn:
        return
    cursor = conn.cursor()
    print("\n--- Cancel a Ticket ---")
    try:
        ticket_id = int(input("Enter Ticket ID to cancel: "))
        # Check if ticket exists
        cursor.execute("SELECT * FROM tickets WHERE ticket_id = %s", (ticket_id,))
        if not cursor.fetchone():
            print("Ticket ID not found.")
            return
            
        query = "DELETE FROM tickets WHERE ticket_id = %s"
        cursor.execute(query, (ticket_id,))
        conn.commit()
        print(f"Ticket ID {ticket_id} has been successfully canceled.")
    except ValueError:
        print("Invalid input. Please enter a numerical ID.")
    except Error as e:
        print(f"Error canceling ticket: {e}")
    finally:
        cursor.close()
        conn.close()

def main_menu():
    """Application control loop."""
    while True:
        print("\n==============================")
        print(" STADIUM TICKET MANAGER SYSTEM")
        print("==============================")
        print("1. Book a Ticket")
        print("2. View All Booked Tickets")
        print("3. Cancel a Ticket")
        print("4. Exit")
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            book_ticket()
        elif choice == "2":
            view_tickets()
        elif choice == "3":
            cancel_ticket()
        elif choice == "4":
            print("Thank you for coming! Please visit again.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main_menu()
