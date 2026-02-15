from marshmallow import Schema, fields, validate, pre_load


class ThemeSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True, validate=validate.Length(min=1))


class AnswerSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1))
    is_correct = fields.Bool(required=True)


class QuestionSchema(Schema):
    id = fields.Int(required=False)
    title = fields.Str(required=True, validate=validate.Length(min=1))
    theme_id = fields.Int(required=True)
    answers = fields.Nested(AnswerSchema, many=True, required=True)

    @pre_load
    def check_answers(self, data, **kwargs):
        answers = data.get("answers", [])
        if len(answers) < 2:
            raise ValueError("Must be at least 2 answers")
        
        correct_count = sum(1 for a in answers if a.get("is_correct"))
        if correct_count == 0:
            raise ValueError("Must have at least one correct answer")
        if correct_count > 1:
            raise ValueError("Must have only one correct answer")
        
        return data


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeSchema, many=True)





class ThemeIdSchema(Schema):
    theme_id = fields.Int(required=True)


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)