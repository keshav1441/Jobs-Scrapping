#!/usr/bin/env python3
"""
Flask web application for displaying scraped jobs
"""

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from config.database import create_tables, SessionLocal, Job
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///jobs.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
create_tables()

@app.route('/')
def index():
    """Main page showing all jobs"""
    return render_template('index.html')

@app.route('/api/jobs')
def get_jobs():
    """API endpoint to get jobs with filtering"""
    db = SessionLocal()
    try:
        # Get query parameters
        search = request.args.get('search', '')
        company = request.args.get('company', '')
        location = request.args.get('location', '')
        source = request.args.get('source', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query
        query = db.query(Job).filter(Job.is_active == True)
        
        if search:
            query = query.filter(
                Job.title.contains(search) | 
                Job.description.contains(search)
            )
        
        if company:
            query = query.filter(Job.company.contains(company))
        
        if location:
            query = query.filter(Job.location.contains(location))
        
        if source:
            query = query.filter(Job.source_site.contains(source))
        
        # Get total count
        total = query.count()
        
        # Paginate results
        jobs = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return jsonify({
            'jobs': [job.to_dict() for job in jobs],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/stats')
def get_stats():
    """Get statistics about scraped jobs"""
    db = SessionLocal()
    try:
        total_jobs = db.query(Job).filter(Job.is_active == True).count()
        
        # Jobs by source
        sources = db.query(Job.source_site, db.func.count(Job.id)).filter(
            Job.is_active == True
        ).group_by(Job.source_site).all()
        
        # Recent jobs (last 24 hours)
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_jobs = db.query(Job).filter(
            Job.is_active == True,
            Job.scraped_at >= recent_cutoff
        ).count()
        
        return jsonify({
            'total_jobs': total_jobs,
            'recent_jobs': recent_jobs,
            'sources': [{'name': source, 'count': count} for source, count in sources]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/companies')
def get_companies():
    """Get list of companies"""
    db = SessionLocal()
    try:
        companies = db.query(Job.company).filter(
            Job.is_active == True,
            Job.company.isnot(None),
            Job.company != ''
        ).distinct().all()
        
        return jsonify([company[0] for company in companies])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/locations')
def get_locations():
    """Get list of locations"""
    db = SessionLocal()
    try:
        locations = db.query(Job.location).filter(
            Job.is_active == True,
            Job.location.isnot(None),
            Job.location != ''
        ).distinct().all()
        
        return jsonify([location[0] for location in locations])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
