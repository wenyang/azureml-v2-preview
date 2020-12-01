# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import re
import sys
import time
import json

from azure.ml._operations.run_operations import RunOperations
from azure.ml._utils.utils import create_session_with_retry, camel_case_transformer, download_text_from_url
from azure.ml._operations.run_history_constants import RunHistoryConstants, JobStatus
from azure.ml._restclient.machinelearningservices.models import JobBaseResource

STATUS_KEY = "status"


def _get_logs(run_details):
    """Return logs.
    :param status:
    :type status: dict
    :return:
    :rtype: builtin.list
    """
    # TODO Bani

    output_logs_pattern = 'azureml-logs/[\\d]{2}.+\\.txt'

    logs = [x for x in run_details["logFiles"] if re.match(output_logs_pattern, x)]
    logs.sort()
    return logs


def _incremental_print(log, printed, fileout):
    """Incremental print.
    :param log:
    :type log: dict
    :param printed:
    :type printed: int
    :param fileout:
    :type fileout: TestIOWrapper
    :return:
    :rtype: int
    """
    count = 0
    for line in log.splitlines():
        if count >= printed:
            fileout.write(line + "\n")
            printed += 1
        count += 1

    return printed


def _get_last_log_primary_instance(logs):
    """Return last log for primary instance.
    :param logs:
    :type logs: builtin.list
    :return: Returns the last log primary instance.
    :rtype:
    """
    primary_ranks = ["rank_0", "worker_0"]
    rank_match_re = re.compile(r"(.*)_(.*?_.*?)\.txt")
    last_log_name = logs[-1]

    last_log_match = rank_match_re.match(last_log_name)
    if not last_log_match:
        return last_log_name

    last_log_prefix = last_log_match.group(1)
    matching_logs = sorted(filter(lambda x: x.startswith(last_log_prefix), logs))

    # we have some specific ranks that denote the primary, use those if found
    for log_name in matching_logs:
        match = rank_match_re.match(log_name)
        if not match:
            continue
        if match.group(2) in primary_ranks:
            return log_name

    # no definitively primary instance, just return the highest sorted
    return matching_logs[0]


def _wait_before_polling(current_seconds):
    if current_seconds < 0:
        raise ValueError("current_seconds must be positive")
    import math
    # Sigmoid that tapers off near the_get_logs max at ~ 3 min
    duration = RunHistoryConstants._WAIT_COMPLETION_POLLING_INTERVAL_MAX / (1.0 + 100 * math.exp(-current_seconds / 20.0))
    return max(RunHistoryConstants._WAIT_COMPLETION_POLLING_INTERVAL_MIN, duration)


def stream_logs_until_completion(run_operations: RunOperations, job_resource: JobBaseResource, raise_exception_on_failed_job=True) -> None:
    job_name = job_resource.name
    experiment_name = job_resource.properties.experiment_name
    studio_endpoint = job_resource.properties.interaction_endpoints.studio or None
    file_handle = sys.stdout

    def get_details():
        """Get the definition, status information, current log files, and other details of the run.
        :return: Return the details for the run
        :rtype: dict[str, str]
        """
        return run_operations.get_run_details(
            experiment_name, job_name) \
            .as_dict(key_transformer=camel_case_transformer)

    try:
        """Stream the experiment run output to the specified file handle.
        By default the the file handle points to stdout.
        :param file_handle: A file handle to stream the output to.
        :type file_handle: file
        :param wait_post_processing:
        :type wait_post_processing: bool
        :return:
        :rtype: builtin.list
        """
        # from azureml._execution import _commands

        file_handle.write("RunId: {}\n".format(job_name))
        file_handle.write("Web View: {}\n".format(studio_endpoint))

        printed = 0
        current_log = None
        _current_details = get_details()
        session = create_session_with_retry()

        # TODO: Temporary solution to wait for all the logs to be printed in the finalizing state.
        poll_start_time = time.time()
        while (_current_details[STATUS_KEY] in RunHistoryConstants.IN_PROGRESS_STAUSES or
                _current_details[STATUS_KEY] == JobStatus.FINALIZING):
            file_handle.flush()
            time.sleep(_wait_before_polling(time.time() - poll_start_time))
            _current_details = get_details()  # TODO use FileWatcher

            # Check whether there is a higher priority log than the one we are currently streaming (current_log)
            available_logs = _get_logs(_current_details)
            # next_log is the log we should be following now, based on the available logs we just got
            next_log = _get_last_log_primary_instance(available_logs) if available_logs else None
            # if next_log != current_log, we need to switch to streaming next_log
            if available_logs and current_log != next_log:
                printed = 0
                current_log = next_log
                file_handle.write("\n")
                file_handle.write("Streaming " + current_log + "\n")
                file_handle.write("=" * (len(current_log) + 10) + "\n")
                file_handle.write("\n")

            if current_log:
                content = download_text_from_url(_current_details["logFiles"][current_log],
                                                 session,
                                                 timeout=RunHistoryConstants._DEFAULT_GET_CONTENT_TIMEOUT)
                printed = _incremental_print(content, printed, file_handle)

                # TODO: Temporary solution to wait for all the logs to be printed in the finalizing state.
                if (_current_details[STATUS_KEY] not in RunHistoryConstants.IN_PROGRESS_STAUSES and
                    _current_details[STATUS_KEY] == JobStatus.FINALIZING and
                        "The activity completed successfully. Finalizing run..." in content):
                    break

        file_handle.write("\n")
        file_handle.write("Execution Summary\n")
        file_handle.write("=================\n")
        file_handle.write("RunId: {}\n".format(job_name))
        file_handle.write("Web View: {}\n".format(studio_endpoint))

        warnings = _current_details.get("warnings")
        if warnings:
            messages = [x.get("message") for x in warnings if x.get("message")]
            if len(messages) > 0:
                file_handle.write("\nWarnings:\n")
                for message in messages:
                    file_handle.write(message + "\n")
                file_handle.write("\n")

        if _current_details[STATUS_KEY] == JobStatus.FAILED:
            error = _current_details.get("error", "Detailed error not set on the Run. Please check the logs for details.")
            # If we are raising the error later on, so we don't double print.
            if not raise_exception_on_failed_job:
                file_handle.write("\nError:\n")
                file_handle.write(json.dumps(error, indent=4))
                file_handle.write("\n")
            else:
                raise Exception("Exception : \n {} ".format(json.dumps(error, indent=4)))

        file_handle.write("\n")
        file_handle.flush()
    except KeyboardInterrupt:
        error_message = "The output streaming for the run interrupted.\n" \
                        "But the run is still executing on the compute target. \n" \
                        "Details for canceling the run can be found here: " \
                        "https://aka.ms/aml-docs-cancel-run"
        raise Exception(error_message)
