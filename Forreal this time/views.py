{% if 'manage_team' in user_permissions %}
    <a href="{{ url_for('manage_team') }}" class="btn btn-primary">Manage Team</a>
{% endif %}
{% if 'view_reports' in user_permissions %}
    <a href="{{ url_for('view_reports') }}" class="btn btn-primary">View Reports</a>
{% endif %}
{% endif %}
