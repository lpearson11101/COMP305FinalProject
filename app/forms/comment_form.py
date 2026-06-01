from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class CommentForm(FlaskForm):
    body = TextAreaField(
        "Comment",
        validators=[
            DataRequired(),
            Length(min=2, max=2000)
        ]
    )

    submit = SubmitField("Post Comment")