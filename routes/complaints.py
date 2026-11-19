from flask import Blueprint, render_template, request, redirect, url_for, session
from models.complaint import save_complaint

complaints_bp = Blueprint('complaints', __name__)

@complaints_bp.route('/submit-complaint', methods=['GET', 'POST'])
def submit_complaint():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == 'POST':
        user_id = session["user_id"]
        category = request.form.get('category', '').strip()
        description = request.form.get('description', '').strip()
        
        if not category or not description:
            return "All fields are required!", 400
            
        complaint_id = save_complaint(user_id, category, description)
        
        return render_template('submission_success.html', complaint_id=complaint_id)
        
    return render_template('submit_complaint.html')