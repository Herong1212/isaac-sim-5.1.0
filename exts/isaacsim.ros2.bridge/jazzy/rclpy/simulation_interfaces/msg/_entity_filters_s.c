// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from simulation_interfaces:msg/EntityFilters.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "simulation_interfaces/msg/detail/entity_filters__struct.h"
#include "simulation_interfaces/msg/detail/entity_filters__functions.h"

#include "rosidl_runtime_c/string.h"
#include "rosidl_runtime_c/string_functions.h"

#include "rosidl_runtime_c/primitives_sequence.h"
#include "rosidl_runtime_c/primitives_sequence_functions.h"

// Nested array functions includes
#include "simulation_interfaces/msg/detail/entity_category__functions.h"
// end nested array functions include
bool simulation_interfaces__msg__entity_category__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * simulation_interfaces__msg__entity_category__convert_to_py(void * raw_ros_message);
bool simulation_interfaces__msg__tags_filter__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * simulation_interfaces__msg__tags_filter__convert_to_py(void * raw_ros_message);
bool simulation_interfaces__msg__bounds__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * simulation_interfaces__msg__bounds__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool simulation_interfaces__msg__entity_filters__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[56];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("simulation_interfaces.msg._entity_filters.EntityFilters", full_classname_dest, 55) == 0);
  }
  simulation_interfaces__msg__EntityFilters * ros_message = _ros_message;
  {  // filter
    PyObject * field = PyObject_GetAttrString(_pymsg, "filter");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->filter, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }
  {  // categories
    PyObject * field = PyObject_GetAttrString(_pymsg, "categories");
    if (!field) {
      return false;
    }
    PyObject * seq_field = PySequence_Fast(field, "expected a sequence in 'categories'");
    if (!seq_field) {
      Py_DECREF(field);
      return false;
    }
    Py_ssize_t size = PySequence_Size(field);
    if (-1 == size) {
      Py_DECREF(seq_field);
      Py_DECREF(field);
      return false;
    }
    if (!simulation_interfaces__msg__EntityCategory__Sequence__init(&(ros_message->categories), size)) {
      PyErr_SetString(PyExc_RuntimeError, "unable to create simulation_interfaces__msg__EntityCategory__Sequence ros_message");
      Py_DECREF(seq_field);
      Py_DECREF(field);
      return false;
    }
    simulation_interfaces__msg__EntityCategory * dest = ros_message->categories.data;
    for (Py_ssize_t i = 0; i < size; ++i) {
      if (!simulation_interfaces__msg__entity_category__convert_from_py(PySequence_Fast_GET_ITEM(seq_field, i), &dest[i])) {
        Py_DECREF(seq_field);
        Py_DECREF(field);
        return false;
      }
    }
    Py_DECREF(seq_field);
    Py_DECREF(field);
  }
  {  // tags
    PyObject * field = PyObject_GetAttrString(_pymsg, "tags");
    if (!field) {
      return false;
    }
    if (!simulation_interfaces__msg__tags_filter__convert_from_py(field, &ros_message->tags)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // bounds
    PyObject * field = PyObject_GetAttrString(_pymsg, "bounds");
    if (!field) {
      return false;
    }
    if (!simulation_interfaces__msg__bounds__convert_from_py(field, &ros_message->bounds)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * simulation_interfaces__msg__entity_filters__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of EntityFilters */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("simulation_interfaces.msg._entity_filters");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "EntityFilters");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  simulation_interfaces__msg__EntityFilters * ros_message = (simulation_interfaces__msg__EntityFilters *)raw_ros_message;
  {  // filter
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->filter.data,
      strlen(ros_message->filter.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "filter", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // categories
    PyObject * field = NULL;
    size_t size = ros_message->categories.size;
    field = PyList_New(size);
    if (!field) {
      return NULL;
    }
    simulation_interfaces__msg__EntityCategory * item;
    for (size_t i = 0; i < size; ++i) {
      item = &(ros_message->categories.data[i]);
      PyObject * pyitem = simulation_interfaces__msg__entity_category__convert_to_py(item);
      if (!pyitem) {
        Py_DECREF(field);
        return NULL;
      }
      int rc = PyList_SetItem(field, i, pyitem);
      (void)rc;
      assert(rc == 0);
    }
    assert(PySequence_Check(field));
    {
      int rc = PyObject_SetAttrString(_pymessage, "categories", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // tags
    PyObject * field = NULL;
    field = simulation_interfaces__msg__tags_filter__convert_to_py(&ros_message->tags);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "tags", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // bounds
    PyObject * field = NULL;
    field = simulation_interfaces__msg__bounds__convert_to_py(&ros_message->bounds);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "bounds", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
