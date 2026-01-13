from flask import Blueprint
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView

from webapp import bcrypt
from flask_login import current_user



adminnbp= Blueprint("adminnbp",__name__)


class UserModelView(ModelView):
    column_list = ['username', 'email', 'fname', 'lname', 'id']
    column_searchable_list = ['username', 'email']
    column_labels = {
        'fname': 'First Name',
        'lname': 'Last Name'
    }

    def on_model_change(self, form, model, is_created):
        # Only hash if it's a new password or being changed
        if form.password.data and (is_created or not form.password.data.startswith('$2b$')):
             model.password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")

    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1


class MyModelView(ModelView):
    column_display_pk = True
    page_size = 20

    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.id == 1
    






adminbp = Blueprint("adminbp", __name__)





