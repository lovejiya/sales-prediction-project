/*CREATE DATABASE sales_db;

CREATE TABLE stores(store_id INT, store_type TEXT, assortment TEXT, competition_distance FLOAT);

CREATE TABLE sales_data(store_id INT, date DATE, sales FLOAT, promo INT, state_holiday TEXT, school_holiday TEXT);

CREATE TABLE predictions(id SERIAL , store_id INT, date DATE, predicted_sales FLOAT);*/
SELECT current_database();
SELECT COUNT(*) FROM sales_data;
SELECT COUNT(*) FROM stores;
