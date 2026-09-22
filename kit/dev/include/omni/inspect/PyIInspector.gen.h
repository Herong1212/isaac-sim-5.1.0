// SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

// --------- Warning: This is a build system generated file. ----------

#pragma once

#include <omni/core/ITypeFactory.h>
#include <omni/python/PyBind.h>
#include <omni/python/PyString.h>
#include <omni/python/PyVec.h>

#include <sstream>

inline auto bindIInspector(const py::module& m)
{
    // hack around pybind11 issues with C++17
    //   - https://github.com/pybind/pybind11/issues/2234
    //   - https://github.com/pybind/pybind11/issues/2666
    //   - https://github.com/pybind/pybind11/issues/2856
    py::class_<omni::core::Generated<omni::inspect::IInspector_abi>,
               omni::python::detail::PyObjectPtr<omni::core::Generated<omni::inspect::IInspector_abi>>, omni::core::IObject>
        clsParent(m, "_IInspector");
    py::class_<omni::inspect::IInspector, omni::python::detail::PyObjectPtr<omni::inspect::IInspector>> cls(
        m, "IInspector", clsParent, R"OMNI_BIND_RAW_(Base class for object inspection requests.)OMNI_BIND_RAW_");
    cls.def(py::init(
        [](const omni::python::detail::PyObjectPtr<omni::core::IObject>& obj)
        {
            auto tmp = omni::core::cast<omni::inspect::IInspector>(obj.get());
            if (!tmp)
            {
                throw std::runtime_error("invalid type conversion");
            }
            return tmp;
        }));
    cls.def(py::init(
        []()
        {
            auto tmp = omni::core::createType<omni::inspect::IInspector>();
            if (!tmp)
            {
                throw std::runtime_error("unable to create omni::inspect::IInspector instantiation");
            }
            return tmp;
        }));
    cls.def_property(
        "help", nullptr, [](omni::inspect::IInspector* self, const char* helpString) { self->setHelp(helpString); });
    cls.def("help_information", &omni::inspect::IInspector::helpInformation,
            R"OMNI_BIND_RAW_(Returns the help information currently available on the inspector. Note that this could change
from one invocation to the next so it's important to read it immediately after requesting it.
@returns String containing the help information describing the current configuration of the inspector)OMNI_BIND_RAW_");
    cls.def("help_flag", &omni::inspect::IInspector::helpFlag,
            R"OMNI_BIND_RAW_(Returns the common flag used to tell the inspection process to put the help information into the
inspector using the setHelp_abi function. Using this approach avoids having every inspector/object
combination add an extra ABI function just for retrieving the help information, as well as providing a
consistent method for requesting it.
@returns String containing the name of the common flag used for help information)OMNI_BIND_RAW_");
    cls.def(
        "set_flag",
        [](omni::inspect::IInspector* self, const char* flagName, bool flagState) { self->setFlag(flagName, flagState); },
        R"OMNI_BIND_RAW_(Enable or disable an inspection flag. It's up to the individual inspection operations or the derived
inspector interfaces to interpret the flag.
@param[in] flagName Name of the flag to set
@param[in] flagState New state for the flag)OMNI_BIND_RAW_",
        py::arg("flag_name"), py::arg("flag_state"));
    cls.def(
        "is_flag_set",
        [](omni::inspect::IInspector* self, const char* flagName)
        {
            auto return_value = self->isFlagSet(flagName);

            return return_value;
        },
        R"OMNI_BIND_RAW_(Checks whether a particular flag is currently set or not.
@param[in] flagName Name of the flag to check
@returns True if the named flag is set, false if not)OMNI_BIND_RAW_",
        py::arg("flag_name"));
    return omni::python::PyBind<omni::inspect::IInspector>::bind(cls);
}
