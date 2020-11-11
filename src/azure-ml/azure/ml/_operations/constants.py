# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
# default timeout of session for getting content in the job run,
# the 1st element is conn timeout, the 2nd is the read timeout.


class Constants():
    _DEFAULT_GET_CONTENT_TIMEOUT = (5, 120)
    _WAIT_COMPLETION_POLLING_INTERVAL_MIN = os.environ.get("AZUREML_RUN_POLLING_INTERVAL_MIN", 2)
    _WAIT_COMPLETION_POLLING_INTERVAL_MAX = os.environ.get("AZUREML_RUN_POLLING_INTERVAL_MAX", 60)


# run document status
class JobStatus(object):
    # Ordered by transition order
    QUEUED = "Queued"
    NOT_STARTED = "NotStarted"
    PREPARING = "Preparing"
    PROVISIONING = "Provisioning"
    STARTING = "Starting"
    RUNNING = "Running"
    CANCEL_REQUESTED = "CancelRequested"
    CANCELED = "Canceled"  # Not official yet
    FINALIZING = "Finalizing"
    COMPLETED = "Completed"
    FAILED = "Failed"
    PAUSED = "Paused"
    NOTRESPONDING = "NotResponding"

    @classmethod
    def list(cls):
        """Return the list of supported run status."""
        return [cls.QUEUED, cls.PREPARING, cls.PROVISIONING, cls.STARTING,
                cls.RUNNING, cls.CANCEL_REQUESTED, cls.CANCELED,
                cls.FINALIZING, cls.COMPLETED, cls.FAILED, cls.NOT_STARTED,
                cls.FAILED, cls.PAUSED, cls.NOTRESPONDING]

    @classmethod
    def get_job_status(cls):
        """Return the list of running status."""
        return [cls.NOT_STARTED,
                cls.QUEUED,
                cls.PREPARING,
                cls.PROVISIONING,
                cls.STARTING,
                cls.RUNNING]

    @classmethod
    def get_post_processing_status(cls):
        """Return the list of running status."""
        return [cls.CANCEL_REQUESTED, cls.FINALIZING]

    @classmethod
    def get_job_terminal_status(cls):
        """Return the list of terminal status."""
        return [cls.COMPLETED, cls.FAILED, cls.CANCELED, cls.NOTRESPONDING, cls.PAUSED]
