# app/models/__init__.py

from .user_model import User
from .role_model import Role
from .survey_model import Survey
from .farm_model import Farm
from .survey_type_model import SurveyType
from .factor_model import Factor
from .possible_value_model import PossibleValue
from .response_factor_model import ResponseFactor
from .data_tth_model import DataTTH

# Exponer los modelos para facilitar su uso
__all__ = [
    'User',
    'Role',
    'Survey',
    'Farm',
    'SurveyType',
    'Factor',
    'PossibleValue',
    'ResponseFactor',
    'DataTTH'
]