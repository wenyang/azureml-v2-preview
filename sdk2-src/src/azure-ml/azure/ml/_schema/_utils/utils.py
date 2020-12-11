# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Any, Dict, Union

from azure.ml._schema import CommandJobSchema, InternalCommandJob
from azure.ml._schema._sweep import SweepJobSchema, InternalSweepJob

from azure.ml.constants import JOB_TYPE, JobType


def load_job_from_yaml(
    data: Dict[str, Any], context: Dict[str, str], **kwargs
) -> Union[InternalCommandJob, InternalSweepJob]:
    job_type = data.pop(JOB_TYPE, None)
    if job_type == JobType.SWEEP:
        return SweepJobSchema(context=context).load(data, **kwargs)
    else:
        return CommandJobSchema(context=context).load(data, **kwargs)
