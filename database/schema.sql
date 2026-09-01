-- ==============================================================================
-- Persistent AI Data Analyst: MySQL Database Schema
-- Database: business_analytics
-- Includes 11 normalized relational tables with full PK, FK, and Indexing
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS `business_analytics`
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE `business_analytics`;

-- Disable foreign key checks during schema rebuild
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `sales`;
DROP TABLE IF EXISTS `payments`;
DROP TABLE IF EXISTS `order_items`;
DROP TABLE IF EXISTS `orders`;
DROP TABLE IF EXISTS `inventory`;
DROP TABLE IF EXISTS `products`;
DROP TABLE IF EXISTS `employees`;
DROP TABLE IF EXISTS `suppliers`;
DROP TABLE IF EXISTS `customers`;
DROP TABLE IF EXISTS `categories`;
DROP TABLE IF EXISTS `regions`;

-- ------------------------------------------------------------------------------
-- 1. REGIONS
-- ------------------------------------------------------------------------------
CREATE TABLE `regions` (
    `region_id` INT AUTO_INCREMENT PRIMARY KEY,
    `region_name` VARCHAR(100) NOT NULL UNIQUE,
    `country` VARCHAR(100) NOT NULL DEFAULT 'India',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 2. CATEGORIES
-- ------------------------------------------------------------------------------
CREATE TABLE `categories` (
    `category_id` INT AUTO_INCREMENT PRIMARY KEY,
    `category_name` VARCHAR(100) NOT NULL UNIQUE,
    `description` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 3. SUPPLIERS
-- ------------------------------------------------------------------------------
CREATE TABLE `suppliers` (
    `supplier_id` INT AUTO_INCREMENT PRIMARY KEY,
    `supplier_name` VARCHAR(150) NOT NULL,
    `contact_name` VARCHAR(100),
    `email` VARCHAR(100),
    `phone` VARCHAR(30),
    `city` VARCHAR(100) NOT NULL,
    `region_id` INT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_suppliers_region` FOREIGN KEY (`region_id`)
        REFERENCES `regions` (`region_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 4. EMPLOYEES
-- ------------------------------------------------------------------------------
CREATE TABLE `employees` (
    `employee_id` INT AUTO_INCREMENT PRIMARY KEY,
    `first_name` VARCHAR(50) NOT NULL,
    `last_name` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `department` VARCHAR(50) NOT NULL,
    `role` VARCHAR(50) NOT NULL,
    `salary` DECIMAL(10, 2) NOT NULL,
    `hire_date` DATE NOT NULL,
    `region_id` INT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_employees_region` FOREIGN KEY (`region_id`)
        REFERENCES `regions` (`region_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 5. CUSTOMERS
-- ------------------------------------------------------------------------------
CREATE TABLE `customers` (
    `customer_id` INT AUTO_INCREMENT PRIMARY KEY,
    `first_name` VARCHAR(50) NOT NULL,
    `last_name` VARCHAR(50) NOT NULL,
    `email` VARCHAR(100),
    `phone` VARCHAR(30),
    `city` VARCHAR(100) NOT NULL,
    `state` VARCHAR(100) NOT NULL,
    `region_id` INT,
    `customer_segment` VARCHAR(50) NOT NULL DEFAULT 'Consumer',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_customers_region` FOREIGN KEY (`region_id`)
        REFERENCES `regions` (`region_id`) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX `idx_customers_city` (`city`),
    INDEX `idx_customers_segment` (`customer_segment`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 6. PRODUCTS
-- ------------------------------------------------------------------------------
CREATE TABLE `products` (
    `product_id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_name` VARCHAR(150) NOT NULL,
    `category_id` INT NOT NULL,
    `supplier_id` INT,
    `unit_price` DECIMAL(10, 2) NOT NULL,
    `cost_price` DECIMAL(10, 2) NOT NULL,
    `sku` VARCHAR(50) NOT NULL UNIQUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_products_category` FOREIGN KEY (`category_id`)
        REFERENCES `categories` (`category_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_products_supplier` FOREIGN KEY (`supplier_id`)
        REFERENCES `suppliers` (`supplier_id`) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX `idx_products_category` (`category_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 7. INVENTORY
-- ------------------------------------------------------------------------------
CREATE TABLE `inventory` (
    `inventory_id` INT AUTO_INCREMENT PRIMARY KEY,
    `product_id` INT NOT NULL,
    `warehouse_city` VARCHAR(100) NOT NULL,
    `stock_quantity` INT NOT NULL DEFAULT 0,
    `reorder_level` INT NOT NULL DEFAULT 20,
    `last_restocked_date` DATE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_inventory_product` FOREIGN KEY (`product_id`)
        REFERENCES `products` (`product_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_inventory_product` (`product_id`),
    INDEX `idx_inventory_city` (`warehouse_city`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 8. ORDERS
-- ------------------------------------------------------------------------------
CREATE TABLE `orders` (
    `order_id` INT AUTO_INCREMENT PRIMARY KEY,
    `customer_id` INT NOT NULL,
    `employee_id` INT,
    `order_date` DATE NOT NULL,
    `order_status` VARCHAR(50) NOT NULL DEFAULT 'Completed',
    `total_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `discount_amount` DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    `net_amount` DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    `shipping_city` VARCHAR(100) NOT NULL,
    `region_id` INT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_orders_customer` FOREIGN KEY (`customer_id`)
        REFERENCES `customers` (`customer_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_orders_employee` FOREIGN KEY (`employee_id`)
        REFERENCES `employees` (`employee_id`) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT `fk_orders_region` FOREIGN KEY (`region_id`)
        REFERENCES `regions` (`region_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX `idx_orders_date` (`order_date`),
    INDEX `idx_orders_status` (`order_status`),
    INDEX `idx_orders_city` (`shipping_city`),
    INDEX `idx_orders_region` (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 9. ORDER_ITEMS
-- ------------------------------------------------------------------------------
CREATE TABLE `order_items` (
    `order_item_id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `quantity` INT NOT NULL,
    `unit_price` DECIMAL(10, 2) NOT NULL,
    `discount_percent` DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    `total_price` DECIMAL(12, 2) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_order_items_order` FOREIGN KEY (`order_id`)
        REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_order_items_product` FOREIGN KEY (`product_id`)
        REFERENCES `products` (`product_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX `idx_order_items_order` (`order_id`),
    INDEX `idx_order_items_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 10. PAYMENTS
-- ------------------------------------------------------------------------------
CREATE TABLE `payments` (
    `payment_id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `payment_date` DATE NOT NULL,
    `payment_method` VARCHAR(50) NOT NULL,
    `amount` DECIMAL(12, 2) NOT NULL,
    `payment_status` VARCHAR(50) NOT NULL DEFAULT 'Success',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_payments_order` FOREIGN KEY (`order_id`)
        REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX `idx_payments_date` (`payment_date`),
    INDEX `idx_payments_method` (`payment_method`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 11. SALES (Reporting & Dimensional Summary Table)
-- ------------------------------------------------------------------------------
CREATE TABLE `sales` (
    `sale_id` INT AUTO_INCREMENT PRIMARY KEY,
    `order_id` INT NOT NULL,
    `product_id` INT NOT NULL,
    `customer_id` INT NOT NULL,
    `region_id` INT NOT NULL,
    `sale_date` DATE NOT NULL,
    `year` INT NOT NULL,
    `month` INT NOT NULL,
    `month_name` VARCHAR(20) NOT NULL,
    `quarter` VARCHAR(10) NOT NULL,
    `quantity` INT NOT NULL,
    `revenue` DECIMAL(12, 2) NOT NULL,
    `cost` DECIMAL(12, 2) NOT NULL,
    `profit` DECIMAL(12, 2) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_sales_order` FOREIGN KEY (`order_id`)
        REFERENCES `orders` (`order_id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_sales_product` FOREIGN KEY (`product_id`)
        REFERENCES `products` (`product_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_sales_customer` FOREIGN KEY (`customer_id`)
        REFERENCES `customers` (`customer_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT `fk_sales_region` FOREIGN KEY (`region_id`)
        REFERENCES `regions` (`region_id`) ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX `idx_sales_date` (`sale_date`),
    INDEX `idx_sales_year_month` (`year`, `month`),
    INDEX `idx_sales_product` (`product_id`),
    INDEX `idx_sales_region` (`region_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;
