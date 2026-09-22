# Copyright (c) 2018-2020, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#


"""This module provides a Singleton pattern implementation that ensures a class has only one instance and provides a global point of access to it."""


def Singleton(class_):
    """Ensures a class has only one instance and provides a global point of access to it.

    Args:
        class_ (type): The class to be instantiated as a singleton."""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance
