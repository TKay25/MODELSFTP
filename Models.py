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

try:
    connection = psycopg2.connect(external_database_url)
    cursor = connection.cursor()
    print("✅ Connection to PostgreSQL successful!")

    # Test query (optional, ensures DB is responsive)
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    print("PostgreSQL version:", record)

except Exception as e:
    print("❌ Failed to connect to the database")
    print("Error:", e)