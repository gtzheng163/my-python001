# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from datetime import datetime
import pymysql
import logging

class ProductAnalysisPipeline:
    data_list = []
    def __init__(self, host, port, user, password, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            port=crawler.settings.get('MYSQL_PORT'),
            user=crawler.settings.get('MYSQL_USERNAME'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            db=crawler.settings.get('MYSQL_DB')
        )
    def open_spider(self, spider):
        self.conn = pymysql.connect(host=self.host,
                                    port=self.port,
                                    user=self.user,
                                    password=self.password,
                                    db=self.db,
                                    charset='utf8mb4')
        self.cur = self.conn.cursor()
        logging.info(f"Connected to mysql: {self.conn.host} on port: {self.conn.port}, using db: {self.conn.db}, "
                     f"charset is: {self.conn.charset}")
    def close_spider(self, spider):
        self.insert_data(self.data_list)
        self.cur.close()
        self.conn.close()
        logging.info("DB connection closed.")
    def process_item(self, item, spider):
        if len(self.data_list) == 10:
            self.insert_data(self.data_list)
            self.data_list = []
        else:
            product_name = item['product_name']
            user_name = item['user_name']
            user_comment = item['user_comment']
            create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.data_list.append([product_name, user_name, user_comment, create_time])
        return item
    def insert_data(self, data_list):
        logging.debug(f"Will insert following data: {data_list}")
        try:
            sql = """
            INSERT INTO product(product_name, user_name, user_comment, create_time)
            VALUES (%s, %s, %s, %s)"""
            self.cur.executemany(sql, data_list)
            self.conn.commit()
            logging.info(f"Inserted {len(data_list)} comments to DB.")
        except Exception as e:
            self.conn.rollback()
            logging.error("Insertion fail!")
            logging.error(e)
if __name__ == '__main__':
    data_list = [['怡泉 Schweppes 无糖零卡 苏打水 汽水饮料400ml*12瓶 整箱装 可口可乐公司出品+凑单品', '值友3032196445', '我也是??！！！！ ', '2020-08-30 21:12:50']]
    conn = pymysql.connect(host='127.0.0.1',
                           port=3306,
                           user='root',
                           password='MySQL666!',
                           db='db1')
    cur = conn.cursor()
    for data in data_list:
        product_name, user_name, user_comment, create_time = data
        sql = f"""
                        INSERT INTO product(product_name, user_name, user_comment, create_time)
                        VALUES ('{product_name}', '{user_name}', '{user_comment}', '{create_time}')
                        ON DUPLICATE KEY UPDATE create_time = '{create_time}'"""
        cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()

