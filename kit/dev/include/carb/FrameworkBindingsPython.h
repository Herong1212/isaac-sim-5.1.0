// SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.
#pragma once

#include "BindingsPythonUtils.h"
#include "StartupUtils.h"
#include "filesystem/IFileSystem.h"
#include "logging/Logger.h"

#include <memory>
#include <string>
#include <vector>

using namespace py::literals;

namespace carb
{
namespace filesystem
{
struct File
{
};
} // namespace filesystem

namespace detail
{
template <typename VT, typename T, size_t S>
T getVectorValue(const VT& vector, size_t i)
{
    if (i >= S)
    {
        throw py::index_error();
    }

    const T* components = reinterpret_cast<const T*>(&vector);
    return components[i];
}
template <typename VT, typename T, size_t S>
void setVectorValue(VT& vector, size_t i, T value)
{
    if (i >= S)
    {
        throw py::index_error();
    }

    T* components = reinterpret_cast<T*>(&vector);
    components[i] = value;
}

template <typename VT, typename T, size_t S>
bool getVectorEq(const VT& lhs, const VT& rhs)
{
    if (std::addressof(lhs) == std::addressof(rhs))
        return true;

    const T* plhs = reinterpret_cast<const T*>(std::addressof(lhs));
    const T* prhs = reinterpret_cast<const T*>(std::addressof(rhs));
    for (size_t i = 0; i != S; ++i)
    {
        if (*(plhs++) != *(prhs++))
            return false;
    }
    return true;
}

template <typename VT, typename T, size_t S>
py::list getVectorSlice(const VT& s, const py::slice& slice)
{
    size_t start, stop, step, slicelength;
    if (!slice.compute(S, &start, &stop, &step, &slicelength))
        throw py::error_already_set();
    py::list returnList;
    for (size_t i = 0; i < slicelength; ++i)
    {
        returnList.append(getVectorValue<VT, T, S>(s, start));
        start += step;
    }
    return returnList;
}

template <typename VT, typename T, size_t S>
void setVectorSlice(VT& s, const py::slice& slice, const py::sequence& value)
{
    size_t start, stop, step, slicelength;
    if (!slice.compute(S, &start, &stop, &step, &slicelength))
        throw py::error_already_set();
    if (slicelength != value.size())
        throw std::runtime_error("Left and right hand size of slice assignment have different sizes!");
    for (size_t i = 0; i < slicelength; ++i)
    {
        setVectorValue<VT, T, S>(s, start, value[i].cast<T>());
        start += step;
    }
}

template <typename TupleT, class T, size_t S>
py::class_<TupleT> defineTupleCommon(py::module& m, const char* name, const char* docstring)
{
    py::class_<TupleT> c(m, name, docstring);

    c.def(py::init<>());

    c.def("__eq__", [](const TupleT& lhs, const TupleT& rhs) { return getVectorEq<TupleT, T, S>(lhs, rhs); });
    c.def("__ne__", [](const TupleT& lhs, const TupleT& rhs) { return !getVectorEq<TupleT, T, S>(lhs, rhs); });

    // Python special methods for iterators, [], len():
    c.def("__len__", [](const TupleT& t) {
        CARB_UNUSED(t);
        return S;
    });
    c.def("__getitem__", [](const TupleT& t, size_t i) { return getVectorValue<TupleT, T, S>(t, i); });
    c.def("__setitem__", [](TupleT& t, size_t i, T v) { setVectorValue<TupleT, T, S>(t, i, v); });
    c.def("__getitem__",
          [](const TupleT& t, py::slice slice) -> py::list { return getVectorSlice<TupleT, T, S>(t, slice); });
    c.def("__setitem__",
          [](TupleT& t, py::slice slice, const py::sequence& value) { setVectorSlice<TupleT, T, S>(t, slice, value); });

    // That allows passing python sequence into C++ function which accepts concrete TupleT:
    py::implicitly_convertible<py::sequence, TupleT>();

    return c;
}

template <typename TupleT, class T>
py::class_<TupleT> defineTuple(py::module& m,
                               const char* typeName,
                               const char* varName0,
                               T TupleT::*var0,
                               const char* varName1,
                               T TupleT::*var1,
                               const char* docstring = "")
{
    py::class_<TupleT> c = detail::defineTupleCommon<TupleT, T, 2>(m, typeName, docstring);

    // Ctors:
    c.def(py::init<T, T>());
    c.def(py::init([](py::sequence s) -> TupleT { return { s[0].cast<T>(), s[1].cast<T>() }; }));

    // Properties:
    c.def_readwrite(varName0, var0);
    c.def_readwrite(varName1, var1);

    // Formatting:
    c.def("__str__", [var0, var1](const TupleT& t) { return fmt::format("({},{})", t.*var0, t.*var1); });
    c.def("__repr__",
          [typeName, var0, var1](const TupleT& t) { return fmt::format("carb.{}({},{})", typeName, t.*var0, t.*var1); });

    // Pickling:
    c.def(py::pickle(
        // __getstate__
        [var0, var1](const TupleT& t) { return py::make_tuple(t.*var0, t.*var1); },
        // __setstate__
        [](py::tuple t) {
            return TupleT{ t[0].cast<T>(), t[1].cast<T>() };
        }));

    return c;
}

template <typename TupleT, class T>
py::class_<TupleT> defineTuple(py::module& m,
                               const char* typeName,
                               const char* varName0,
                               T TupleT::*var0,
                               const char* varName1,
                               T TupleT::*var1,
                               const char* varName2,
                               T TupleT::*var2,
                               const char* docstring = "")
{
    py::class_<TupleT> c = detail::defineTupleCommon<TupleT, T, 3>(m, typeName, docstring);

    // Ctors:
    c.def(py::init<T, T, T>());
    c.def(py::init([](py::sequence s) -> TupleT { return { s[0].cast<T>(), s[1].cast<T>(), s[2].cast<T>() }; }));

    // Properties:
    c.def_readwrite(varName0, var0);
    c.def_readwrite(varName1, var1);
    c.def_readwrite(varName2, var2);

    // Formatting:
    c.def("__str__",
          [var0, var1, var2](const TupleT& t) { return fmt::format("({},{},{})", t.*var0, t.*var1, t.*var2); });
    c.def("__repr__", [typeName, var0, var1, var2](const TupleT& t) {
        return fmt::format("carb.{}({},{},{})", typeName, t.*var0, t.*var1, t.*var2);
    });

    // Pickling:
    c.def(py::pickle(
        // __getstate__
        [var0, var1, var2](const TupleT& t) { return py::make_tuple(t.*var0, t.*var1, t.*var2); },
        // __setstate__
        [](py::tuple t) {
            return TupleT{ t[0].cast<T>(), t[1].cast<T>(), t[2].cast<T>() };
        }));

    return c;
}

template <typename TupleT, class T>
py::class_<TupleT> defineTuple(py::module& m,
                               const char* type,
                               const char* varName0,
                               T TupleT::*var0,
                               const char* varName1,
                               T TupleT::*var1,
                               const char* varName2,
                               T TupleT::*var2,
                               const char* varName3,
                               T TupleT::*var3,
                               const char* docstring = "")
{
    py::class_<TupleT> c = detail::defineTupleCommon<TupleT, T, 4>(m, type, docstring);

    // Ctors:
    c.def(py::init<T, T, T, T>());
    c.def(py::init([](py::sequence s) -> TupleT {
        return { s[0].cast<T>(), s[1].cast<T>(), s[2].cast<T>(), s[3].cast<T>() };
    }));

    // Properties:
    c.def_readwrite(varName0, var0);
    c.def_readwrite(varName1, var1);
    c.def_readwrite(varName2, var2);
    c.def_readwrite(varName3, var3);

    // Formatting:
    c.def("__str__", [var0, var1, var2, var3](const TupleT& t) {
        return fmt::format("({},{},{},{})", t.*var0, t.*var1, t.*var2, t.*var3);
    });
    c.def("__repr__", [type, var0, var1, var2, var3](const TupleT& t) {
        return fmt::format("carb.{}({},{},{},{})", type, t.*var0, t.*var1, t.*var2, t.*var3);
    });

    // Pickling:
    c.def(py::pickle(
        // __getstate__
        [var0, var1, var2, var3](const TupleT& t) { return py::make_tuple(t.*var0, t.*var1, t.*var2, t.*var3); },
        // __setstate__
        [](py::tuple t) {
            return TupleT{ t[0].cast<T>(), t[1].cast<T>(), t[2].cast<T>(), t[3].cast<T>() };
        }));

    return c;
}

static void log(
    const char* source, int32_t level, const char* fileName, const char* functionName, int lineNumber, const char* message)
{
    if (g_carbLogFn && g_carbLogLevel <= level)
    {
        g_carbLogFn(source, level, fileName, functionName, lineNumber, "%s", message);
    }
}


} // namespace detail

inline void definePythonModule(py::module& m)
{
    //////// Common ////////
    using namespace carb::detail;

    defineTuple<Float2>(m, "Float2", "x", &Float2::x, "y", &Float2::y, R"(
        Pair of floating point values. These can be accessed via the named attributes, `x` & `y`, but
        also support sequence access, making them work where a list or tuple is expected.

        >>> f = carb.Float2(1.0, 2.0)
        >>> f[0]
        1.0
        >>> f.y
        2.0
        )");

    defineTuple<Float3>(
        m, "Float3", "x", &Float3::x, "y", &Float3::y, "z", &Float3::z,
        R"(A triplet of floating point values. These can be accessed via the named attributes, `x`, `y` & `z`, but
        also support sequence access, making them work where a list or tuple is expected.

        >>> v = [1, 2, 3]
        f = carb.Float3(v)
        >>> f[0]
        1.0
        >>> f.y
        2.0
        >>> f[2]
        3.0
        )");

    defineTuple<Float4>(
        m, "Float4", "x", &Float4::x, "y", &Float4::y, "z", &Float4::z, "w", &Float4::w,
        R"(A quadruplet of floating point values. These can be accessed via the named attributes, `x`, `y`, `z` & `w`,
        but also support sequence access, making them work where a list or tuple is expected.

        >>> v = [1, 2, 3, 4]
        f = carb.Float4(v)
        >>> f[0]
        1.0
        >>> f.y
        2.0
        >>> f[2]
        3.0
        >>> f.w
        4.0
        )");

    defineTuple<Int2>(m, "Int2", "x", &Int2::x, "y", &Int2::y);

    defineTuple<Int3>(m, "Int3", "x", &Int3::x, "y", &Int3::y, "z", &Int3::z);

    defineTuple<Int4>(m, "Int4", "x", &Int4::x, "y", &Int4::y, "z", &Int4::z, "w", &Int4::w);

    defineTuple<Uint2>(m, "Uint2", "x", &Uint2::x, "y", &Uint2::y);

    defineTuple<Uint3>(m, "Uint3", "x", &Uint3::x, "y", &Uint3::y, "z", &Uint3::z);

    defineTuple<Uint4>(m, "Uint4", "x", &Uint4::x, "y", &Uint4::y, "z", &Uint4::z, "w", &Uint4::w);

    defineTuple<Double2>(m, "Double2", "x", &Double2::x, "y", &Double2::y);

    defineTuple<Double3>(m, "Double3", "x", &Double3::x, "y", &Double3::y, "z", &Double3::z);

    defineTuple<Double4>(m, "Double4", "x", &Double4::x, "y", &Double4::y, "z", &Double4::z, "w", &Double4::w);

    defineTuple<ColorRgb>(m, "ColorRgb", "r", &ColorRgb::r, "g", &ColorRgb::g, "b", &ColorRgb::b);

    defineTuple<ColorRgbDouble>(
        m, "ColorRgbDouble", "r", &ColorRgbDouble::r, "g", &ColorRgbDouble::g, "b", &ColorRgbDouble::b);

    defineTuple<ColorRgba>(
        m, "ColorRgba", "r", &ColorRgba::r, "g", &ColorRgba::g, "b", &ColorRgba::b, "a", &ColorRgba::a);

    defineTuple<ColorRgbaDouble>(m, "ColorRgbaDouble", "r", &ColorRgbaDouble::r, "g", &ColorRgbaDouble::g, "b",
                                 &ColorRgbaDouble::b, "a", &ColorRgbaDouble::a);


    //////// Python Utils ////////

    py::class_<Subscription, std::shared_ptr<Subscription>>(m, "Subscription", R"(
        Subscription holder.

        This object is returned by different subscription functions. Subscription lifetime is associated with this object. You can
        it while you need subscribed callback to be called. Then you can explicitly make it equal to `None` or call `unsubscribe` method or `del` it to unsubscribe.

        Quite common patter of usage is when you have a class which subscribes to various callbacks and you want to subscription to stay valid while class instance is alive.

        .. code-block:: python

            class Foo:
                def __init__(self):
                    events = carb.events.get_events_interface()
                    stream = events.create_event_stream()
                    self._event_sub = stream.subscribe_to_pop(0, self._on_event)

                def _on_event(self, e):
                    print(f'event {e}')

        >>> f = Foo()
        >>> # f receives some events
        >>> f._event_sub = None
        >>> f = None
        )")
        .def(py::init([](std::function<void()> unsubscribeFn) {
            return std::make_shared<Subscription>(wrapPythonCallback(std::move(unsubscribeFn)));
        }))
        .def("unsubscribe", &Subscription::unsubscribe);


    //////// ILogging ////////

    m.def("log", detail::log, py::arg("source"), py::arg("level"), py::arg("fileName"), py::arg("functionName"),
          py::arg("lineNumber"), py::arg("message"));

    py::module loggingModule = m.def_submodule("logging");
    {
        loggingModule.attr("EXTRA_FIELD_FLAG_NONE") = logging::fExtraFieldFlagNone;
        loggingModule.attr("EXTRA_FIELD_FLAG_GLOBAL") = logging::fExtraFieldFlagGlobal;
        loggingModule.attr("EXTRA_FIELD_FLAG_THREAD") = logging::fExtraFieldFlagThread;

        py::enum_<logging::LogSettingBehavior>(loggingModule, "LogSettingBehavior")
            .value("INHERIT", logging::LogSettingBehavior::eInherit)
            .value("OVERRIDE", logging::LogSettingBehavior::eOverride);

#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 3)
        struct PyLogger : public logging::Logger2
        {
            const logging::ILogging* logging;
            py::function func;
            std::optional<bool> useKwArgs;

            PyLogger(const logging::ILogging* logging, py::function fn) : logging(logging), func(std::move(fn))
            {
                logging->addLogger(this);
            }
            ~PyLogger()
            {
                if (logging)
                {
                    logging->removeLogger(this);
                }
            }
            void handleMessage(const logging::LogMessage& msg) override
            {
                py::gil_scoped_acquire gil;
                static_assert(sizeof(logging::LogMessage) == 96, "Add missing fields");

                // Always try kwargs first
                if (!useKwArgs || useKwArgs.value())
                {
                    const char* globalExtraFields =
                        CARB_INCLUDES_MEMBER(msg.sizeOf, logging::LogMessage::globalExtraFields) ? msg.globalExtraFields :
                                                                                                   "";
                    const char* threadExtraFields =
                        CARB_INCLUDES_MEMBER(msg.sizeOf, logging::LogMessage::threadExtraFields) ? msg.threadExtraFields :
                                                                                                   "";
                    auto kwargs =
                        py::dict("source"_a = msg.source, "filename"_a = msg.fileName ? msg.fileName : "",
                                 "line_number"_a = msg.lineNumber, "level"_a = msg.level,
                                 "module_name"_a = msg.moduleName ? msg.moduleName : "",
                                 "function_name"_a = msg.functionName ? msg.functionName : "", "pid"_a = msg.processId,
                                 "tid"_a = msg.threadId, "trace_parent_id"_a = msg.traceParentId,
                                 "timestamp_ns"_a = msg.timestampNs, "global_extra_fields"_a = globalExtraFields,
                                 "thread_extra_fields"_a = threadExtraFields, "message"_a = msg.message);

                    // We know the function takes kwargs, so just call
                    try
                    {
                        func(**kwargs);
                        useKwArgs.emplace(true);
                        return;
                    }
                    catch (const py::error_already_set& e)
                    {
                        if (!useKwArgs && e.matches(PyExc_TypeError))
                        {
                            // We tried kwargs and it failed; fall back to old positional arguments
                            useKwArgs.emplace(false);
                        }
                        else
                        {
                            CARB_LOG_ERROR("PyLogger(kwargs): %s", e.what());
                            return;
                        }
                    }
                }

                // If we made it to here, we need to send with positional args
                CARB_ASSERT(!useKwArgs.value_or(true));
                try
                {
                    func(msg.source, msg.level, msg.fileName, msg.lineNumber, msg.message);
                }
                catch (const py::error_already_set& e)
                {
                    CARB_LOG_ERROR("PyLogger(positional): %s", e.what());
                }
            }
        };

        py::class_<logging::Logger2, std::unique_ptr<logging::Logger2, py::nodelete>>(loggingModule, "Logger");
        py::class_<PyLogger, logging::Logger2>(loggingModule, "LoggerHandle");
#else
        struct PyLogger : public logging::Logger
        {
            const logging::ILogging* logging;
            py::function func;
            PyLogger(const logging::ILogging* logging, py::function func) : logging(logging), func(std::move(func))
            {
                this->handleMessage = msg;
                logging->addLogger(this);
            }
            ~PyLogger()
            {
                logging->removeLogger(this);
            }

            static void msg(Logger* logger,
                            const char* source,
                            int32_t level,
                            const char* fileName,
                            const char* functionName,
                            int lineNumber,
                            const char* message)
            {
                CARB_UNUSED(functionName);
                py::gil_scoped_acquire gil;
                try
                {
                    static_cast<PyLogger*>(logger)->func(source, level, fileName, lineNumber, message);
                }
                catch (const py::error_already_set& e)
                {
                    CARB_LOG_ERROR("PyLogger: %s", e.what());
                }
            }
        };

        py::class_<logging::Logger>(loggingModule, "Logger");
        py::class_<PyLogger, logging::Logger>(loggingModule, "LoggerHandle");
#endif

        defineInterfaceClass<logging::ILogging>(loggingModule, "ILogging", "acquire_logging")
            .def("set_level_threshold", wrapInterfaceFunction(&logging::ILogging::setLevelThreshold))
            .def("get_level_threshold", wrapInterfaceFunction(&logging::ILogging::getLevelThreshold))
            .def("set_log_enabled", wrapInterfaceFunction(&logging::ILogging::setLogEnabled))
            .def("is_log_enabled", wrapInterfaceFunction(&logging::ILogging::isLogEnabled))
            .def("set_level_threshold_for_source", wrapInterfaceFunction(&logging::ILogging::setLevelThresholdForSource))
            .def("set_log_enabled_for_source", wrapInterfaceFunction(&logging::ILogging::setLogEnabledForSource))
            .def("reset", wrapInterfaceFunction(&logging::ILogging::reset))
            .def("add_logger", [](const logging::ILogging* ls,
                                  py::function logFn) { return std::make_unique<PyLogger>(ls, std::move(logFn)); })
            .def("remove_logger", [](const logging::ILogging*,
                                     PyLogger* logger) { std::exchange(logger->logging, nullptr)->removeLogger(logger); })
#if CARB_VERSION_ATLEAST(carb_logging_ILogging, 1, 4)
            .def("modify_extra_field_value",
                 [](logging::ILogging* ls, const char* key, const char* value, logging::ExtraFieldFlags flags) {
                     return ls->modifyExtraFieldValue(key, value, flags);
                 },
                 py::arg("key"), py::arg("value"), py::arg("flags") = logging::fExtraFieldFlagNone)
            .def("add_extra_field",
                 [](logging::ILogging* ls, const char* key, const char* value, logging::ExtraFieldFlags flags) {
                     return ls->addExtraField(key, value, flags);
                 },
                 py::arg("key"), py::arg("value"), py::arg("flags") = logging::fExtraFieldFlagNone)
            .def("remove_extra_field",
                 [](logging::ILogging* ls, const char* key, logging::ExtraFieldFlags flags) {
                     return ls->removeExtraField(key, flags);
                 },
                 py::arg("key"), py::arg("flags") = logging::fExtraFieldFlagNone)
            .def("has_extra_field",
                 [](logging::ILogging* ls, const char* key, logging::ExtraFieldFlags flags) {
                     return ls->hasExtraField(key, flags);
                 },
                 py::arg("key"), py::arg("flags") = logging::fExtraFieldFlagNone)
#endif
            /**/;

        loggingModule.attr("LEVEL_VERBOSE") = py::int_(logging::kLevelVerbose);
        loggingModule.attr("LEVEL_INFO") = py::int_(logging::kLevelInfo);
        loggingModule.attr("LEVEL_WARN") = py::int_(logging::kLevelWarn);
        loggingModule.attr("LEVEL_ERROR") = py::int_(logging::kLevelError);
        loggingModule.attr("LEVEL_FATAL") = py::int_(logging::kLevelFatal);
    }

    //////// IFileSystem ////////

    py::module filesystemModule = m.def_submodule("filesystem");
    {
        using namespace filesystem;

        py::class_<filesystem::File>(filesystemModule, "File");

        py::enum_<DirectoryItemType>(filesystemModule, "DirectoryItemType")
            .value("FILE", DirectoryItemType::eFile)
            .value("DIRECTORY", DirectoryItemType::eDirectory);

        defineInterfaceClass<IFileSystem>(filesystemModule, "IFileSystem", "acquire_filesystem")
            .def("get_current_directory_path", wrapInterfaceFunction(&IFileSystem::getCurrentDirectoryPath))
            .def("set_current_directory_path", wrapInterfaceFunction(&IFileSystem::setCurrentDirectoryPath))
            .def("get_app_directory_path", wrapInterfaceFunction(&IFileSystem::getAppDirectoryPath))
            .def("set_app_directory_path", wrapInterfaceFunction(&IFileSystem::setAppDirectoryPath))
            .def("exists", wrapInterfaceFunction(&IFileSystem::exists))
            .def("is_directory", wrapInterfaceFunction(&IFileSystem::isDirectory))
            .def("open_file_to_read", wrapInterfaceFunction(&IFileSystem::openFileToRead),
                 py::return_value_policy::reference)
            .def("open_file_to_write", wrapInterfaceFunction(&IFileSystem::openFileToWrite),
                 py::return_value_policy::reference)
            .def("open_file_to_append", wrapInterfaceFunction(&IFileSystem::openFileToAppend),
                 py::return_value_policy::reference)
            .def("close_file", wrapInterfaceFunction(&IFileSystem::closeFile))
            .def("get_file_size", wrapInterfaceFunction(&IFileSystem::getFileSize))
            //.def("get_file_mod_time", wrapInterfaceFunction(&IFileSystem::getFileModTime))
            .def("get_mod_time", wrapInterfaceFunction(&IFileSystem::getModTime))
            //.def("read_file_chunk", wrapInterfaceFunction(&IFileSystem::readFileChunk))
            //.def("write_file_chunk", wrapInterfaceFunction(&IFileSystem::writeFileChunk))
            //.def("read_file_line", wrapInterfaceFunction(&IFileSystem::readFileLine))
            //.def("write_file_line", wrapInterfaceFunction(&IFileSystem::writeFileLine))
            .def("flush_file", wrapInterfaceFunction(&IFileSystem::flushFile))
            .def("make_temp_directory",
                 [](IFileSystem* iface) -> py::object {
                     char buffer[1024];
                     if (iface->makeTempDirectory(buffer, CARB_COUNTOF(buffer)))
                     {
                         return py::str(std::string(buffer));
                     }
                     return py::none();
                 })
            .def("make_directory", wrapInterfaceFunction(&IFileSystem::makeDirectory))
            .def("remove_directory", wrapInterfaceFunction(&IFileSystem::removeDirectory))
            .def("copy", wrapInterfaceFunction(&IFileSystem::copy))
            //.def("for_each_directory_item", wrapInterfaceFunction(&IFileSystem::forEachDirectoryItem))
            //.def("for_each_directory_item_recursive", wrapInterfaceFunction(
            //&IFileSystem::forEachDirectoryItemRecursive))
            // .def("subscribe_to_change_events", wrapInterfaceFunction(
            //&IFileSystem::createChangeSubscription)) .def("unsubscribe_to_change_events", wrapInterfaceFunction(
            //&IFileSystem::destroyChangeSubscription))
            ;
    }

    //////// Framework ////////

    py::enum_<PluginHotReload>(m, "PluginHotReload")
        .value("DISABLED", PluginHotReload::eDisabled)
        .value("ENABLED", PluginHotReload::eEnabled);

    py::class_<PluginImplDesc>(m, "PluginImplDesc")
        .def_readonly("name", &PluginImplDesc::name)
        .def_readonly("description", &PluginImplDesc::description)
        .def_readonly("author", &PluginImplDesc::author)
        .def_readonly("hotReload", &PluginImplDesc::hotReload)
        .def_readonly("build", &PluginImplDesc::build);

    py::class_<Version>(m, "Version")
        .def(py::init<>())
        .def(py::init<uint32_t, uint32_t>())
        .def_readonly("major", &Version::major)
        .def_readonly("minor", &Version::minor)
        .def("__repr__", [](const Version& v) { return fmt::format("v{}.{}", v.major, v.minor); });

    py::class_<InterfaceDesc>(m, "InterfaceDesc")
        .def_readonly("name", &InterfaceDesc::name)
        .def_readonly("version", &InterfaceDesc::version)
        .def("__repr__", [](const InterfaceDesc& d) {
            return fmt::format("\"{} v{}.{}\"", d.name, d.version.major, d.version.minor);
        });

    py::class_<PluginDesc>(m, "PluginDesc")
        .def_readonly("impl", &PluginDesc::impl)
        .def_property_readonly("interfaces",
                               [](const PluginDesc& d) {
                                   return std::vector<InterfaceDesc>(d.interfaces, d.interfaces + d.interfaceCount);
                               })
        .def_property_readonly("dependencies",
                               [](const PluginDesc& d) {
                                   return std::vector<InterfaceDesc>(d.dependencies, d.dependencies + d.dependencyCount);
                               })
        .def_readonly("libPath", &PluginDesc::libPath);


    m.def("get_framework", []() { return getFramework(); }, py::return_value_policy::reference);

    py::class_<Framework>(m, "Framework")
        .def("startup",
             [](const Framework* framework, std::vector<std::string> argv, const char* config,
                std::vector<std::string> initialPluginsSearchPaths, const char* configFormat) {
                 CARB_UNUSED(framework);

                 std::vector<char*> argv_(argv.size());
                 for (size_t i = 0; i < argv.size(); i++)
                 {
                     argv_[i] = (char*)argv[i].c_str();
                 }
                 std::vector<char*> initialPluginsSearchPaths_(initialPluginsSearchPaths.size());
                 for (size_t i = 0; i < initialPluginsSearchPaths.size(); i++)
                 {
                     initialPluginsSearchPaths_[i] = (char*)initialPluginsSearchPaths[i].c_str();
                 }

                 carb::StartupFrameworkDesc startupParams = carb::StartupFrameworkDesc::getDefault();
                 startupParams.configString = config;
                 startupParams.argv = argv_.size() ? argv_.data() : nullptr;
                 startupParams.argc = static_cast<int>(argv_.size());
                 startupParams.initialPluginsSearchPaths =
                     initialPluginsSearchPaths_.size() ? initialPluginsSearchPaths_.data() : nullptr;
                 startupParams.initialPluginsSearchPathCount = initialPluginsSearchPaths_.size();
                 startupParams.configFormat = configFormat;

                 startupFramework(startupParams);
             },
             py::arg("argv") = std::vector<std::string>(), py::arg("config") = nullptr,
             py::arg("initial_plugins_search_paths") = std::vector<std::string>(), py::arg("config_format") = "toml")
        .def("load_plugins",
             [](const Framework* framework, std::vector<std::string> loadedFileWildcards,
                std::vector<std::string> searchPaths) {
                 std::vector<const char*> loadedFileWildcards_(loadedFileWildcards.size());
                 for (size_t i = 0; i < loadedFileWildcards.size(); i++)
                 {
                     loadedFileWildcards_[i] = loadedFileWildcards[i].c_str();
                 }

                 std::vector<const char*> searchPaths_(searchPaths.size());
                 for (size_t i = 0; i < searchPaths.size(); i++)
                 {
                     searchPaths_[i] = searchPaths[i].c_str();
                 }


                 carb::PluginLoadingDesc desc = carb::PluginLoadingDesc::getDefault();
                 desc.loadedFileWildcardCount = loadedFileWildcards_.size();
                 desc.loadedFileWildcards = loadedFileWildcards_.data();
                 if (searchPaths_.size() > 0)
                 {
                     desc.searchPathCount = searchPaths_.size();
                     desc.searchPaths = searchPaths_.data();
                 }

                 framework->loadPluginsEx(desc);
             },
             py::arg("loaded_file_wildcards") = std::vector<std::string>(),
             py::arg("search_paths") = std::vector<std::string>())
        .def("unload_all_plugins", wrapInterfaceFunction(&Framework::unloadAllPlugins))
        .def("get_plugins",
             [](const Framework* framework) {
                 std::vector<PluginDesc> plugins(framework->getPluginCount());
                 framework->getPlugins(plugins.data());
                 return plugins;
             })
        .def("try_reload_plugins", wrapInterfaceFunction(&Framework::tryReloadPlugins))
        .def("start_plugin",
             [](const Framework* framework, const char* plugin) {
                 auto& desc = framework->getPluginDesc(plugin);
                 if (desc.interfaceCount == 0)
                     throw std::runtime_error("Plugin invalid or has no interfaces");
                 if (!framework->tryAcquireInterfaceWithClient(g_carbClientName, desc.interfaces[0], plugin))
                     throw std::runtime_error("Failed to acquire interface");
             },
             py::arg("plugin"), py::call_guard<py::gil_scoped_release>())
        /**/;

    m.def("breakpoint", [] { CARB_BREAK_POINT(); }, R"(
Issues a hardware breakpoint.

Warning: If a native debugger is not attached, this can cause an application
error resulting in a crash.

Args:
    None

Returns:
    None
        )")
        .def("wait_for_native_debugger",
             [](float timeout, bool stop, bool quiet) {
                 if (carb::extras::isDebuggerAttached())
                     return true;
                 using namespace std::chrono;
                 cpp::optional<steady_clock::time_point> timeoutTime;
                 constexpr static float kMaxTimeoutSec = 10 * 24 * 60 * 60; // 10 days
                 if (timeout >= 0)
                 {
                     if (timeout > kMaxTimeoutSec)
                         timeout = kMaxTimeoutSec;
                     timeoutTime.emplace(
                         cpp::detail::absTime<steady_clock>(duration_cast<nanoseconds>(duration<float>(timeout))));
                     if (!quiet)
                         printf("Waiting for debugger for %f seconds...\n", timeout);
                 }
                 else if (!quiet)
                     printf("Waiting for debugger...\n");
                 while (!carb::extras::isDebuggerAttached())
                 {
                     if (timeoutTime && steady_clock::now() >= timeoutTime.value())
                         return false;
                     this_thread::sleepForUs(10000); // 10ms
                 }
                 if (stop)
                     CARB_BREAK_POINT();
                 return true;
             },
             R"(
Waits for a debugger to attach.

Blocks (with GIL released) until a native debugger attaches to the process or a
timeout occurs.

Args:
    timeout: The time in seconds to wait. Negative values mean to wait forever.
             A value of 0 will check if a native debugger is attached without
             waiting. Optional, default value is -1.
    stop:    If True, a breakpoint is triggered immediately after a debugger
             attaches. If a timeout is reached instead, no breakpoint is
             triggered. Optional, default value is False.
    quiet:   When called if a debugger is not already attached a message is
             printed to stdout unless this is True. Optional, default value is
             False.

Returns:
    True if a native debugger attached, False if a timeout is reached.
             )",
             py::call_guard<py::gil_scoped_release>(), py::arg("timeout") = -1.f, py::arg("stop") = false,
             py::arg("quiet") = false)
        /**/;

    py::options options;
    // options.disable_function_signatures();

    m.def("answer_question",
          [](const char* message) {
              CARB_UNUSED(message);

              return std::string("blarg");
          },
          py::arg("question"), R"(
        This function can answer some questions.

        It currently only answers a limited set of questions so don't expect it to know everything.

        Args:
            question: The question passed to the function, trailing question mark is not necessary and
                casing is not important.

        Returns:
            The answer to the question or empty string if it doesn't know the answer.)");
}
} // namespace carb
