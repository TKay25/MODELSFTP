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

#external_database_url = "postgresql://lmsdatabase_8ag3_user:6WD9lOnHkiU7utlUUjT88m4XgEYQMTLb@dpg-ctp9h0aj1k6c739h9di0-a.oregon-postgres.render.com/lmsdatabase_8ag3"
#database = 'lmsdatabase_8ag3'

#connection = psycopg2.connect(external_database_url)

#cursor = connection.cursor()