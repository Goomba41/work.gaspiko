# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm
from wtforms import TextField
from wtforms.validators import Required, regexp, Length

class DelExecutorForm(FlaskForm):
    del_id = TextField('id', validators = [Required()])
