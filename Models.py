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
# Fetch all table names in public schema
cursor.execute("""
    SELECT tablename FROM pg_tables
    WHERE schemaname = 'public';
""")
tables = cursor.fetchall()

# Drop each table
for table in tables:
    table_name = table[0]
    cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
    print(f"Dropped table: {table_name}")


data_zwg = {
    "<1m": {
        "Normal Curve Bid Rate": 10.00,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 12.00,
        "Treasury Curve Bid Rate": 16.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 18.00,
    },
    "1m-2m": {
        "Normal Curve Bid Rate": 11.00,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 13.00,
        "Treasury Curve Bid Rate": 11.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 13.00,
    },
    "2m-3m": {
        "Normal Curve Bid Rate": 12.00,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 14.00,
        "Treasury Curve Bid Rate": 11.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 13.00,
    },
    "3m-6m": {
        "Normal Curve Bid Rate": 12.00,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 14.00,
        "Treasury Curve Bid Rate": 11.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 13.00,
    },
    "6m-9m": {
        "Normal Curve Bid Rate": 12.00,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 14.00,
        "Treasury Curve Bid Rate": 11.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 13.00,
    },
    "9m-12m": {
        "Normal Curve Bid Rate": 12.00,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 14.00,
        "Treasury Curve Bid Rate": 11.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 13.00,
    },
    "1y-2y": {
        "Normal Curve Bid Rate": 13.94,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 15.94,
        "Treasury Curve Bid Rate": 7.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 9.00,
    },
    "2y-3y": {
        "Normal Curve Bid Rate": 15.45,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 17.45,
        "Treasury Curve Bid Rate": 5.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 7.00,
    },
    "3y-5y": {
        "Normal Curve Bid Rate": 18.47,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 20.47,
        "Treasury Curve Bid Rate": 5.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 7.00,
    },
    "+5y": {
        "Normal Curve Bid Rate": 17.47,
        "Normal Curve Liquidity Premium": 2.00,
        "Normal Curve Offer Rate": 19.47,
        "Treasury Curve Bid Rate": 5.00,
        "Treasury Curve Liquidity Premium": 2.00,
        "Treasury Curve Offer Rate": 7.00,
    },
}


df_zwg = pd.DataFrame(data_zwg)

data_usd = {
    "<1m": {
        "Normal Curve Bid Rate": 8.00,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 9.15,
        "Treasury Curve Bid Rate": 2.88,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 4.03,
        "Lines of Credit Curve Bid Rate": 9.22,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 10.37,
    },
    "1m-2m": {
        "Normal Curve Bid Rate": 9.00,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 10.15,
        "Treasury Curve Bid Rate": 3.59,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 4.74,
        "Lines of Credit Curve Bid Rate": 9.22,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 10.37,
    },
    "2m-3m": {
        "Normal Curve Bid Rate": 10.00,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 11.15,
        "Treasury Curve Bid Rate": 2.76,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 3.91,
        "Lines of Credit Curve Bid Rate": 9.22,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 10.37,
    },
    "3m-6m": {
        "Normal Curve Bid Rate": 11.00,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 12.15,
        "Treasury Curve Bid Rate": 5.30,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 6.45,
        "Lines of Credit Curve Bid Rate": 9.22,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 10.37,
    },
    "6m-9m": {
        "Normal Curve Bid Rate": 11.00,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 12.15,
        "Treasury Curve Bid Rate": 4.25,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 5.40,
        "Lines of Credit Curve Bid Rate": 9.22,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 10.37,
    },
    "9m-12m": {
        "Normal Curve Bid Rate": 11.00,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 12.15,
        "Treasury Curve Bid Rate": 3.19,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 4.34,
        "Lines of Credit Curve Bid Rate": 9.22,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 10.37,
    },
    "1y-2y": {
        "Normal Curve Bid Rate": 14.39,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 15.54,
        "Treasury Curve Bid Rate": 4.37,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 5.52,
        "Lines of Credit Curve Bid Rate": 9.83,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 10.98,
    },
    "2y-3y": {
        "Normal Curve Bid Rate": 17.11,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 18.26,
        "Treasury Curve Bid Rate": 4.86,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 6.01,
        "Lines of Credit Curve Bid Rate": 9.97,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 11.12,
    },
    "3y-5y": {
        "Normal Curve Bid Rate": 22.55,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 23.70,
        "Treasury Curve Bid Rate": 4.86,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 6.01,
        "Lines of Credit Curve Bid Rate": 10.85,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 12.00,
    },
    "+5y": {
        "Normal Curve Bid Rate": 22.55,
        "Normal Curve Liquidity Premium": 1.15,
        "Normal Curve Offer Rate": 23.70,
        "Treasury Curve Bid Rate": 4.86,
        "Treasury Curve Liquidity Premium": 1.15,
        "Treasury Curve Offer Rate": 6.01,
        "Lines of Credit Curve Bid Rate": 10.85,
        "Lines of Credit Curve Liquidity Premium": 1.15,
        "Lines of Credit Curve Offer Rate": 12.00,
    },
}


df_usd = pd.DataFrame(data_usd)


try:

    # Create table if it doesn't exist
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS zwgftpyieldcurves (
        Metric VARCHAR(100),
        "<1m" NUMERIC,
        "1m-2m" NUMERIC,
        "2m-3m" NUMERIC,
        "3m-6m" NUMERIC,
        "6m-9m" NUMERIC,
        "9m-12m" NUMERIC,
        "1y-2y" NUMERIC,
        "2y-3y" NUMERIC,
        "3y-5y" NUMERIC,
        "+5y" NUMERIC
            );
    """)
    conn.commit()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usdftpyieldcurves (
            Metric VARCHAR(100),
            "<1m" NUMERIC,
            "1m-2m" NUMERIC,
            "2m-3m" NUMERIC,
            "3m-6m" NUMERIC,
            "6m-9m" NUMERIC,
            "9m-12m" NUMERIC,
            "1y-2y" NUMERIC,
            "2y-3y" NUMERIC,
            "3y-5y" NUMERIC,
            "+5y" NUMERIC
        );
    """)

    conn.commit()

    # Fix dataframe layout so "Metric" is a column
    df_zwg_reset = df_zwg.reset_index().rename(columns={"index": "Metric"})

    for _, row in df_zwg_reset.iterrows():
        cursor.execute("""
            INSERT INTO zwgftpyieldcurves
            (Metric, "<1m", "1m-2m", "2m-3m", "3m-6m", "6m-9m", "9m-12m",
            "1y-2y", "2y-3y", "3y-5y", "+5y")
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, tuple(row))

    conn.commit()


    print("✅ Data inserted/updated into 'ZWG FTP Yield Curves' successfully!")


    # Fix dataframe layout so "Metric" is a column
    df_usd_reset = df_usd.reset_index().rename(columns={"index": "Metric"})

    for _, row in df_usd_reset.iterrows():
        cursor.execute("""
            INSERT INTO usdftpyieldcurves
            (Metric, "<1m", "1m-2m", "2m-3m", "3m-6m", "6m-9m", "9m-12m",
            "1y-2y", "2y-3y", "3y-5y", "+5y")
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, tuple(row))

    conn.commit()


    conn.commit()
    print("✅ Data inserted/updated into 'USD FTP Yield Curves' successfully!")

except Exception as e:
    print("❌ Error:", e)'''

@app.route('/')
def landingpage():

    try:

        conn.rollback()

        query = f"SELECT * FROM zwgftpyieldcurves;"
        cursor.execute(query)
        rows = cursor.fetchall()

        colnames = [desc[0] for desc in cursor.description]
        zwg_df = pd.DataFrame(rows, columns=colnames)

        query = f"SELECT * FROM usdftpyieldcurves;"
        cursor.execute(query)
        rows = cursor.fetchall()

        colnames = [desc[0] for desc in cursor.description]
        usd_df = pd.DataFrame(rows, columns=colnames)

        print(zwg_df)
        print(usd_df)

        # Convert DataFrames to HTML tables (Bootstrap-friendly)
        zwg_html = zwg_df.to_html(classes="table table-striped table-bordered", index=False)
        usd_html = usd_df.to_html(classes="table table-striped table-bordered", index=False)

        return render_template("index.html", zwg_table=zwg_html, usd_table=usd_html)

    except Exception as e:
        conn.rollback()  # reset failed transaction
        print("❌ Error in landingpage:", e)
        return f"Database error: {e}", 500

@app.route("/apply", methods=["POST"])
def apply():
    currency = request.form.get("currency")
    tenor = request.form.get("tenor")
    source = request.form.get("source")

    # Do something with inputs (save, process, calculate, etc.)
    result = f"Currency: {currency}, Tenor: {tenor} months, Source: {source}"

    return render_template("form.html", result=result)

if __name__ == '__main__':
    app.run(debug=True)