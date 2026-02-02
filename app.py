"""
Web Server untuk Sistem Analisis Gadai
Backend API dengan Flask
"""
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
from pathlib import Path
from config import OUTPUT_DIR, PROCESSED_FILE, OUTLET_SUMMARY, INPUT_FILE
from src.loader import load_and_normalize
from src.processor import process_data
from src.analyzer import analyze_data
from src.reporter import save_reports
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Route utama
@app.route('/')
def index():
    """Halaman utama dashboard"""
    return render_template('index.html')

# API: Get summary statistics
@app.route('/api/summary')
def get_summary():
    """Get statistik ringkasan"""
    try:
        df = pd.read_csv(PROCESSED_FILE)
        
        # Hitung transaksi berisiko tinggi
        transaksi_berisiko = int((df['kategori_risiko'] == 'tinggi').sum()) if 'kategori_risiko' in df.columns else 0
        
        summary = {
            'total_transaksi': len(df),
            'total_outlet': df['outlet'].nunique() if 'outlet' in df.columns else 0,
            'transaksi_berisiko': transaksi_berisiko,
            'persen_berisiko': round(transaksi_berisiko / len(df) * 100, 1) if len(df) > 0 else 0,
            'status_counts': df['status_transaksi'].value_counts().to_dict() if 'status_transaksi' in df.columns else {},
            'risiko_counts': df['kategori_risiko'].value_counts().to_dict() if 'kategori_risiko' in df.columns else {},
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get outlet data
@app.route('/api/outlets')
def get_outlets():
    """Get data summary per outlet"""
    try:
        df = pd.read_csv(OUTLET_SUMMARY)
        
        # Convert to dict
        outlets = []
        for idx, row in df.iterrows():
            outlets.append({
                'outlet': row['outlet'] if 'outlet' in df.columns else idx,
                'total_transaksi': int(row['total_transaksi']),
                'total_pinjaman': float(row['total_pinjaman']),
                'rata_ltv': float(row['rata_ltv']) if 'rata_ltv' in row else 0,
                'transaksi_berisiko': int(row['transaksi_berisiko']) if 'transaksi_berisiko' in row else 0,
                'transaksi_sedang': int(row['transaksi_sedang']) if 'transaksi_sedang' in row else 0,
                'persen_berisiko': float(row['persen_berisiko']) if 'persen_berisiko' in row else 0
            })
        
        return jsonify(outlets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get top outlets
@app.route('/api/outlets/top')
def get_top_outlets():
    """Get top 10 outlet"""
    try:
        limit = int(request.args.get('limit', 10))
        sort_by = request.args.get('sort', 'total_pinjaman')
        
        df = pd.read_csv(OUTLET_SUMMARY)
        df = df.sort_values(sort_by, ascending=False).head(limit)
        
        outlets = []
        for idx, row in df.iterrows():
            outlets.append({
                'outlet': row['outlet'] if 'outlet' in df.columns else idx,
                'total_transaksi': int(row['total_transaksi']),
                'total_pinjaman': float(row['total_pinjaman']),
                'rata_ltv': float(row['rata_ltv']) if 'rata_ltv' in row else 0,
                'transaksi_berisiko': int(row['transaksi_berisiko']) if 'transaksi_berisiko' in row else 0,
                'transaksi_sedang': int(row['transaksi_sedang']) if 'transaksi_sedang' in row else 0,
                'persen_berisiko': float(row['persen_berisiko']) if 'persen_berisiko' in row else 0
            })
        
        return jsonify(outlets)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Get transactions data
@app.route('/api/transactions')
def get_transactions():
    """Get data transaksi dengan pagination"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        outlet = request.args.get('outlet', None)
        
        df = pd.read_csv(PROCESSED_FILE)
        
        # Filter by outlet if specified
        if outlet:
            df = df[df['outlet'] == outlet]
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        total = len(df)
        
        df_page = df.iloc[start:end]
        
        # Convert to dict
        transactions = df_page.to_dict('records')
        
        return jsonify({
            'data': transactions,
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API: Run analysis
@app.route('/api/analyze', methods=['POST'])
def run_analysis():
    """Jalankan analisis ulang"""
    try:
        # Load data
        df = load_and_normalize()
        
        # Process
        df, col_mapping = process_data(df)
        
        # Analyze
        summary_status, outlet_summary = analyze_data(df, col_mapping)
        
        # Save
        save_reports(df, summary_status, outlet_summary)
        
        return jsonify({
            'success': True,
            'message': 'Analisis berhasil dijalankan',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# API: Get chart data
@app.route('/api/charts/status')
def get_status_chart():
    """Data untuk pie chart status"""
    try:
        df = pd.read_csv(PROCESSED_FILE)
        status_counts = df['status_transaksi'].value_counts()
        
        return jsonify({
            'labels': status_counts.index.tolist(),
            'values': status_counts.values.tolist()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts/outlet-risk')
def get_outlet_risk_chart():
    """Data untuk bar chart outlet berisiko"""
    try:
        limit = int(request.args.get('limit', 10))
        df = pd.read_csv(OUTLET_SUMMARY)
        df = df.sort_values('persen_berisiko', ascending=False).head(limit)
        
        return jsonify({
            'labels': df['outlet'].tolist() if 'outlet' in df.columns else df.index.tolist(),
            'values': df['persen_berisiko'].tolist() if 'persen_berisiko' in df.columns else []
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
