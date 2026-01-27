from pycaret.datasets import get_data
from pycaret.classification import ClassificationExperiment
data = get_data('diabetes')
exp = ClassificationExperiment()
exp.setup(data, target='Class variable',session_id=123)
best_model = exp.compare_models()
print(best_model)