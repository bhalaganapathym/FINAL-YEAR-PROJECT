"""
Seed Data Generator for Persistent AI Data Analyst.
Generates comprehensive synthetic dataset:
- 4 Regions (South, North, West, East)
- 6 Categories
- 10 Suppliers
- 15 Sales Employees
- 60 Customers across Chennai, Bangalore, Mumbai, Delhi, Hyderabad, Kolkata, Pune
- 30 Products
- 30 Inventory records
- 700+ Orders spanning 2022-01-01 to 2024-12-31 with realistic seasonal variations
- 1,800+ Order Items
- 700+ Payments
- 1,800+ Sales records
"""

import random
from datetime import date, timedelta
from pathlib import Path

# Seed for reproducible data generation
random.seed(42)

OUT_FILE = Path(__file__).resolve().parent / "seed.sql"

REGIONS = [
    (1, "South", "India"),
    (2, "North", "India"),
    (3, "West", "India"),
    (4, "East", "India"),
]

CATEGORIES = [
    (1, "Electronics", "Smartphones, Tablets, Smart Devices, Accessories"),
    (2, "Computers & Laptops", "Laptops, Desktops, Monitors, Keyboards"),
    (3, "Appliances", "Refrigerators, Microwaves, Air Conditioners, Washing Machines"),
    (4, "Furniture", "Ergonomic Chairs, Executive Desks, Standing Tables, Bookcases"),
    (5, "Office Supplies", "Stationery, Printers, Paper, Organizers"),
    (6, "Audio & Wearables", "Headphones, Smartwatches, Earbuds, Bluetooth Speakers"),
]

SUPPLIERS = [
    (1, "Apex Electronics Pvt Ltd", "Rajesh Sharma", "rajesh@apexelectronics.com", "+91-9876543210", "Bangalore", 1),
    (2, "Nordic Tech Supplies", "Anita Desai", "anita@nordictech.in", "+91-9876543211", "Delhi", 2),
    (3, "Western Digital Gear", "Vikram Patel", "vikram@westerndigitalgear.com", "+91-9876543212", "Mumbai", 3),
    (4, "Eastern Horizon Mart", "Subhash Roy", "subhash@easternhorizon.in", "+91-9876543213", "Kolkata", 4),
    (5, "Coromandel Appliance Hub", "Kavita Reddy", "kavita@coromandelhub.com", "+91-9876543214", "Chennai", 1),
    (6, "Deccan Smart Solutions", "Arun Varma", "arun@deccansmart.in", "+91-9876543215", "Hyderabad", 1),
    (7, "Maratha Office Logistics", "Pradeep Joshi", "pradeep@marathaoffice.com", "+91-9876543216", "Pune", 3),
    (8, "National Hardware Guild", "Manoj Singh", "manoj@nationalguild.in", "+91-9876543217", "Delhi", 2),
    (9, "Silversun Living Goods", "Deepa Nair", "deepa@silversun.com", "+91-9876543218", "Chennai", 1),
    (10, "Zenith Audio Innovations", "Rohan Mehta", "rohan@zenithaudio.in", "+91-9876543219", "Mumbai", 3),
]

EMPLOYEES = [
    (1, "Suresh", "Iyer", "suresh.iyer@company.com", "Sales", "Senior Sales Executive", 85000.00, "2021-03-15", 1),
    (2, "Priya", "Natarajan", "priya.natarajan@company.com", "Sales", "Key Account Manager", 92000.00, "2021-06-01", 1),
    (3, "Amit", "Kapoor", "amit.kapoor@company.com", "Sales", "Regional Sales Lead", 110000.00, "2020-11-10", 2),
    (4, "Neha", "Chawla", "neha.chawla@company.com", "Sales", "Sales Representative", 65000.00, "2022-02-18", 2),
    (5, "Rahul", "Deshmukh", "rahul.deshmukh@company.com", "Sales", "Territory Account Manager", 88000.00, "2021-01-20", 3),
    (6, "Sneha", "Kulkarni", "sneha.kulkarni@company.com", "Sales", "Sales Representative", 62000.00, "2022-05-12", 3),
    (7, "Anirban", "Banerjee", "anirban.b@company.com", "Sales", "Regional Sales Lead", 105000.00, "2021-08-05", 4),
    (8, "Pooja", "Sen", "pooja.sen@company.com", "Sales", "Sales Executive", 70000.00, "2022-09-01", 4),
    (9, "Karthik", "Rao", "karthik.rao@company.com", "Sales", "Enterprise Sales Lead", 125000.00, "2020-04-14", 1),
    (10, "Divya", "Menon", "divya.menon@company.com", "Sales", "Sales Representative", 64000.00, "2023-01-10", 1),
    (11, "Gaurav", "Malhotra", "gaurav.m@company.com", "Sales", "Sales Representative", 66000.00, "2023-03-01", 2),
    (12, "Tanvi", "Bhatia", "tanvi.bhatia@company.com", "Sales", "Sales Executive", 72000.00, "2022-11-15", 3),
    (13, "Arvind", "Sundaram", "arvind.s@company.com", "Operations", "Inventory Manager", 95000.00, "2020-02-01", 1),
    (14, "Meera", "Swaminathan", "meera.s@company.com", "Marketing", "Marketing Manager", 90000.00, "2021-07-15", 1),
    (15, "Vikas", "Gupta", "vikas.gupta@company.com", "Operations", "Logistics Coordinator", 78000.00, "2022-04-01", 2),
]

CITIES_DATA = [
    # (City, State, Region_id)
    ("Chennai", "Tamil Nadu", 1),
    ("Bangalore", "Karnataka", 1),
    ("Hyderabad", "Telangana", 1),
    ("Coimbatore", "Tamil Nadu", 1),
    ("Delhi", "Delhi NCR", 2),
    ("Noida", "Uttar Pradesh", 2),
    ("Gurgaon", "Haryana", 2),
    ("Chandigarh", "Punjab", 2),
    ("Mumbai", "Maharashtra", 3),
    ("Pune", "Maharashtra", 3),
    ("Ahmedabad", "Gujarat", 3),
    ("Surat", "Gujarat", 3),
    ("Kolkata", "West Bengal", 4),
    ("Bhubaneswar", "Odisha", 4),
    ("Patna", "Bihar", 4),
    ("Guwahati", "Assam", 4),
]

PRODUCTS = [
    # (id, name, cat_id, sup_id, unit_price, cost_price, sku)
    (1, "ProBook X15 Laptop 16GB", 2, 1, 68000.00, 52000.00, "LAP-PBX15-01"),
    (2, "UltraBook Air 13 8GB", 2, 1, 55000.00, 42000.00, "LAP-UBA13-02"),
    (3, "Workstation Tower Z80", 2, 3, 95000.00, 74000.00, "DESK-WZ80-03"),
    (4, "4K UHD Gaming Monitor 27-inch", 2, 3, 26000.00, 19500.00, "MON-4K27-04"),
    (5, "Wireless Ergonomic Keyboard & Mouse", 2, 3, 3500.00, 2200.00, "ACC-WEKM-05"),
    (6, "Galaxy Nova Pro Smartphone 256GB", 1, 1, 48000.00, 36000.00, "PHN-GNP256-06"),
    (7, "Galaxy Nova Lite Smartphone 128GB", 1, 1, 24000.00, 18000.00, "PHN-GNL128-07"),
    (8, "SwiftTab 11-inch Tablet", 1, 1, 32000.00, 24000.00, "TAB-ST11-08"),
    (9, "FastCharge 65W GaN Multi-Port Hub", 1, 6, 2800.00, 1600.00, "ACC-FC65-09"),
    (10, "Smart Surge Protector & Power Tower", 1, 6, 2200.00, 1300.00, "ACC-SSPT-10"),
    (11, "FrostFree Double Door Refrigerator 340L", 3, 5, 38000.00, 29000.00, "APP-FFR340-11"),
    (12, "Inverter Split Air Conditioner 1.5 Ton", 3, 5, 42000.00, 32000.00, "APP-ISAC15-12"),
    (13, "Front Load Smart Washing Machine 8kg", 3, 5, 34000.00, 26000.00, "APP-FLWM8-13"),
    (14, "Convection Microwave Oven 28L", 3, 5, 14500.00, 10500.00, "APP-CMO28-14"),
    (15, "Air Purifier with HEPA Filter Pro", 3, 2, 12000.00, 8500.00, "APP-APHP-15"),
    (16, "ErgoSpine High-Back Mesh Office Chair", 4, 9, 14000.00, 9500.00, "FUR-ESHC-16"),
    (17, "Solid Oak Executive Desk 6ft", 4, 9, 28000.00, 19000.00, "FUR-SOED-17"),
    (18, "Motorized Dual-Motor Standing Desk", 4, 9, 32000.00, 22000.00, "FUR-MDS-18"),
    (19, "Modular 4-Shelf Storage Bookcase", 4, 7, 8500.00, 5600.00, "FUR-MSB-19"),
    (20, "Mobile 3-Drawer Under-Desk Pedestal", 4, 7, 5200.00, 3400.00, "FUR-MUDP-20"),
    (21, "LaserJet Enterprise Multifunction Printer", 5, 8, 28500.00, 21000.00, "OFC-LEMP-21"),
    (22, "High-Yield Toner Cartridge Black Pack", 5, 8, 4200.00, 2800.00, "OFC-HYTC-22"),
    (23, "Premium Executive Bond Paper A4 (5 Reams)", 5, 8, 1600.00, 1050.00, "OFC-PEBP-23"),
    (24, "Electric Heavy-Duty Paper Shredder", 5, 8, 7500.00, 4800.00, "OFC-EHPS-24"),
    (25, "All-in-One Desk Organizer & Wireless Station", 5, 7, 1800.00, 1100.00, "OFC-AIOD-25"),
    (26, "Zenith QuietComfort ANC Headphones", 6, 10, 16500.00, 11500.00, "AUD-ZQCH-26"),
    (27, "Zenith True Wireless Studio Earbuds", 6, 10, 6800.00, 4600.00, "AUD-ZTWE-27"),
    (28, "Rugged Outdoor 360 Bluetooth Speaker", 6, 10, 5200.00, 3400.00, "AUD-ROBS-28"),
    (29, "PulseFit GPS Smartwatch & Heart Monitor", 6, 10, 9800.00, 6500.00, "AUD-PFGW-29"),
    (30, "Studio Condenser USB Microphone & Stand", 6, 10, 7200.00, 4800.00, "AUD-SCUM-30"),
]

FIRST_NAMES = [
    "Aarav", "Aditi", "Ajay", "Akash", "Ananya", "Anand", "Archana", "Ashok",
    "Bhavna", "Chethan", "Deepak", "Devi", "Girish", "Harish", "Isha", "Jayant",
    "Kiran", "Lakshmi", "Madhav", "Manish", "Naveen", "Nisha", "Pallavi", "Pawan",
    "Radha", "Rajiv", "Rakesh", "Rekha", "Sanjay", "Santosh", "Shilpa", "Shruti",
    "Siddharth", "Sumit", "Swati", "Tarun", "Uma", "Varun", "Venkat", "Vidya",
    "Vijay", "Vineet", "Yamini", "Yash", "Zainab", "Abhishek", "Kavya", "Manas",
    "Pranav", "Ritu", "Rohit", "Sameer", "Tanvi", "Umesh", "Vasudha", "Vimal"
]

LAST_NAMES = [
    "Nair", "Sharma", "Menon", "Reddy", "Patel", "Rao", "Gupta", "Deshmukh",
    "Mukherjee", "Chatterjee", "Bose", "Joshi", "Bhat", "Kulkarni", "Pillai",
    "Subramanian", "Sundaram", "Choudhury", "Verma", "Malhotra", "Kapoor",
    "Aggarwal", "Shetty", "Gowda", "Hegde", "Puri", "Sinha", "Mishra", "Pandey"
]

SEGMENTS = ["Consumer", "Corporate", "Small Business"]
PAYMENT_METHODS = ["UPI", "Credit Card", "Net Banking", "Debit Card", "Cash on Delivery"]


def generate():
    lines = []
    lines.append("-- ==============================================================================")
    lines.append("-- Persistent AI Data Analyst: Seed Data (2022 - 2024 Realistic Dataset)")
    lines.append("-- Database: business_analytics")
    lines.append("-- ==============================================================================\n")
    lines.append("USE `business_analytics`;\n")
    lines.append("SET FOREIGN_KEY_CHECKS = 0;\n")

    # 1. Regions
    lines.append("-- 1. Regions")
    lines.append("INSERT INTO `regions` (`region_id`, `region_name`, `country`) VALUES")
    reg_rows = [f"({r[0]}, '{r[1]}', '{r[2]}')" for r in REGIONS]
    lines.append(",\n".join(reg_rows) + ";\n")

    # 2. Categories
    lines.append("-- 2. Categories")
    lines.append("INSERT INTO `categories` (`category_id`, `category_name`, `description`) VALUES")
    cat_rows = [f"({c[0]}, '{c[1]}', '{c[2]}')" for c in CATEGORIES]
    lines.append(",\n".join(cat_rows) + ";\n")

    # 3. Suppliers
    lines.append("-- 3. Suppliers")
    lines.append("INSERT INTO `suppliers` (`supplier_id`, `supplier_name`, `contact_name`, `email`, `phone`, `city`, `region_id`) VALUES")
    sup_rows = [f"({s[0]}, '{s[1]}', '{s[2]}', '{s[3]}', '{s[4]}', '{s[5]}', {s[6]})" for s in SUPPLIERS]
    lines.append(",\n".join(sup_rows) + ";\n")

    # 4. Employees
    lines.append("-- 4. Employees")
    lines.append("INSERT INTO `employees` (`employee_id`, `first_name`, `last_name`, `email`, `department`, `role`, `salary`, `hire_date`, `region_id`) VALUES")
    emp_rows = [f"({e[0]}, '{e[1]}', '{e[2]}', '{e[3]}', '{e[4]}', '{e[5]}', {e[6]}, '{e[7]}', {e[8]})" for e in EMPLOYEES]
    lines.append(",\n".join(emp_rows) + ";\n")

    # 5. Customers (60 realistic customers)
    lines.append("-- 5. Customers")
    lines.append("INSERT INTO `customers` (`customer_id`, `first_name`, `last_name`, `email`, `phone`, `city`, `state`, `region_id`, `customer_segment`) VALUES")
    cust_rows = []
    customer_list = []
    for cid in range(1, 61):
        fn = FIRST_NAMES[cid % len(FIRST_NAMES)]
        ln = LAST_NAMES[cid % len(LAST_NAMES)]
        city_info = CITIES_DATA[cid % len(CITIES_DATA)]
        seg = SEGMENTS[cid % len(SEGMENTS)]
        email = f"{fn.lower()}.{ln.lower()}{cid}@example.com"
        phone = f"+91-{random.randint(9000000000, 9999999999)}"
        cust_rows.append(f"({cid}, '{fn}', '{ln}', '{email}', '{phone}', '{city_info[0]}', '{city_info[1]}', {city_info[2]}, '{seg}')")
        customer_list.append((cid, city_info[0], city_info[2]))
    lines.append(",\n".join(cust_rows) + ";\n")

    # 6. Products
    lines.append("-- 6. Products")
    lines.append("INSERT INTO `products` (`product_id`, `product_name`, `category_id`, `supplier_id`, `unit_price`, `cost_price`, `sku`) VALUES")
    prod_rows = [f"({p[0]}, '{p[1]}', {p[2]}, {p[3]}, {p[4]}, {p[5]}, '{p[6]}')" for p in PRODUCTS]
    lines.append(",\n".join(prod_rows) + ";\n")

    # 7. Inventory
    lines.append("-- 7. Inventory")
    lines.append("INSERT INTO `inventory` (`inventory_id`, `product_id`, `warehouse_city`, `stock_quantity`, `reorder_level`, `last_restocked_date`) VALUES")
    inv_rows = []
    for i, p in enumerate(PRODUCTS, 1):
        wh_city = random.choice(["Chennai", "Bangalore", "Mumbai", "Delhi", "Kolkata", "Hyderabad"])
        stock = random.randint(40, 300)
        reorder = random.randint(15, 35)
        lines_date = f"2024-{random.randint(10, 12):02d}-{random.randint(1, 28):02d}"
        inv_rows.append(f"({i}, {p[0]}, '{wh_city}', {stock}, {reorder}, '{lines_date}')")
    lines.append(",\n".join(inv_rows) + ";\n")

    # 8. Orders, Order Items, Payments, and Sales spanning 2022 to 2024
    # Monthly base order counts with strong seasonality:
    # Q1 (Jan-Mar): lower (15-20 orders/mo)
    # Q2 (Apr-Jun): moderate (18-24 orders/mo)
    # Q3 (Jul-Sep): growing (20-28 orders/mo)
    # Q4 (Oct-Dec): peak festive season (30-45 orders/mo)
    # Year-over-Year growth: 2022 (base), 2023 (+15%), 2024 (+25%)

    orders_sql = []
    order_items_sql = []
    payments_sql = []
    sales_sql = []

    order_id_counter = 1
    order_item_id_counter = 1
    sale_id_counter = 1

    months_info = [
        (1, "January", "Q1", 16),
        (2, "February", "Q1", 15),
        (3, "March", "Q1", 18),
        (4, "April", "Q2", 20),
        (5, "May", "Q2", 22),
        (6, "June", "Q2", 21),
        (7, "July", "Q3", 24),
        (8, "August", "Q3", 26),
        (9, "September", "Q3", 28),
        (10, "October", "Q4", 38),   # Diwali / Festival rush
        (11, "November", "Q4", 44),  # Peak shopping
        (12, "December", "Q4", 42),  # Year-end closing
    ]

    sales_employees = [e[0] for e in EMPLOYEES if e[4] == "Sales"]

    for year in [2022, 2023, 2024]:
        growth_multiplier = 1.0 if year == 2022 else (1.18 if year == 2023 else 1.38)

        for m_num, m_name, quarter, base_count in months_info:
            num_orders = int(base_count * growth_multiplier)

            for _ in range(num_orders):
                day = random.randint(1, 28)
                order_date_str = f"{year}-{m_num:02d}-{day:02d}"

                cust_id, cust_city, reg_id = random.choice(customer_list)
                emp_id = random.choice(sales_employees)
                status = random.choices(["Completed", "Shipped", "Delivered"], weights=[70, 20, 10])[0]

                # 1 to 4 items per order
                num_items = random.choices([1, 2, 3, 4], weights=[45, 35, 15, 5])[0]
                selected_prods = random.sample(PRODUCTS, num_items)

                order_gross = 0.0
                order_items_temp = []

                for prod in selected_prods:
                    p_id, p_name, p_cat, p_sup, unit_price, cost_price, p_sku = prod
                    qty = random.choices([1, 2, 3, 5], weights=[60, 25, 10, 5])[0]
                    disc_pct = random.choice([0.00, 5.00, 10.00, 15.00])
                    item_total = round(float(unit_price) * qty * (1 - disc_pct / 100.0), 2)
                    item_cost = round(float(cost_price) * qty, 2)
                    item_profit = round(item_total - item_cost, 2)

                    order_gross += item_total
                    order_items_temp.append((
                        order_item_id_counter,
                        order_id_counter,
                        p_id,
                        qty,
                        unit_price,
                        disc_pct,
                        item_total,
                        item_cost,
                        item_profit
                    ))
                    order_item_id_counter += 1

                discount_amount = round(random.choice([0.0, 100.0, 250.0, 500.0]) if order_gross > 20000 else 0.0, 2)
                net_amount = max(round(order_gross - discount_amount, 2), 0.0)

                orders_sql.append(
                    f"({order_id_counter}, {cust_id}, {emp_id}, '{order_date_str}', '{status}', "
                    f"{order_gross:.2f}, {discount_amount:.2f}, {net_amount:.2f}, '{cust_city}', {reg_id})"
                )

                for item in order_items_temp:
                    oi_id, o_id, p_id, qty, u_price, d_pct, tot_price, cost_val, profit_val = item
                    order_items_sql.append(
                        f"({oi_id}, {o_id}, {p_id}, {qty}, {u_price:.2f}, {d_pct:.2f}, {tot_price:.2f})"
                    )

                    sales_sql.append(
                        f"({sale_id_counter}, {o_id}, {p_id}, {cust_id}, {reg_id}, '{order_date_str}', "
                        f"{year}, {m_num}, '{m_name}', '{quarter}', {qty}, {tot_price:.2f}, {cost_val:.2f}, {profit_val:.2f})"
                    )
                    sale_id_counter += 1

                # Payment
                pay_method = random.choice(PAYMENT_METHODS)
                payments_sql.append(
                    f"({order_id_counter}, {order_id_counter}, '{order_date_str}', '{pay_method}', {net_amount:.2f}, 'Success')"
                )

                order_id_counter += 1

    # Format chunks for SQL inserts
    lines.append("-- 8. Orders")
    lines.append("INSERT INTO `orders` (`order_id`, `customer_id`, `employee_id`, `order_date`, `order_status`, `total_amount`, `discount_amount`, `net_amount`, `shipping_city`, `region_id`) VALUES")
    lines.append(",\n".join(orders_sql) + ";\n")

    lines.append("-- 9. Order Items")
    lines.append("INSERT INTO `order_items` (`order_item_id`, `order_id`, `product_id`, `quantity`, `unit_price`, `discount_percent`, `total_price`) VALUES")
    lines.append(",\n".join(order_items_sql) + ";\n")

    lines.append("-- 10. Payments")
    lines.append("INSERT INTO `payments` (`payment_id`, `order_id`, `payment_date`, `payment_method`, `amount`, `payment_status`) VALUES")
    lines.append(",\n".join(payments_sql) + ";\n")

    lines.append("-- 11. Sales (Analytical Aggregate Summary Table)")
    lines.append("INSERT INTO `sales` (`sale_id`, `order_id`, `product_id`, `customer_id`, `region_id`, `sale_date`, `year`, `month`, `month_name`, `quarter`, `quantity`, `revenue`, `cost`, `profit`) VALUES")
    lines.append(",\n".join(sales_sql) + ";\n")

    lines.append("SET FOREIGN_KEY_CHECKS = 1;\n")

    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Successfully generated seed.sql with {len(orders_sql)} orders and {len(sales_sql)} sales records at: {OUT_FILE}")


if __name__ == "__main__":
    generate()
