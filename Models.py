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

data = {
    "Tenor": ["<1m", "1m-2m", "2m-3m", "3m-6m", "6m-9m", "9m-12m", "1y-2y", "2y-3y", "3y-5y", "+5y"],
    "Normal Curve Bid Rate": [10.00, 11.00, 12.00, 12.00, 12.00, 12.00, 13.94, 15.45, 18.47, 17.47],
    "Normal Curve Liquidity Premium": [2.00]*10,
    "Normal Curve Offer Rate": [12.00, 13.00, 14.00, 14.00, 14.00, 14.00, 15.94, 17.45, 20.47, 19.47],
    "Treasury Curve Bid Rate": [16.00, 11.00, 11.00, 11.00, 11.00, 11.00, 7.00, 5.00, 5.00, 5.00],
    "Treasury Curve Liquidity Premium": [2.00]*10,
    "Treasury Curve Offer Rate": [18.00, 13.00, 13.00, 13.00, 13.00, 13.00, 9.00, 7.00, 7.00, 7.00],
}

df = pd.DataFrame(data)

try:
    conn = psycopg2.connect(external_database_url)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "ZWG FTP Yield Curve" (
            Term VARCHAR(10) PRIMARY KEY,
            Normal_Curve_Bid_Rate NUMERIC,
            Normal_Curve_Liquidity_Premium NUMERIC,
            Normal_Curve_Offer_Rate NUMERIC,
            Treasury_Curve_Bid_Rate NUMERIC,
            Treasury_Curve_Liquidity_Premium NUMERIC,
            Treasury_Curve_Offer_Rate NUMERIC
        );
    """)

    # Insert rows (on conflict, update values)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO "ZWG FTP Yield Curve" 
            (Tenor, Normal_Curve_Bid_Rate, Normal_Curve_Liquidity_Premium, Normal_Curve_Offer_Rate, 
             Treasury_Curve_Bid_Rate, Treasury_Curve_Liquidity_Premium, Treasury_Curve_Offer_Rate)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (Term) DO UPDATE SET
                Normal_Curve_Bid_Rate = EXCLUDED.Normal_Curve_Bid_Rate,
                Normal_Curve_Liquidity_Premium = EXCLUDED.Normal_Curve_Liquidity_Premium,
                Normal_Curve_Offer_Rate = EXCLUDED.Normal_Curve_Offer_Rate,
                Treasury_Curve_Bid_Rate = EXCLUDED.Treasury_Curve_Bid_Rate,
                Treasury_Curve_Liquidity_Premium = EXCLUDED.Treasury_Curve_Liquidity_Premium,
                Treasury_Curve_Offer_Rate = EXCLUDED.Treasury_Curve_Offer_Rate;
        """, tuple(row))

    conn.commit()
    print("✅ Data inserted/updated into 'ZWG FTP Yield Curve' successfully!")

except Exception as e:
    print("❌ Error:", e)