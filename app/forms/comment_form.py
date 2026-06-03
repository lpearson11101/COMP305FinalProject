from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

#comment form for users to post comments on book pages. 
# The body of the comment must be between 2 and 2000 characters long.
class CommentForm(FlaskForm):
    body = TextAreaField(
        "Comment",
        validators=[
            DataRequired(),
            Length(min=2, max=2000)
        ]
    )

    submit = SubmitField("Post Comment")