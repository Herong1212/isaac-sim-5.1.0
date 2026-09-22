# Copyright (c) 2023, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


"""A helper class which helps to interact with Fabric stages."""

__all__ = ["FabricStageHelper"]

import usdrt.Usd
from typing import Optional


class FabricStageHelper:
    """A helper class that manages Fabric and USD stages within a given context.

    This class allows users to interact with Fabric and USD stages by either using a specified stage or the current context's stage. It encapsulates the logic to fetch and set the Fabric/USD stage based on the context or the provided stage.

    Args:
        stage: Optional[usdrt.Usd.Stage]
            The Fabric stage to be used. If not provided, stage will be fetched from context.
        context_name: Optional[str]
            The name of the context from which to fetch the stage; if not provided, the default context is used."""

    def __init__(self, stage: Optional[usdrt.Usd.Stage] = None, context_name: Optional[str] = None):
        """Initializes the FabricStageHelper with an optional stage or context name."""
        self._set_stage(stage, context_name)

    def _set_stage(self, stage: Optional[usdrt.Usd.Stage] = None, context_name: Optional[str] = None):
        """Internal method to set the stage ID or context name.

        Args:
            stage (Optional[usdrt.Usd.Stage]): The Fabric stage to store. If provided, context_name is ignored.
            context_name (Optional[str]): The name of the context to store. Used if stage is None."""
        if stage is not None:
            self.__stage_id = stage.GetStageId()
            self.__context_name = None
        elif context_name is not None:
            self.__stage_id = None
            self.__context_name = context_name
        else:
            self.__stage_id = None
            self.__context_name = ""

    def _get_context(self) -> Optional["omni.usd.context"]:
        """Retrieves the USD context based on the stored context name.

        Returns:
            Optional["omni.usd.context"]: The USD context if available; otherwise, None."""
        import omni.usd

        if self.__context_name is not None:
            return omni.usd.get_context(self.__context_name)

        return omni.usd.get_context()

    def _get_stage(self) -> Optional[usdrt.Usd.Stage]:
        """Retrieves the attached Fabric stage based on the stored stage ID or the current context's stage ID.

        Returns:
            Optional[usdrt.Usd.Stage]: The attached Fabric stage if available; otherwise, None."""
        if self.__stage_id is not None:
            stage = usdrt.Usd.Stage.Attach(self.__stage_id)
            return stage

        stage_id = self._get_context().get_stage_id()
        return usdrt.Usd.Stage.Attach(stage_id)

    def _get_usd_stage(self):
        """Retrieves the USD stage from the current context.

        Returns:
            pxr.Usd.Stage: The USD stage associated with the current context."""
        return self._get_context().get_stage()
