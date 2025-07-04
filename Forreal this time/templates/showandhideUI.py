{% if 'manage_users' in user_permissions %}
<a href="{{ url_for('admin.add_user') }}">Add User</a>
{% endif %}
