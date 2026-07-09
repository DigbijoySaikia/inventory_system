from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QDialog, QFormLayout, QLineEdit, 
    QSpinBox, QDoubleSpinBox, QMessageBox
)
from PySide6.QtCore import Qt
import sqlite3
from database import get_connection

class ItemDialog(QDialog):
    def __init__(self, parent=None, title="Item Form", name="", category="", quantity=0, price=0.0, edit_mode=False):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(300, 200)
        
        layout = QFormLayout(self)
        
        self.name_input = QLineEdit(self)
        self.name_input.setText(name)
        if edit_mode:
            self.name_input.setReadOnly(True)
            
        self.category_input = QLineEdit(self)
        self.category_input.setText(category)
        
        self.quantity_input = QSpinBox(self)
        self.quantity_input.setRange(0, 1000000)
        self.quantity_input.setValue(quantity)
        
        self.price_input = QDoubleSpinBox(self)
        self.price_input.setRange(0.0, 1000000.0)
        self.price_input.setDecimals(2)
        self.price_input.setValue(price)
        
        layout.addRow("Item Name:", self.name_input)
        layout.addRow("Category:", self.category_input)
        layout.addRow("Quantity:", self.quantity_input)
        layout.addRow("Price ($):", self.price_input)
        
        self.submit_btn = QPushButton("Save", self)
        self.submit_btn.setObjectName("addButton")
        self.submit_btn.clicked.connect(self.accept)
        layout.addRow(self.submit_btn)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "category": self.category_input.text().strip(),
            "quantity": self.quantity_input.value(),
            "price": self.price_input.value()
        }


class InventoryDashboard(QWidget):
    def __init__(self, user_id, logout_callback):
        super().__init__()
        self.user_id = user_id
        self.logout_callback = logout_callback
        self.init_ui()
        self.load_data()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        
        header_layout = QHBoxLayout()
        title = QLabel("📦 Inventory Management Dashboard")
        title.setObjectName("dashboardTitle")
        
        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("logoutBtn")
        logout_btn.clicked.connect(self.logout_callback)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(logout_btn)
        main_layout.addLayout(header_layout)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.add_btn = QPushButton("➕ Add New Item")
        self.add_btn.setObjectName("addButton")
        
        self.edit_btn = QPushButton("✏️ Edit Stock / Price")
        self.edit_btn.setObjectName("editButton")
        
        self.sell_btn = QPushButton("💰 Sell / Deduct Item")
        self.sell_btn.setObjectName("sellButton")
        
        self.delete_btn = QPushButton("🗑️ Delete Item")
        self.delete_btn.setObjectName("deleteButton")
        
        self.refresh_btn = QPushButton("🔄 Refresh Table")
        self.refresh_btn.setObjectName("refreshButton")
        
        for btn in [self.add_btn, self.edit_btn, self.sell_btn, self.delete_btn, self.refresh_btn]:
            btn_layout.addWidget(btn)
            
        main_layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Item Name", "Category", "Quantity", "Price ($)", "Total Value ($)"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.table)
        
        self.add_btn.clicked.connect(self.handle_add)
        self.edit_btn.clicked.connect(self.handle_edit)
        self.sell_btn.clicked.connect(self.handle_sell)
        self.delete_btn.clicked.connect(self.handle_delete)
        self.refresh_btn.clicked.connect(self.load_data)

    def load_data(self):
        self.table.setRowCount(0)
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, category, quantity, price FROM inventory WHERE user_id = ?", (self.user_id,))
        rows = cursor.fetchall()
        conn.close()
        
        for row_idx, row_data in enumerate(rows):
            self.table.insertRow(row_idx)
            qty = row_data[3]
            price = row_data[4]
            total_value = qty * price
            
            for col_idx, data in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
                
            self.table.setItem(row_idx, 5, QTableWidgetItem(f"{total_value:.2f}"))

    def handle_add(self):
        dialog = ItemDialog(self, title="Add New Item")
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["name"] or not data["category"]:
                QMessageBox.warning(self, "Validation Error", "All fields are required.")
                return
            
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO inventory (user_id, name, category, quantity, price) VALUES (?, ?, ?, ?, ?)",
                    (self.user_id, data["name"], data["category"], data["quantity"], data["price"])
                )
                conn.commit()
                self.load_data()
            except sqlite3.IntegrityError:
                QMessageBox.critical(self, "Error", "An item with this name already exists in your inventory.")
            finally:
                conn.close()

    def handle_edit(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select a row to edit.")
            return
            
        name = self.table.item(selected_row, 1).text()
        category = self.table.item(selected_row, 2).text()
        quantity = int(self.table.item(selected_row, 3).text())
        price = float(self.table.item(selected_row, 4).text())
        
        dialog = ItemDialog(self, title="Edit Item Data", name=name, category=category, quantity=quantity, price=price, edit_mode=True)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE inventory SET category=?, quantity=?, price=? WHERE name=? AND user_id=?",
                (data["category"], data["quantity"], data["price"], name, self.user_id)
            )
            conn.commit()
            conn.close()
            self.load_data()

    def handle_sell(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select an item to sell.")
            return
            
        name = self.table.item(selected_row, 1).text()
        current_qty = int(self.table.item(selected_row, 3).text())
        
        sell_dialog = QDialog(self)
        sell_dialog.setWindowTitle("Process Sale")
        layout = QFormLayout(sell_dialog)
        spin_box = QSpinBox()
        spin_box.setRange(1, current_qty if current_qty > 0 else 1)
        
        layout.addRow(f"Quantity to sell (Available: {current_qty}):", spin_box)
        submit = QPushButton("Deduct Stock")
        submit.clicked.connect(sell_dialog.accept)
        layout.addRow(submit)
        
        if current_qty <= 0:
            QMessageBox.critical(self, "Out of Stock", "This item has no units left to sell.")
            return

        if sell_dialog.exec() == QDialog.Accepted:
            deduct_amount = spin_box.value()
            new_qty = current_qty - deduct_amount
            
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE inventory SET quantity=? WHERE name=? AND user_id=?", (new_qty, name, self.user_id))
            conn.commit()
            conn.close()
            self.load_data()
            QMessageBox.information(self, "Success", f"Successfully processed sale of {deduct_amount} units.")

    def handle_delete(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Selection Error", "Please select an item to delete.")
            return
            
        name = self.table.item(selected_row, 1).text()
        
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to permanently delete '{name}' from your inventory?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE name=? AND user_id=?", (name, self.user_id))
            conn.commit()
            conn.close()
            self.load_data()
            QMessageBox.information(self, "Success", f"Successfully deleted '{name}'.")