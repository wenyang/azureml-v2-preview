# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------


from marshmallow import fields, post_load, validate
from typing import Optional
from ..schema import PatchedSchemaMeta
from azure.ml._restclient.machinelearningservices.models import Mpi, TensorFlow, PyTorch
from azure.ml.constants import DistributionType


class MPIDistributionSchema(metaclass=PatchedSchemaMeta):
    distribution_type = fields.Str(
        data_key="type", name="type", required=True, validate=validate.Equal(DistributionType.MPI)
    )
    process_count_per_instance = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        data.pop("distribution_type")
        return Mpi(**data)


class TensorFlowDistributionSchema(metaclass=PatchedSchemaMeta):
    distribution_type = fields.Str(
        data_key="type", name="type", required=True, validate=validate.Equal(DistributionType.TENSORFLOW)
    )
    parameter_server_count = fields.Int()
    worker_count = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        data.pop("distribution_type")
        return TensorFlow(**data)


class PyTorchDistributionSchema(metaclass=PatchedSchemaMeta):
    distribution_type = fields.Str(
        data_key="type", name="type", required=True, validate=validate.Equal(DistributionType.PYTORCH)
    )
    process_count_per_node = fields.Int()

    @post_load
    def make(self, data, **kwargs):
        data.pop("distribution_type")
        return PyTorch(**data)
