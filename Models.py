import uuid
import os
import numpy as np
from mysql.connector import Error
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, send_file,flash, make_response, after_this_request
from datetime import datetime, timedelta
import pandas as pd
from xhtml2pdf import pisa
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import matplotlib.pyplot as plt
import seaborn as sns
import psycopg2
from psycopg2 import sql
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.styles import PatternFill, Font
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import io
import base64
import json
import requests
import pdfkit
from weasyprint import HTML
import re
import time
import random


app = Flask(__name__)
app.secret_key = 'your_secret_key'  
app.secret_key = '011235'
app.permanent_session_lifetime = timedelta(minutes=30)
user_sessions = {}

external_database_url = "postgresql://treasuryx_user:EmjnMPmqoRPtvRwSH3uZOhW1vHf7KVKE@dpg-d3aigt2dbo4c738s91r0-a.oregon-postgres.render.com/treasuryx"
database = 'treasuryx'

conn = psycopg2.connect(external_database_url)
cursor = conn.cursor()

'''
data_zwg = {
    "Tenor": ["<1m", "1m-2m", "2m-3m", "3m-6m", "6m-9m", "9m-12m", "1y-2y", "2y-3y", "3y-5y", "+5y"],
    "Normal Curve Bid Rate": [10.00, 11.00, 12.00, 12.00, 12.00, 12.00, 13.94, 15.45, 18.47, 17.47],
    "Normal Curve Liquidity Premium": [2.00]*10,
    "Normal Curve Offer Rate": [12.00, 13.00, 14.00, 14.00, 14.00, 14.00, 15.94, 17.45, 20.47, 19.47],
    "Treasury Curve Bid Rate": [16.00, 11.00, 11.00, 11.00, 11.00, 11.00, 7.00, 5.00, 5.00, 5.00],
    "Treasury Curve Liquidity Premium": [2.00]*10,
    "Treasury Curve Offer Rate": [18.00, 13.00, 13.00, 13.00, 13.00, 13.00, 9.00, 7.00, 7.00, 7.00],
}

df_zwg = pd.DataFrame(data_zwg)

data_usd = {
    "Tenor": ["<1m", "1m-2m", "2m-3m", "3m-6m", "6m-9m", "9m-12m", "1y-2y", "2y-3y", "3y-5y", "+5y"],
    "Normal Curve Bid Rate": [8.00, 9.00, 10.00, 11.00, 11.00, 11.00, 14.39, 17.11, 22.55, 22.55],
    "Normal Curve Liquidity Premium": [1.15]*10,
    "Normal Curve Offer Rate": [9.15, 10.15, 11.15, 12.15, 12.15, 12.15, 15.54, 18.26, 23.70, 23.70],
    "Treasury Curve Bid Rate": [2.88, 3.59, 2.76, 5.30, 4.25, 3.19, 4.37, 4.86, 4.86, 4.86],
    "Treasury Curve Liquidity Premium": [1.15]*10,
    "Treasury Curve Offer Rate": [4.03, 4.74, 3.91, 6.45, 5.40, 4.34, 5.52, 6.01, 6.01, 6.01],
    "Lines of Credit Curve Bid Rate": [9.22, 9.22, 9.22, 9.22, 9.22, 9.22, 9.83, 9.97, 10.85, 10.85],
    "Lines of Credit Curve Liquidity Premium": [1.15]*10,
    "Lines of Credit Curve Offer Rate": [10.37, 10.37, 10.37, 10.37, 10.37, 10.37, 10.98, 11.12, 12.00, 12.00],
}

df_usd = pd.DataFrame(data_usd)


try:

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "ZWG FTP Yield Curve" (
            Tenor VARCHAR(10) PRIMARY KEY,
            Normal_Curve_Bid_Rate NUMERIC,
            Normal_Curve_Liquidity_Premium NUMERIC,
            Normal_Curve_Offer_Rate NUMERIC,
            Treasury_Curve_Bid_Rate NUMERIC,
            Treasury_Curve_Liquidity_Premium NUMERIC,
            Treasury_Curve_Offer_Rate NUMERIC
        );
    """)
    conn.commit()

    # Insert rows (on conflict, update values)
    for _, row in df_zwg.iterrows():
        cursor.execute("""
            INSERT INTO "ZWG FTP Yield Curve" 
            (Tenor, Normal_Curve_Bid_Rate, Normal_Curve_Liquidity_Premium, Normal_Curve_Offer_Rate, 
             Treasury_Curve_Bid_Rate, Treasury_Curve_Liquidity_Premium, Treasury_Curve_Offer_Rate)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (Tenor) DO UPDATE SET
                Normal_Curve_Bid_Rate = EXCLUDED.Normal_Curve_Bid_Rate,
                Normal_Curve_Liquidity_Premium = EXCLUDED.Normal_Curve_Liquidity_Premium,
                Normal_Curve_Offer_Rate = EXCLUDED.Normal_Curve_Offer_Rate,
                Treasury_Curve_Bid_Rate = EXCLUDED.Treasury_Curve_Bid_Rate,
                Treasury_Curve_Liquidity_Premium = EXCLUDED.Treasury_Curve_Liquidity_Premium,
                Treasury_Curve_Offer_Rate = EXCLUDED.Treasury_Curve_Offer_Rate;
        """, tuple(row))

    conn.commit()
    print("✅ Data inserted/updated into 'ZWG FTP Yield Curve' successfully!")



    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "USD FTP Yield Curve" (
            Tenor VARCHAR(10) PRIMARY KEY,
            Normal_Curve_Bid_Rate NUMERIC,
            Normal_Curve_Liquidity_Premium NUMERIC,
            Normal_Curve_Offer_Rate NUMERIC,
            Treasury_Curve_Bid_Rate NUMERIC,
            Treasury_Curve_Liquidity_Premium NUMERIC,
            Treasury_Curve_Offer_Rate NUMERIC,
            Lines_of_Credit_Curve_Bid_Rate NUMERIC,
            Lines_of_Credit_Curve_Liquidity_Premium NUMERIC,
            Lines_of_Credit_Curve_Offer_Rate NUMERIC
        );
    """)

    conn.commit()


    # Insert rows (upsert)
    for _, row in df_usd.iterrows():
        cursor.execute("""
            INSERT INTO "USD FTP Yield Curve" 
            (Tenor, Normal_Curve_Bid_Rate, Normal_Curve_Liquidity_Premium, Normal_Curve_Offer_Rate,
             Treasury_Curve_Bid_Rate, Treasury_Curve_Liquidity_Premium, Treasury_Curve_Offer_Rate,
             Lines_of_Credit_Curve_Bid_Rate, Lines_of_Credit_Curve_Liquidity_Premium, Lines_of_Credit_Curve_Offer_Rate)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (Tenor) DO UPDATE SET
                Normal_Curve_Bid_Rate = EXCLUDED.Normal_Curve_Bid_Rate,
                Normal_Curve_Liquidity_Premium = EXCLUDED.Normal_Curve_Liquidity_Premium,
                Normal_Curve_Offer_Rate = EXCLUDED.Normal_Curve_Offer_Rate,
                Treasury_Curve_Bid_Rate = EXCLUDED.Treasury_Curve_Bid_Rate,
                Treasury_Curve_Liquidity_Premium = EXCLUDED.Treasury_Curve_Liquidity_Premium,
                Treasury_Curve_Offer_Rate = EXCLUDED.Treasury_Curve_Offer_Rate,
                Lines_of_Credit_Curve_Bid_Rate = EXCLUDED.Lines_of_Credit_Curve_Bid_Rate,
                Lines_of_Credit_Curve_Liquidity_Premium = EXCLUDED.Lines_of_Credit_Curve_Liquidity_Premium,
                Lines_of_Credit_Curve_Offer_Rate = EXCLUDED.Lines_of_Credit_Curve_Offer_Rate;
        """, tuple(row))

    conn.commit()
    print("✅ Data inserted/updated into 'USD FTP Yield Curve' successfully!")

except Exception as e:
    print("❌ Error:", e)'''

@app.route('/')
def landingpage():

    def fetch_table(table_name):
        """Fetch table into pandas DataFrame"""
        conn = psycopg2.connect(external_database_url)
        query = f'SELECT * FROM "{table_name}" ORDER BY Tenor;'
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    zwg_df = fetch_table("ZWG FTP Yield Curve")
    usd_df = fetch_table("USD FTP Yield Curve")

    print()

    zwg_df = zwg_df.T.reset_index()
    usd_df = usd_df.T.reset_index()

    # Convert DataFrames to HTML tables (Bootstrap-friendly)
    zwg_html = zwg_df.to_html(classes="table table-striped table-bordered", index=False)
    usd_html = usd_df.to_html(classes="table table-striped table-bordered", index=False)

    return render_template("index.html", zwg_table=zwg_html, usd_table=usd_html)



if __name__ == '__main__':
    app.run(debug=True)