# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

# Import the Tf module so that bindings are registered for pxr::TfToken
# Otherwise we get "boost::python::error_already_set" exceptions when importing this module
# We wrap the import in try catch so that it's not considered a public python module by repo_checkapi
try:
    import pxr.Tf
except ImportError:
    pass

from ._omni_converter_dgn_tokens import *
