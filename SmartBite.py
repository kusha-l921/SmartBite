import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QMessageBox, QWidget, QComboBox, QListWidget
)
from PyQt5.QtCore import Qt

# Utility functions for CSV operations
def save_to_csv(filename, data, mode='a'):
    with open(filename, mode, newline='') as file:
        writer = csv.writer(file)
        writer.writerow(data)

def read_from_csv(filename):
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        return list(reader)

class LoginSignupWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login or Signup")
        self.setGeometry(100, 100, 300, 250)
        
        self.email_field = QLineEdit(self)
        self.email_field.setPlaceholderText("Enter Email")
        
        self.password_field = QLineEdit(self)
        self.password_field.setPlaceholderText("Enter Password")
        self.password_field.setEchoMode(QLineEdit.Password)

        self.toggle_password_button = QPushButton("Show Password", self)
        self.toggle_password_button.setCheckable(True)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        
        self.login_button = QPushButton("Login", self)
        self.login_button.clicked.connect(self.login)
        
        self.signup_button = QPushButton("Sign Up", self)
        self.signup_button.clicked.connect(self.signup)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Email:"))
        layout.addWidget(self.email_field)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(self.password_field)
        layout.addWidget(self.toggle_password_button)
        layout.addWidget(self.login_button)
        layout.addWidget(self.signup_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.credentials_file = "credentials.csv"
        self.order_history_file = "order_history.csv"
        self.current_user = None
    
    def toggle_password_visibility(self):
        if self.toggle_password_button.isChecked():
            self.password_field.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setText("Hide Password")
        else:
            self.password_field.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setText("Show Password")
    
    def login(self):
        email = self.email_field.text()
        password = self.password_field.text()
        credentials = read_from_csv(self.credentials_file)
        
        for record in credentials:
            if record[0] == email and record[1] == password:
                self.current_user = email
                self.open_menu()
                return
        
        QMessageBox.warning(self, "Login Failed", "Invalid email or password.")
    
    def signup(self):
        email = self.email_field.text()
        password = self.password_field.text()
        
        if not email or not password:
            QMessageBox.warning(self, "Signup Failed", "Email and Password cannot be empty.")
            return
        
        credentials = read_from_csv(self.credentials_file)
        for record in credentials:
            if record[0] == email:
                QMessageBox.warning(self, "Signup Failed", "Email already exists.")
                return
        
        save_to_csv(self.credentials_file, [email, password])
        QMessageBox.information(self, "Signup Successful", "Account created successfully.")
    
    def open_menu(self):
        self.menu_window = MenuWindow(self.current_user, self.order_history_file)
        self.menu_window.show()
        self.close()

class MenuWindow(QMainWindow):
    def __init__(self, user, order_history_file):
        super().__init__()
        self.setWindowTitle("Food Menu")
        self.setGeometry(100, 100, 400, 400)
        
        self.user = user
        self.order_history_file = order_history_file
        self.selected_items = []
        self.total_price = 0.0  # Track total price of the order
        
        # Dictionary to store items with their prices
        self.items_with_prices = {
            "Burger": [("Cheeseburger", 5.0), ("Veggie Burger", 4.5), ("Chicken Burger", 6.0)],
            "Pizza": [("Mushroom Pizza", 8.0), ("Pepperoni Pizza", 9.0), ("Chicken Pizza", 10.0)],
            "Fries": [("Regular Fries", 2.5), ("Cheese Fries", 3.0), ("Curly Fries", 3.5)],
            "Beverage": [("Cola", 1.5), ("Sprite", 1.5), ("Water", 1.0)]
        }
        
        self.category_combo = QComboBox(self)
        self.category_combo.addItems(self.items_with_prices.keys())
        self.category_combo.currentTextChanged.connect(self.update_items)
        
        self.items_combo = QComboBox(self)
        
        self.add_button = QPushButton("Add to Order", self)
        self.add_button.clicked.connect(self.add_item)
        
        self.remove_button = QPushButton("Remove Selected Item", self)
        self.remove_button.clicked.connect(self.remove_item)
        
        self.order_list = QListWidget(self)
        
        self.total_label = QLabel(f"Total: $0.00", self)  # Display total price
        
        self.complete_order_button = QPushButton("Complete Order", self)
        self.complete_order_button.clicked.connect(self.complete_order)
        
        self.view_history_button = QPushButton("View Order History", self)
        self.view_history_button.clicked.connect(self.view_order_history)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"Welcome, {self.user}!"))
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_combo)
        layout.addWidget(QLabel("Items:"))
        layout.addWidget(self.items_combo)
        layout.addWidget(self.add_button)
        layout.addWidget(self.remove_button)  # Added the Remove button
        layout.addWidget(QLabel("Order Summary:"))
        layout.addWidget(self.order_list)
        layout.addWidget(self.total_label)
        layout.addWidget(self.complete_order_button)
        layout.addWidget(self.view_history_button)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        
        self.update_items()
    
    def update_items(self):
        category = self.category_combo.currentText()
        items = self.items_with_prices[category]
        self.items_combo.clear()
        for item, price in items:
            self.items_combo.addItem(f"{item} - ${price:.2f}", (item, price))
    
    def add_item(self):
        item_data = self.items_combo.currentData()  
        if item_data:
            item, price = item_data
            self.selected_items.append((item, price))
            self.total_price += price
            self.order_list.addItem(f"{item} - ${price:.2f}")
            self.total_label.setText(f"Total: ${self.total_price:.2f}")
    
    def remove_item(self):
        selected_item = self.order_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            for item, price in self.selected_items:
                if f"{item} - ${price:.2f}" == item_text:
                    self.selected_items.remove((item, price))
                    self.total_price -= price
                    break
            self.order_list.takeItem(self.order_list.row(selected_item))
            self.total_label.setText(f"Total: ${self.total_price:.2f}")
    
    def complete_order(self):
        if not self.selected_items:
            QMessageBox.warning(self, "Order Error", "No items selected.")
            return
        
        order_summary = ", ".join([item[0] for item in self.selected_items])
        save_to_csv(self.order_history_file, [self.user, order_summary, f"${self.total_price:.2f}"])
        QMessageBox.information(self, "Order Complete", f"Your order has been placed.\nTotal: ${self.total_price:.2f}")
        
       
        self.selected_items.clear()
        self.total_price = 0.0
        self.order_list.clear()
        self.total_label.setText(f"Total: $0.00")
    
    def view_order_history(self):
        try:
            orders = read_from_csv(self.order_history_file)
            user_orders = [f"{order[1]} - Total: {order[2]}" for order in orders if order[0] == self.user]
            
            if not user_orders:
                QMessageBox.information(self, "Order History", "No previous orders found.")
                return
            
            history = "\n".join(user_orders)
            QMessageBox.information(self, "Order History", f"Your previous orders:\n{history}")
        except FileNotFoundError:
             QMessageBox.information(self, "Order History", "No order history available.")


app = QApplication(sys.argv)

for file in ["credentials.csv", "order_history.csv"]:
    with open(file, 'a') as f:
        pass

window = LoginSignupWindow()
window.show()

sys.exit(app.exec_())