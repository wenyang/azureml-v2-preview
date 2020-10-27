# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import re
import sys
import time
import json

from azure.ml._operations.run_operations import RunOperations
from azure.ml._utils.utils import create_session_with_retry, camel_case_transformer, download_text_from_url
from azure.ml._operations.constants import Constants, JobStatus


class JobLogManager(object):
    def __init__(self, runobject: RunOperations, experiment_name: str, job_name: str):
        self.exp_name = experiment_name
        self.job_name = job_name
        self._run = runobject
        self.session = create_session_with_retry()
        self.JOB_STATES = JobStatus.get_job_status()
        self.POST_PROCESSING_STATES = JobStatus.get_post_processing_statuses()
        self.web_uri = None

    def download_all_job_logs(self, destination: str):
        """Download all logs for the run to a directory.
        :param destination: The destination path to store logs. If unspecified, a directory named as the run ID
            is created in the user home directory.
        :type destination: str
        :return: A list of names of logs downloaded.
        :rtype: builtin.list
        """

        destination = os.path.join(destination)
        os.makedirs(destination, exist_ok=True)
        details = self.get_job_logs_with_content()
        log_files = details["logFiles"]
        downloaded_logs = []
        for log_name in log_files:
            target_path = os.path.join(destination, log_name)
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            with open(target_path, 'w') as file:
                file.write(log_files[log_name])
            downloaded_logs.append(target_path)

        return downloaded_logs

    def get_job_logs_with_content(self):   # aka get_details
        """Return run status including log file content.

        :return: Returns the status for the run with log file contents.
        :rtype: dict
        """
        details = self.get_details()
        log_files = details["logFiles"]
        for log_name in log_files:
            content = download_text_from_url(log_files[log_name], self.session)
            log_files[log_name] = content
        return details

    def get_details(self):
        """Get the definition, status information, current log files, and other details of the run.
        :return: Return the details for the run
        :rtype: dict[str, str]
        """
        details = self._run.get_run_details(
            self.exp_name, self.job_name) \
            .as_dict(key_transformer=camel_case_transformer)
        self.status = details.get('status')
        # input_datasets = details.get('inputDatasets')
        # output_datasets = details.get('outputDatasets')
        '''
        if input_datasets is not None:
            from azureml.data._dataset_lineage import _InputDatasetsLineage
            details['inputDatasets'] = _InputDatasetsLineage(self.experiment.workspace, input_datasets)
        if output_datasets:
            from azureml.data._dataset_lineage import update_output_lineage
            update_output_lineage(self.experiment.workspace, output_datasets)
        '''
        return details

    def wait_for_completion(self, weburi: str, show_output=False, wait_post_processing=False, raise_on_error=True):
        """Wait for the completion of this job run. Returns the status object after the wait.
        :param show_output: Indicates whether to show the job run output on sys.stdout.
        :type show_output: bool
        :param wait_post_processing: Indicates whether to wait for the post processing to
            complete after the job run completes.
        :type wait_post_processing: bool
        :param raise_on_error: Indicates whether an Error is raised when the Job Run is in a failed state.
        :type raise_on_error: bool
        :return: The status object.
        :rtype: dict
        """
        self.web_uri = weburi
        if show_output:
            try:
                self._stream_run_output(
                    file_handle=sys.stdout,
                    wait_post_processing=wait_post_processing,
                    raise_on_error=raise_on_error)
                return self.get_details()  # This is normal path
            except KeyboardInterrupt:
                error_message = "The output streaming for the run interrupted.\n" \
                                "But the run is still executing on the compute target. \n" \
                                "Details for canceling the run can be found here: " \
                                "https://aka.ms/aml-docs-cancel-run"

                raise Exception(error_message)
        else:
            job_states = self.JOB_STATES
            if wait_post_processing:
                job_states.extend(self.POST_PROCESSING_STATES)

            current_status = self._run.get_status()
            poll_start_time = time.time()
            while current_status is None or current_status in job_states:
                time.sleep(self._wait_before_polling(time.time() - poll_start_time))
                current_status = self._run.get_status()

            final_details = self.get_details()
            if current_status == JobStatus.FAILED:
                error = final_details.get("error")
                if not error:
                    error = "Detailed error not set on the Run. Please check the logs for details."

                if raise_on_error:
                    raise Exception(error_details=json.dumps(error, indent=4))

            return final_details

    def _stream_run_output(self, file_handle=sys.stdout, wait_post_processing=False, raise_on_error=True):
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

        def incremental_print(log, printed, fileout):
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

        file_handle.write("RunId: {}\n".format(self.job_name))
        file_handle.write("Web View: {}\n".format(self.web_uri))

        printed = 0
        current_log = None
        if wait_post_processing:
            self.JOB_STATES.append(JobStatus.FINALIZING)
            self.JOB_STATES.append(JobStatus.CANCEL_REQUESTED)

        _current_details = self.get_details()
        session = create_session_with_retry()

        # TODO: Temporary solution to wait for all the logs to be printed in the finalizing state.
        poll_start_time = time.time()
        while (_current_details["status"] in self.JOB_STATES or
                _current_details["status"] == JobStatus.FINALIZING):
            file_handle.flush()
            time.sleep(self._wait_before_polling(time.time() - poll_start_time))
            _current_details = self.get_details()  # TODO use FileWatcher

            # Check whether there is a higher priority log than the one we are currently streaming (current_log)
            available_logs = self._get_logs(_current_details)
            # next_log is the log we should be following now, based on the available logs we just got
            next_log = self._get_last_log_primary_instance(available_logs) if available_logs else None
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
                                                 timeout=Constants._DEFAULT_GET_CONTENT_TIMEOUT)
                printed = incremental_print(content, printed, file_handle)

                # TODO: Temporary solution to wait for all the logs to be printed in the finalizing state.
                if (_current_details["status"] not in self.JOB_STATES and
                    _current_details["status"] == JobStatus.FINALIZING and
                        "The activity completed successfully. Finalizing run..." in content):
                    break

        file_handle.write("\n")
        file_handle.write("Execution Summary\n")
        file_handle.write("=================\n")
        file_handle.write("RunId: {}\n".format(self.job_name))
        file_handle.write("Web View: {}\n".format(self.web_uri))

        warnings = _current_details.get("warnings")
        if warnings:
            messages = [x.get("message") for x in warnings if x.get("message")]
            if len(messages) > 0:
                file_handle.write("\nWarnings:\n")
                for message in messages:
                    file_handle.write(message + "\n")
                file_handle.write("\n")

        error = _current_details.get("error")
        if not error:
            error = "Detailed error not set on the Run. Please check the logs for details."

        if _current_details["status"] == JobStatus.FAILED:
            # If we are raising the error later on, so we don't double print.
            if not raise_on_error:
                file_handle.write("\nError:\n")
                file_handle.write(json.dumps(error, indent=4))
                file_handle.write("\n")
            else:
                raise Exception(error_details=json.dumps(error, indent=4))

        file_handle.write("\n")
        file_handle.flush()

    def _wait_before_polling(self, current_seconds):
        if current_seconds < 0:
            raise ValueError("current_seconds must be positive")
        import math
        # Sigmoid that tapers off near the max at ~ 3 min
        duration = Constants._WAIT_COMPLETION_POLLING_INTERVAL_MAX / (1.0 + 100 * math.exp(-current_seconds / 20.0))
        return max(Constants._WAIT_COMPLETION_POLLING_INTERVAL_MIN, duration)

    def _get_logs(self, status):
        """Return logs.
        :param status:
        :type status: dict
        :return:
        :rtype: builtin.list
        """
        # TODO Bani

        self._output_logs_pattern = 'azureml-logs/[\\d]{2}.+\\.txt'

        logs = [x for x in status["logFiles"] if re.match(self._output_logs_pattern, x)]
        logs.sort()
        return logs

    def _get_last_log_primary_instance(self, logs):
        """Return last log for primary instance.
        :param logs:
        :type logs: builtin.list
        :return: Returns the last log primary instance.
        :rtype:
        """
        primary_ranks = ["rank_0", "worker_0"]
        rank_match_re = re.compile("(.*)_(.*?_.*?)\.txt")
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

    def get_job_status(self):
        """Fetch the latest status of the run.

        Common values returned include "Running", "Completed", and "Failed".

        .. remarks::

            * NotStarted - This is a temporary state client-side Run objects are in before cloud submission.
            * Starting - The Run has started being processed in the cloud. The caller has a run ID at this point.
            * Provisioning - Returned when on-demand compute is being created for a given job submission.
            * Preparing - The run environment is being prepared:
                * docker image build
                * conda environment setup
            * Queued - The job is queued in the compute target. For example, in BatchAI the job is in queued state
                 while waiting for all the requested nodes to be ready.
            * Running - The job started to run in the compute target.
            * Finalizing - User code has completed and the run is in post-processing stages.
            * CancelRequested - Cancellation has been requested for the job.
            * Completed - The run completed successfully. This includes both the user code and run
                post-processing stages.
            * Failed - The run failed. Usually the Error property on a run will provide details as to why.
            * Canceled - Follows a cancellation request and indicates that the run is now successfully cancelled.
            * NotResponding - For runs that have Heartbeats enabled, no heartbeat has been recently sent.

            .. code-block:: python

                run = experiment.submit(config)
                while run.get_status() not in ['Completed', 'Failed']: # For example purposes only, not exhaustive
                    print('Run {} not in terminal state'.format(run.id))
                    time.sleep(10)

        :return: The latest status.
        :rtype: str
        """
        if self.status not in ["Completed", "Failed", "Canceled", "NotResponding", "Paused"]:
            self.status = self._run.get_status(self.exp_name, self.job_name)
        return self.status
