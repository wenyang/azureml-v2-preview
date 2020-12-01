# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any


class LoadableMixin:
    def load(self, obj: Any) -> None:
        pass
