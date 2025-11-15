"""Admin routes for the Campus Resource Hub."""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload
from datetime import datetime
from src.database import db
from src.decorators import admin_required
from src.models import User, Resource, Booking, Review
from src.views.resources import get_resource_stats

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview statistics."""
    # Get statistics
    total_users = User.query.count()
    active_resources = Resource.query.filter_by(status='published').count()
    pending_approvals = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    
    # Get category breakdown
    category_counts = db.session.query(
        Resource.category,
        func.count(Resource.id).label('count')
    ).group_by(Resource.category).all()
    
    category_data = []
    category_labels = {
        'study-room': 'Study Rooms',
        'lab-equipment': 'Lab Equipment',
        'event-space': 'Event Spaces',
        'av-equipment': 'AV Equipment',
        'tutoring': 'Tutoring',
        'other': 'Other'
    }
    
    for category, count in category_counts:
        category_data.append({
            'name': category_labels.get(category, category),
            'count': count
        })
    
    # Get recent bookings (last 5)
    recent_bookings = Booking.query.order_by(desc(Booking.created_at)).limit(5).all()
    
    # Get top resources by booking count
    top_resources = db.session.query(
        Resource.id,
        Resource.title,
        func.count(Booking.id).label('booking_count')
    ).join(Booking, Resource.id == Booking.resource_id, isouter=True)\
     .group_by(Resource.id, Resource.title)\
     .order_by(desc('booking_count'))\
     .limit(5).all()
    
    stats = {
        'total_users': total_users,
        'active_resources': active_resources,
        'pending_approvals': pending_approvals,
        'total_bookings': total_bookings
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         category_data=category_data,
                         recent_bookings=recent_bookings,
                         top_resources=top_resources,
                         active_tab='overview')


@admin_bp.route('/users')
@admin_required
def users():
    """User management page."""
    users_list = User.query.order_by(desc(User.created_at)).all()
    
    # Get stats for overview
    total_users = len(users_list)
    active_resources = Resource.query.filter_by(status='published').count()
    pending_approvals = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    
    return render_template('admin/dashboard.html',
                         users=users_list,
                         stats={'total_users': total_users, 'active_resources': active_resources, 'pending_approvals': pending_approvals, 'total_bookings': total_bookings},
                         category_data=[],
                         recent_bookings=[],
                         top_resources=[],
                         resources=[],
                         reviews=[],
                         pending_bookings=[],
                         active_tab='users')


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Delete user (cascade will handle related records)
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.name} has been deleted.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/update-role', methods=['POST'])
@admin_required
def update_user_role(user_id):
    """Update a user's role."""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role not in ['student', 'staff', 'admin']:
        flash('Invalid role.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Prevent changing your own role from admin
    if user.id == current_user.id and user.role == 'admin' and new_role != 'admin':
        flash('You cannot change your own role from admin.', 'danger')
        return redirect(url_for('admin.users'))
    
    user.role = new_role
    db.session.commit()
    
    flash(f'User {user.name}\'s role has been updated to {new_role}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/resources')
@admin_required
def resources():
    """Resource management page."""
    resources_list = Resource.query.options(
        joinedload(Resource.owner)
    ).order_by(desc(Resource.created_at)).all()
    
    # Add stats to each resource
    resources_with_stats = []
    for resource in resources_list:
        stats = get_resource_stats(resource.id)
        resources_with_stats.append({
            'resource': resource,
            'rating': stats['rating'],
            'review_count': stats['review_count'],
            'booking_count': stats['booking_count']
        })
    
    # Get stats for overview
    total_users = User.query.count()
    active_resources = Resource.query.filter_by(status='published').count()
    pending_approvals = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    
    return render_template('admin/dashboard.html',
                         resources=resources_with_stats,
                         users=User.query.all(),
                         stats={'total_users': total_users, 'active_resources': active_resources, 'pending_approvals': pending_approvals, 'total_bookings': total_bookings},
                         category_data=[],
                         recent_bookings=[],
                         top_resources=[],
                         reviews=[],
                         pending_bookings=[],
                         active_tab='resources')


@admin_bp.route('/resources/<int:resource_id>/archive', methods=['POST'])
@admin_required
def archive_resource(resource_id):
    """Archive a resource."""
    resource = Resource.query.get_or_404(resource_id)
    resource.status = 'archived'
    resource.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Resource "{resource.title}" has been archived.', 'success')
    return redirect(url_for('admin.resources'))


@admin_bp.route('/resources/<int:resource_id>/publish', methods=['POST'])
@admin_required
def publish_resource(resource_id):
    """Publish a resource."""
    resource = Resource.query.get_or_404(resource_id)
    resource.status = 'published'
    resource.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Resource "{resource.title}" has been published.', 'success')
    return redirect(url_for('admin.resources'))


@admin_bp.route('/approvals')
@admin_required
def approvals():
    """Pending booking approvals page."""
    pending_bookings = Booking.query.filter_by(status='pending')\
        .options(joinedload(Booking.resource), joinedload(Booking.user))\
        .order_by(Booking.created_at).all()
    
    # Get stats for overview
    total_users = User.query.count()
    active_resources = Resource.query.filter_by(status='published').count()
    total_bookings = Booking.query.count()
    
    return render_template('admin/dashboard.html',
                         pending_bookings=pending_bookings,
                         users=User.query.all(),
                         resources=[],
                         stats={'total_users': total_users, 'active_resources': active_resources, 'pending_approvals': len(pending_bookings), 'total_bookings': total_bookings},
                         category_data=[],
                         recent_bookings=[],
                         top_resources=[],
                         reviews=[],
                         active_tab='approvals')


@admin_bp.route('/approvals/<int:booking_id>/approve', methods=['POST'])
@admin_required
def approve_booking(booking_id):
    """Approve a pending booking."""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != 'pending':
        flash('This booking is not pending approval.', 'danger')
        return redirect(url_for('admin.approvals'))
    
    booking.status = 'approved'
    booking.updated_at = datetime.utcnow()
    
    # Create notification
    from src.views.bookings import create_notification
    create_notification(
        booking.user_id,
        'booking_confirmed',
        'Booking Approved',
        f'Your booking for {booking.resource.title} has been approved.',
        url_for('bookings.list_bookings')
    )
    
    db.session.commit()
    
    flash('Booking approved successfully.', 'success')
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/approvals/<int:booking_id>/reject', methods=['POST'])
@admin_required
def reject_booking(booking_id):
    """Reject a pending booking."""
    booking = Booking.query.get_or_404(booking_id)
    
    if booking.status != 'pending':
        flash('This booking is not pending approval.', 'danger')
        return redirect(url_for('admin.approvals'))
    
    booking.status = 'rejected'
    booking.updated_at = datetime.utcnow()
    
    # Create notification
    from src.views.bookings import create_notification
    create_notification(
        booking.user_id,
        'booking_rejected',
        'Booking Rejected',
        f'Your booking request for {booking.resource.title} has been rejected.',
        url_for('bookings.list_bookings')
    )
    
    db.session.commit()
    
    flash('Booking rejected.', 'success')
    return redirect(url_for('admin.approvals'))


@admin_bp.route('/reviews')
@admin_required
def reviews():
    """Review moderation page."""
    reviews_list = Review.query.options(
        joinedload(Review.resource),
        joinedload(Review.user)
    ).order_by(desc(Review.created_at)).all()
    
    # Get stats for overview
    total_users = User.query.count()
    active_resources = Resource.query.filter_by(status='published').count()
    pending_approvals = Booking.query.filter_by(status='pending').count()
    total_bookings = Booking.query.count()
    
    return render_template('admin/dashboard.html',
                         reviews=reviews_list,
                         users=User.query.all(),
                         resources=[],
                         stats={'total_users': total_users, 'active_resources': active_resources, 'pending_approvals': pending_approvals, 'total_bookings': total_bookings},
                         category_data=[],
                         recent_bookings=[],
                         top_resources=[],
                         pending_bookings=[],
                         active_tab='reviews')


@admin_bp.route('/chatbot/query', methods=['POST'])
@admin_required
def chatbot_query():
    """Handle chatbot queries using Gemini API."""
    import os
    from google import genai
    from markupsafe import Markup
    import markdown
    
    user_question = request.json.get('question', '').strip()
    
    if not user_question:
        return jsonify({'error': 'Please enter a question.'}), 400
    
    # Get API key from environment variable
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        return jsonify({'error': 'GEMINI_API_KEY environment variable is not set. Please configure it in your .env file.'}), 500
    
    try:
        import time
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Try different models in order of preference (free tier models)
        # The google-genai library may use different model names than the REST API
        models_to_try = [
            'gemini-pro',  # Most widely available free tier model
            'gemini-1.5-pro',
            'gemini-1.5-flash',
            'gemini-2.0-flash-exp'
        ]
        
        # Get database schema
        from src.utils.chatbot import get_database_schema, execute_safe_query
        schema_info = get_database_schema()
        
        # First API call: Generate SQL query
        sql_prompt = f"""{schema_info}

User Question: {user_question}

Please generate a SQL SELECT query to answer this question. Return ONLY the SQL query, nothing else.
Make sure the query is safe (SELECT only) and follows SQLite syntax. Use proper table and column names as described in the schema above."""
        
        # Helper function to make API call with retry logic
        def make_api_call_with_retry(model_name, prompt, max_retries=3):
            """Make API call with exponential backoff retry for rate limits."""
            for attempt in range(max_retries):
                try:
                    return client.models.generate_content(model=model_name, contents=prompt)
                except Exception as e:
                    error_str = str(e)
                    
                    # If it's a 404, don't retry - try next model
                    if '404' in error_str or 'NOT_FOUND' in error_str:
                        raise  # Re-raise to try next model
                    
                    # If it's a rate limit/quota error, retry with backoff
                    if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                        if attempt < max_retries - 1:
                            # Exponential backoff: 2^attempt seconds (2s, 4s, 8s)
                            wait_time = 2 ** attempt
                            print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                            time.sleep(wait_time)
                            continue
                        else:
                            # Last attempt failed, raise with helpful message
                            raise Exception(
                                f"Rate limit exceeded after {max_retries} retries. "
                                "This may be due to free tier limits. "
                                "Please wait a few minutes and try again, or consider enabling billing for higher limits."
                            )
                    
                    # For other errors, raise immediately
                    raise
            
            return None
        
        # Try models until one works
        sql_response = None
        model = None
        last_error = None
        
        for model_name in models_to_try:
            try:
                model = model_name
                sql_response = make_api_call_with_retry(model, sql_prompt)
                break  # Success, exit loop
            except Exception as e:
                last_error = e
                # If it's a 404, try next model
                error_str = str(e)
                if '404' in error_str or 'NOT_FOUND' in error_str:
                    continue  # Try next model
                else:
                    # For other errors (quota, etc.), raise immediately
                    raise
        
        if sql_response is None:
            raise Exception(f"Could not find an available model. Last error: {last_error}")
        generated_sql = sql_response.text.strip()
        
        # Clean up the SQL (remove markdown code blocks if present)
        if '```sql' in generated_sql:
            generated_sql = generated_sql.split('```sql')[1].split('```')[0].strip()
        elif '```' in generated_sql:
            generated_sql = generated_sql.split('```')[1].split('```')[0].strip()
        
        # Execute the query
        query_result = execute_safe_query(generated_sql)
        
        if 'error' in query_result:
            # Include the generated SQL in the error for debugging
            return jsonify({
                'error': f"Database query error: {query_result['error']}",
                'sql': generated_sql,
                'debug': f"Generated SQL (first 200 chars): {generated_sql[:200]}"
            }), 400
        
        # Second API call: Summarize results in natural language
        result_data = query_result['data']
        
        summary_prompt = f"""User asked: {user_question}

I executed this SQL query:
{generated_sql}

Results ({query_result['row_count']} rows):
{result_data}

Please provide a clear, natural language answer to the user's question based on these results. Be concise and informative."""
        
        # Use the same model that worked for SQL generation, with retry logic
        summary_response = make_api_call_with_retry(model, summary_prompt)
        result_text = summary_response.text
        
        # Convert markdown to HTML for better formatting
        result_html = Markup(markdown.markdown(result_text, extensions=['fenced_code', 'tables', 'nl2br']))
        
        return jsonify({
            'success': True,
            'answer': result_html,
            'sql': generated_sql,
            'row_count': query_result['row_count']
        })
        
    except Exception as e:
        # Log the error for debugging
        import traceback
        print(f"Chatbot error: {e}")
        print(traceback.format_exc())
        return jsonify({'error': f'API error: {str(e)}'}), 500
