from azureml.core import Workspace, Experiment, Dataset, Run
from azureml.train.automl import AutoMLConfig

exp = Run.get_context().experiment

data = "https://automlsamplenotebookdata.blob.core.windows.net/automl-sample-notebook-data/creditcard.csv"
compute_name = "cpu-cluster"

dataset = Dataset.Tabular.from_delimited_files(data)

automl_settings = {
    "n_cross_validations": 3,
    "primary_metric": "average_precision_score_weighted",
    "enable_early_stopping": True,
}

automl_config = AutoMLConfig(
    task="classification",
    max_concurrent_iterations=3,
    compute_target=compute_name,
    training_data=dataset,
    label_column_name="Class",
    **automl_settings
)

run = exp.submit(automl_config)
run.wait_for_completion(show_output=True)
