__copyright__ = "Copyright (c) 2023, NVIDIA CORPORATION. All rights reserved."
__license__ = """
NVIDIA CORPORATION and its licensors retain all intellectual property
and proprietary rights in and to this software, related documentation
and any modifications thereto. Any use, reproduction, disclosure or
distribution of this software and related documentation without an express
license agreement from NVIDIA CORPORATION is strictly prohibited.
"""

# GDB Pretty-printers and commands for NVIDIA's Carbonite library
#
# To use, run `source /path/to/carb-gdb-printers.py` in GDB 7.9 or newer, or
# put that in your ~/.gdbinit
#
# This enables pretty-printers for the types listed below in register_printers()
# and commands listed below in register_commands()

import enum
import re

import gdb
import gdb.printing
import gdb.unwinder
from gdb import Frame, UnwindInfo, Value

# Builtin type globals

uint32_t = gdb.lookup_type("uint32_t")
uint64_t = gdb.lookup_type("uint64_t")
size_t = gdb.lookup_type("size_t")
long_t = gdb.lookup_type("long")
const_char_ptr = gdb.lookup_type("char").pointer().const()

# Utility functions


def remove_atomic(val: Value):
    """Returns the internal type of a std::atomic<> or carb::cpp[20]::atomic<>"""
    type = val.type.strip_typedefs()
    if (
        type.name.startswith("std::atomic<")
        or type.name.startswith("carb::cpp::atomic<")
        or type.name.startswith("carb::cpp20::atomic<")
    ):
        return val.cast(val.type.template_argument(0))
    return val


def is_null(val: Value):
    """Tests a value for null"""
    type = val.type.strip_typedefs()
    assert type.code in (
        gdb.TYPE_CODE_PTR,
        gdb.TYPE_CODE_MEMBERPTR,
        gdb.TYPE_CODE_METHODPTR,
    )
    return val == Value(0).cast(type)


def thread_bt(thr: gdb.InferiorThread):
    """Prints the backtrace of a thread"""
    prev = gdb.selected_thread()
    thr.switch()
    gdb.execute("bt")
    prev.switch()


def get_tasking():
    """Attempts to access CarbTaskingDebug or throws an exception if it doesn't exist"""
    try:
        return gdb.parse_and_eval("CarbTaskingDebug")
    except:
        pass
    raise gdb.error("CarbTaskingDebug not found; is carb.tasking in use?")


# These are taken from the libstdc++ pretty printer, and do not appear to be externally accessible
# https://github.com/gcc-mirror/gcc/blob/602e824eec30a7c6792b8b27d61c40f1c1a2714c/libstdc%2B%2B-v3/python/libstdcxx/v6/printers.py
_versioned_namespace = "__8::"


def num_elements(count):
    return "1 element" if count == 1 else f"{count} elements"


def is_specialization_of(x, template_name):
    """
    Test whether a type is a specialization of the named class template.
    The type can be specified as a string or a gdb.Type object.
    The template should be the name of a class template as a string,
    without any 'std' qualification.
    """
    global _versioned_namespace
    if type(x) is gdb.Type:
        x = x.tag
    if _versioned_namespace:
        return re.match("^std::(%s)?%s<.*>$" % (_versioned_namespace, template_name), x) is not None
    return re.match("^std::%s<.*>$" % template_name, x) is not None


def get_template_arg_list(type_obj):
    "Return a type's template arguments as a list"
    n = 0
    template_args = []
    while True:
        try:
            template_args.append(type_obj.template_argument(n))
        except:
            return template_args
        n += 1


def _tuple_impl_get(val):
    "Return the tuple element stored in a _Tuple_impl<N, T> base class."
    bases = val.type.fields()
    if not bases[-1].is_base_class:
        raise ValueError("Unsupported implementation for std::tuple: %s" % str(val.type))
    # Get the _Head_base<N, T> base class:
    head_base = val.cast(bases[-1].type)
    fields = head_base.type.fields()
    if len(fields) == 0:
        raise ValueError("Unsupported implementation for std::tuple: %s" % str(val.type))
    if fields[0].name == "_M_head_impl":
        # The tuple element is the _Head_base::_M_head_impl data member.
        return head_base["_M_head_impl"]
    elif fields[0].is_base_class:
        # The tuple element is an empty base class of _Head_base.
        # Cast to that empty base class.
        return head_base.cast(fields[0].type)
    else:
        raise ValueError("Unsupported implementation for std::tuple: %s" % str(val.type))


def tuple_get(n, val):
    "Return the result of std::get<n>(val) on a std::tuple"
    tuple_size = len(get_template_arg_list(val.type))
    if n > tuple_size:
        raise ValueError("Out of range index for std::get<N> on std::tuple")
    # Get the first _Tuple_impl<0, T...> base class:
    node = val.cast(val.type.fields()[0].type)
    while n > 0:
        # Descend through the base classes until the Nth one.
        node = node.cast(node.type.fields()[0].type)
        n -= 1
    return _tuple_impl_get(node)


def unique_ptr_get(val):
    "Return the result of val.get() on a std::unique_ptr"
    # std::unique_ptr<T, D> contains a std::tuple<D::pointer, D>,
    # either as a direct data member _M_t (the old implementation)
    # or within a data member of type __uniq_ptr_data.
    impl_type = val.type.fields()[0].type.strip_typedefs()
    # Check for new implementations first:
    if is_specialization_of(impl_type, "__uniq_ptr_data") or is_specialization_of(impl_type, "__uniq_ptr_impl"):
        tuple_member = val["_M_t"]["_M_t"]
    elif is_specialization_of(impl_type, "tuple"):
        tuple_member = val["_M_t"]
    else:
        raise ValueError("Unsupported implementation for unique_ptr: %s" % str(impl_type))
    return tuple_get(0, tuple_member)


# end copied code


def get_thread_running_fiber(fiber: Value):
    if fiber.type.strip_typedefs().code != gdb.TYPE_CODE_PTR:
        fiber = fiber.address
    tasking = get_tasking()
    num_threads = tasking["m_threadCount"]
    all_tls = unique_ptr_get(tasking["m_tlsData"])
    for i in range(num_threads):
        tls = all_tls[i]
        if tls["currentFiber"] == fiber:
            # Need to resolve this to a gdb.InferiorThread object
            thr_arr = unique_ptr_get(tasking["m_threads"])
            if is_null(thr_arr):
                return None  # omni.job?
            thr = thr_arr[i].cast(size_t)
            inf = gdb.selected_inferior()
            if hasattr(inf, "thread_from_handle"):
                return inf.thread_from_handle(thr)
            else:
                return inf.thread_from_thread_handle(thr)
    return None


class FContext: ...


class FrameId(object):
    def __init__(self, sp, pc):
        self.sp = sp
        self.pc = pc


###############################################################################
### ENUMS
###############################################################################


class TaskPriority(enum.IntFlag):
    ePriorityLow = 0
    ePriorityMed = 1
    ePriorityHigh = 2
    ePriorityMain = 3

    ePriorityMask = 0x7


class TaskFlags(enum.IntFlag):
    eFlagFiberless = 1 << 26
    eFlagPinned = 1 << 27
    eFlagTaskWaiting = 1 << 28
    eFlagPrereqsMet = 1 << 29
    eFlagFinished = 1 << 30
    eFlagStarted = 1 << 31


class FiberState(enum.IntFlag):
    eCreated = 0
    eAssigned = 1
    eRunning = 2
    eSuspended = 3
    eFinished = 4
    eStateMask = 0x7


class FiberFlag(enum.IntFlag):
    eFlagThreadFiber = 1 << 25
    eFlagReady = 1 << 26
    eFlagWaiting = 1 << 27
    eFlagNoWake = 1 << 28
    eFlagWoken = 1 << 29
    eFlagOnThread = 1 << 31


###############################################################################
### TYPE HELPERS
###############################################################################


class HandleDatabase:
    def __init__(self, val: Value):
        self.val = val
        self.entries = {}
        self.value_t = val.type.template_argument(0)
        self.key_t = val.type.template_argument(1)

        if hasattr(val.type.fields, "m_database"):  # Old style
            self.db = val["m_database"]
            # Read the entries
            iter = 0
            max = 1
            self.BUCKETS = 31  # kBuckets
            while iter < self.BUCKETS:
                ptr = remove_atomic(self.db[iter])
                if is_null(ptr):
                    break

                # Inner loop to gather the entries
                for inner in range(max):
                    self.try_add_entry(max - 1 + inner, ptr[inner])

                max = max * 2
                iter = iter + 1

        else:
            self.FIRST_BUCKET_POP = 16  # kFirstBucketPop
            self.FIRST_BUCKET_BITS = 4  # _kFirstBucketBits
            try:
                self.INDEX_BITS = int(val.type.template_argument(3))  # kIndexBits
                self.LIFECYCLE_BITS = int(val.type.template_argument(4))  # kLifecycleBits
                self.BUCKETS = self.INDEX_BITS - self.FIRST_BUCKET_BITS + 1  # kBuckets
                self.ROLLOVER_FLAG = 1 << (self.LIFECYCLE_BITS - 1)  # kRolloverFlag
            except gdb.Error:
                self.INDEX_BITS = 32
                self.LIFECYCLE_BITS = 32
                self.BUCKETS = 28
                self.ROLLOVER_FLAG = 0x80000000
            self.LIFECYCLE_MASK = self.ROLLOVER_FLAG - 1

            self.db = val["m_bucket"]

            def bucketSize(bucket):
                return self.FIRST_BUCKET_POP if bucket == 0 else 1 << (bucket + self.FIRST_BUCKET_BITS - 1)

            iter = 0
            buckets = self.BUCKETS  # kBuckets
            for iter in range(buckets):
                ptr = remove_atomic(self.db[iter])
                if is_null(ptr):
                    break

                # Inner loop
                max = bucketSize(iter)
                for inner in range(max):
                    self.try_add_entry(inner + (0 if iter == 0 else max), ptr[inner])

    def makeHandle(self, index: int, lifecycle: int):
        return index | ((lifecycle & self.LIFECYCLE_MASK) << self.INDEX_BITS)

    def try_add_entry(self, offset, val: Value):
        meta = val["metadata"].cast(uint64_t)
        refs = meta & 0xFFFFFFFF
        if refs != 0:
            id = self.makeHandle(offset, meta >> 32)
            self.entries[int(id)] = (
                val["val"].address.cast(self.value_t.pointer()),
                int(refs),
            )


class TLHandleDatabase:
    def __init__(self, val: Value):
        self.val = val
        self.slabs = val["m_slabs"]
        self.entries = {}
        self.value_t = val.type.template_argument(0)
        self.key_t = val.type.template_argument(1)
        self.entriesPerSlab = val["kNumDataPerSlab"]

        # Walk the slabs
        iter = 0
        max = 1
        buckets = 31
        for iter in range(31):
            slabArray = remove_atomic(self.slabs[iter])
            if is_null(slabArray):
                break

            for inner in range(max):
                slab = slabArray[inner]
                if not is_null(slab):
                    data = slab["data"]
                    base = slab["baseIndex"]
                    for index in range(self.entriesPerSlab):
                        val = data[index]
                        meta = val["metadata"].cast(uint64_t)
                        refs = meta & 0xFFFFFFFF
                        if refs != 0:
                            id = (meta & 0xFFFFFFFF00000000) + base + index
                            self.entries[int(id)] = (
                                val["val"].address.cast(self.value_t.pointer()),
                                int(refs),
                            )
            max = max * 2


class TaskBundle:
    def __init__(self, val: Value):
        self.val = val
        name = Value(val["m_name"].cast(size_t) & 0x7FFFFFFFFFFFFFFF).cast(const_char_ptr)
        self.name = str(name) if not is_null(name) else "<not set>"
        self.name_or_none = str(name) if not is_null(name) else None
        flags = int(remove_atomic(val["m_flags"]))
        try:
            self.priority = TaskPriority(int(remove_atomic(val["m_priority"])))
            self.flags = flags
        except:
            self.priority = TaskPriority(flags & TaskPriority.ePriorityMask)
            self.flags = TaskFlags(flags & ~TaskPriority.ePriorityMask)
        if self.flags & TaskFlags.eFlagTaskWaiting != 0:
            self.state = "waiting"
        elif self.flags & TaskFlags.eFlagFinished != 0:
            self.state = "finished/canceled"
        elif self.flags & TaskFlags.eFlagStarted != 0:
            self.state = "running"
        elif self.flags & TaskFlags.eFlagPrereqsMet != 0:
            self.state = "new"
        else:
            self.state = "pending"
        self.task = val["task"]
        self.cancel = val["cancel"]

    def is_running(self):
        return self.flags & (TaskFlags.eFlagStarted | TaskFlags.eFlagFinished) == TaskFlags.eFlagStarted


class FiberUnwinder(gdb.unwinder.Unwinder):
    def __init__(self, f: Frame, ctx: FContext):
        super().__init__("FiberUnwinder")
        self.f = f
        self.ctx = ctx
        self.pc = f.read_register("pc")
        self.sp = f.read_register("sp")

    def __call__(self, pending_frame: Frame):
        pc = pending_frame.read_register("pc")
        sp = pending_frame.read_register("sp")
        is_fiber = pc == self.pc and sp == self.sp
        # TOOD: aarch64: this crashes gdb 8.1.1 :-/
        if is_fiber:
            info = pending_frame.create_unwind_info(FrameId(self.ctx.values["sp"], self.ctx.values["pc"]))
            for k, v in self.ctx.values.items():
                info.add_saved_register(k, v)
            return info
        return None


class FContext:
    def __init__(self, ptr):
        self.ptr = ptr
        self.arch = gdb.newest_frame().architecture()  # older versions don't have Inferior.architecture()
        self.values = {}
        registers = self.ptr.cast(uint64_t.pointer())
        if self.arch.name() == "aarch64":
            # ignore floating point registers
            self.values["x19"] = registers[8]
            self.values["x20"] = registers[9]
            self.values["x21"] = registers[10]
            self.values["x22"] = registers[11]
            self.values["x23"] = registers[12]
            self.values["x24"] = registers[13]
            self.values["x25"] = registers[14]
            self.values["x26"] = registers[15]
            self.values["x27"] = registers[16]
            self.values["x28"] = registers[17]
            self.values["x29"] = registers[18]  # fp
            self.values["x30"] = registers[19]  # lr
            self.values["pc"] = registers[20]
            self.values["sp"] = self.ptr
        else:
            self.values["r12"] = registers[1]
            self.values["r13"] = registers[2]
            self.values["r14"] = registers[3]
            self.values["r15"] = registers[4]
            self.values["rbx"] = registers[5]
            self.values["rbp"] = registers[6]
            self.values["rip"] = self.values["pc"] = registers[7]
            self.values["rsp"] = self.values["sp"] = self.ptr

    def backtrace(self):
        orig = gdb.selected_frame()
        gdb.newest_frame().select()
        unwinder = FiberUnwinder(gdb.selected_frame(), self)
        gdb.unwinder.register_unwinder(None, unwinder, True)
        gdb.execute("bt")
        try:
            orig.select()
        except Exception as e:
            print(f"Exception: {e}")
            pass
        gdb.frame_unwinders.remove(unwinder)
        gdb.invalidate_cached_frames()


class Fiber:
    def __init__(self, val: Value):
        if not hasattr(Fiber, "base_type"):
            setattr(Fiber, "base_type", gdb.lookup_type("carb::tasking::BaseFiber"))
            setattr(Fiber, "flag_type", gdb.lookup_type("carb::tasking::FiberFlags"))
            setattr(Fiber, "task_type", gdb.lookup_type("carb::tasking::TaskBundle").pointer())
        if val.type.code == gdb.TYPE_CODE_PTR:
            val = val.dereference()
        self.val = val
        self.base = val.cast(Fiber.base_type)
        self.flags = int(remove_atomic(self.val["m_flags"]))
        self.context = FContext(self.base["m_context"])
        self.state = FiberState(self.flags & FiberState.eStateMask)
        self.flags = FiberFlag(self.flags & ~FiberState.eStateMask)
        self.task = self.val["m_context"].cast(Fiber.task_type)


###############################################################################
### PRINTERS
###############################################################################


class RStringPrinter:
    def __init__(self, val: Value):
        self.val = val
        self.viz = gdb.parse_and_eval("::carb::detail::rstring::Visualizer")

    def to_string(self):
        id = self.val["m_stringId"]
        if id > 2097152:
            return f"Invalid {self.val.type.name} (ID {id})"
        entry = self.viz[id / 16384][id % 16384]
        # embedded nulls are allowed, so process them here so we can print them
        s = entry["m_string"].string(length=entry["m_stringLen"], errors="ignore").replace("\0", "\\000")
        if self.val.type.name.endswith("Key"):
            num = self.val["m_number"]
            if num != 0:
                s = s + "_" + str(num)
        return f'{self.val.type.name} (ID {id}) "{s}"'


class HandleDatabasePrinter:
    def __init__(self, val: Value):
        self.db = TLHandleDatabase(val) if "ThreadLocalHandleDatabase" in val.type.name else HandleDatabase(val)

    def __iter__(self):
        self.which = iter(self.db.entries.items())
        return self

    def __next__(self):
        k, t = next(self.which)
        return (f"{k} (value at {t[0]})", t[0].dereference())

    def children(self):
        return iter(self)

    def to_string(self):
        return f"{self.db.val.type.name} at {self.db.val.address} with {num_elements(len(self.db.entries))}"


class TaskFlagsPrinter:
    CHILDREN = [s for s in TaskFlags]

    def __init__(self, val):
        self.val = val
        self.flags = TaskFlags(int(self.val) & ~TaskPriority.ePriorityMask)

    def __iter__(self):
        self.which = iter(self.CHILDREN)
        return self

    def __next__(self):
        n = next(self.which)
        return (n.name, bool(self.flags & n.value))

    def children(self):
        return iter(self)

    def to_string(self):
        return self.val.type.name


class TaskBundlePrinter:
    def name(self):
        return self.tb.name

    def taskFunction(self):
        return self.tb.task

    def taskArgument(self):
        return self.val["taskArg"]

    def priority(self):
        return self.tb.priority.name

    def flags(self):
        val = remove_atomic(self.val["m_flags"]).cast(gdb.lookup_type("carb::tasking::TaskFlags"))
        return val
        s = ""
        for v in TaskFlags:
            if val & v.value:
                s = s + (" | " if len(s) else "") + v.name
        return s

    def cancelFunction(self):
        return self.tb.cancel

    def prereq(self):
        return self.val["m_prerequisite"]

    def fiber(self):
        return remove_atomic(self.val["m_fiber"])

    CHILDREN = {
        "[name]": name,
        "[task function]": taskFunction,
        "[task argument]": taskArgument,
        "[priority]": priority,
        "[flags]": flags,
        "[cancellation function]": cancelFunction,
        "[prereq]": prereq,
        "[fiber]": fiber,
    }

    def __init__(self, val):
        self.val = val
        self.tb = TaskBundle(val)

    def __iter__(self):
        self.which = iter(TaskBundlePrinter.CHILDREN)
        return self

    def __next__(self):
        n = next(self.which)
        fn = TaskBundlePrinter.CHILDREN[n]
        return (n, fn(self))

    def children(self):
        return iter(self)

    def to_string(self):
        return f"{self.val.type.name} at {self.val.address}"


class FiberFlagsPrinter:
    CHILDREN = [FiberState.eStateMask] + [s for s in FiberFlag]

    def __init__(self, val):
        self.val = val
        self.state = FiberState(int(self.val) & FiberState.eStateMask)
        self.flags = FiberFlag(int(self.val) & ~FiberState.eStateMask)

    def __iter__(self):
        self.which = iter(self.CHILDREN)
        return self

    def __next__(self):
        n = next(self.which)
        if n == FiberState.eStateMask:
            return ("[state]", self.state.name)
        return (n.name, bool(self.flags & n.value))

    def children(self):
        return iter(self)

    def to_string(self):
        return self.val.type.name


class FiberPrinter:
    "Print a carb::tasking::Fiber"

    def flags(self):
        return remove_atomic(self.f.val["m_flags"]).cast(gdb.lookup_type("carb::tasking::FiberFlags"))

    def task(self):
        return self.f.task

    def fls(self):
        return self.f.val["m_flsSlots"]

    CHILDREN = {"flags": flags, "task": task, "fls": fls}

    def __init__(self, val):
        self.f = Fiber(val)

    def __iter__(self):
        self.which = iter(FiberPrinter.CHILDREN)
        return self

    def __next__(self):
        p = next(self.which)
        fn = FiberPrinter.CHILDREN[p]
        return (p, fn(self))

    def children(self):
        return iter(self)

    def to_string(self):
        return self.f.val.type.name


class BacktracePrinter:
    def __init__(self, val):
        self.val = val

    def __iter__(self):
        self.which = iter(range(self.val["m_size"]))
        return self

    def __next__(self):
        i = next(self.which)
        return (str(i), self.val["m_stack"][i])

    def children(self):
        return iter(self)

    def to_string(self):
        return f"{self.val.type.name} at {self.val.address}"


class TaskBacktracePrinter:
    def __init__(self, val):
        self.val = val

    def to_string(self):
        return f"{self.val.type.name} at {self.val.address}"

    def children(self):
        return iter(self)

    def __iter__(self):
        self.initial = True
        return self

    def __next__(self):
        if self.initial:
            self.initial = False
            self.which = iter(range(self.val["waitingSize"]))
            return ("[creation]", self.val.cast(gdb.lookup_type("carb::tasking::Backtrace")))
        p = next(self.which)
        return (f"[waiting frame {p}]", self.val["waiting"][p])


###############################################################################
### COMMANDS
###############################################################################


class FiberCmd(gdb.Command):
    """Collection of commands for carb::tasking fibers"""

    def __init__(self):
        super().__init__("fiber", gdb.COMMAND_USER, prefix=True)


class FiberBTCmd(gdb.Command):
    """Prints the backtrace of a carb::tasking::Fiber"""

    def __init__(self):
        super().__init__("fiber bt", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        if not hasattr(FiberBTCmd, "fiber_t"):
            setattr(FiberBTCmd, "fiber_t", gdb.lookup_type("carb::tasking::Fiber"))
        val = gdb.parse_and_eval(arg)
        fiber_t = FiberBTCmd.fiber_t
        if val.type == long_t:
            val = val.cast(fiber_t.pointer())
        if val.type.code == gdb.TYPE_CODE_PTR:
            val = val.dereference()

        try:
            if not val.type.name.startswith("carb::tasking::"):
                raise Exception()

            if val.type.name == "carb::tasking::Fiber":
                fiber = Fiber(val)
            elif val.type.name != "carb::tasking::BaseFiber":
                raise Exception()
            fiber = Fiber(val.cast(fiber_t))
        except:
            print(f"Type {val.type.name} is not a carb::tasking::[Base]Fiber or pointer")
            return
        if fiber.flags & FiberFlag.eFlagOnThread:
            thr = get_thread_running_fiber(fiber.val)
            if thr:
                print(
                    f"Fiber {fiber.val.address} is running in thread {thr.global_num} (LWP {thr.ptid[1]}) ({thr.name})"
                )
                thread_bt(thr)
                return
            # Couldn't find the thread running
            print(
                "Warning! Fiber state is currently running but thread not found; backtrace based on fiber may not be correct"
            )
        print(f"Backtrace of fiber at {fiber.val.address} (frame 0 may not be correct)")
        fiber.context.backtrace()

        print(f"Backtrace of carb::tasking::BaseFiber at {val.address} (frame 0 may not be correct)")

        context = FContext(val["m_context"])
        context.backtrace()


class FiberListCmd(gdb.Command):
    """Lists all fibers in carb.tasking"""

    def __init__(self):
        super().__init__("fiber list", gdb.COMMAND_USER)

    def fiber_string(self, fiber: Fiber, *args):
        s = f"{fiber.val.address}"
        if len(args):
            s = s + f" [{args[0]}]"
        s = s + f" - {fiber.state.name}"
        if not is_null(fiber.task):
            tb = TaskBundle(fiber.task)
            s = s + f" with task {fiber.task}"
            if tb.name_or_none:
                s = s + f" ({tb.name_or_none})"
            s = s + f" ({tb.task})"
        elif fiber.state == FiberState.eRunning:
            s = s + " but between tasks"

        if fiber.flags & FiberFlag.eFlagOnThread:
            thr = get_thread_running_fiber(fiber.val)
            if thr:
                s = s + f" on thread {thr.global_num} (LWP {thr.ptid[1]})"
            else:
                s = s + " on-thread flag set but thread not found"
        return s

    def gather_fibers(self, slab: Value):
        fibers = {}
        # Look up the kFibersPerSlab constant variable
        if not hasattr(FiberListCmd, "kFibersPerSlab"):
            setattr(FiberListCmd, "kFibersPerSlab", gdb.parse_and_eval("carb::tasking::kFibersPerSlab"))

        if slab["freeCount"] != FiberListCmd.kFibersPerSlab:
            fiberArray = slab["fibers"]
            for index in range(FiberListCmd.kFibersPerSlab):
                fiber = Fiber(fiberArray[index])
                if fiber.state != FiberState.eCreated:
                    fibers[fiber.val.address] = fiber
        return fibers

    def invoke(self, arg, from_tty):
        print("Main thread fiber and all worker thread fibers are not included")

        tasking = get_tasking()

        main_fiber = tasking["m_mainThreadFiber"]
        print(self.fiber_string(Fiber(main_fiber), "main fiber"))

        num_threads = tasking["m_threadCount"]
        all_tls = unique_ptr_get(tasking["m_tlsData"])

        # Print the thread fibers
        fibers = {}
        for i in range(num_threads):
            tls = all_tls[i]
            thread_fiber = tls["threadFiber"]
            if not is_null(thread_fiber):
                print(self.fiber_string(Fiber(thread_fiber), "thread fiber"))

            # Walk the thread's fiber slabs
            next = tls["slabHead"]
            while not is_null(next):
                fibers |= self.gather_fibers(next)
                next = next["pnext"]

        # Walk the external fiber slabs
        fiberDb = tasking["m_fiberDb"]
        next = fiberDb["m_externalHead"]
        while not is_null(next):
            fibers |= self.gather_fibers(next)
            next = next["pnext"]

        for f in fibers.values():
            print(self.fiber_string(f))


class TaskCmd(gdb.Command):
    """Collection of commands for carb.tasking tasks"""

    def __init__(self):
        super().__init__("task", gdb.COMMAND_USER, prefix=True)


class TaskListCmd(gdb.Command):
    """Lists all tasks in carb.tasking"""

    def __init__(self):
        super().__init__("task list", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        tasking = get_tasking()
        taskHandleDb = tasking["m_taskHandleDb"]
        db = (
            TLHandleDatabase(taskHandleDb)
            if "ThreadLocalHandleDatabase" in taskHandleDb.type.name
            else HandleDatabase(taskHandleDb)
        )
        if len(db.entries) == 0:
            print("** No tasks")
            return
        print("carb.tasking mapping of TaskContext: <ptr> <state> [name] <task function>:")
        for k, tp in db.entries.items():
            tb = TaskBundle(tp[0])
            print(f"{k}: {tb.val} {tb.state} [{tb.name}] {tb.task}")


class TaskThreadsCmd(gdb.Command):
    """Lists all tasking threads and what they're running"""

    def __init__(self):
        super().__init__("task threads", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        tasking = get_tasking()
        thread_count = tasking["m_threadCount"]
        all_threads = unique_ptr_get(tasking["m_threads"])
        if is_null(all_threads):
            print("Command not supported when running with omni::job")
            return
        all_tls = unique_ptr_get(tasking["m_tlsData"])
        for i in range(thread_count):
            if hasattr(gdb.selected_inferior(), "thread_from_handle"):
                thr = gdb.selected_inferior().thread_from_handle(all_threads[i].cast(size_t))
            else:
                thr = gdb.selected_inferior().thread_from_thread_handle(all_threads[i].cast(size_t))
            tls = all_tls[i]
            s = f"{i}: {thr.global_num} (LWP {thr.ptid[1]}) {thr.name}: "
            if tls["currentFiber"] == tls["threadFiber"]:
                s = s + "idle"
            else:
                fiber = tls["currentFiber"]
                if not is_null(fiber["m_context"]):
                    tb = TaskBundle(fiber["m_context"].cast(gdb.lookup_type("carb::tasking::TaskBundle").pointer()))
                    s = (
                        s
                        + f"running task at {tb.val.address} [{tb.name}] {tb.task} (fiber {fiber.dereference().address})"
                    )
                else:
                    s = s + f"running fiber {fiber.dereference().address} without a task (may be context switching)"
            print(s)


class TaskAggregateCmd(gdb.Command):
    """Lists an aggregation of all tasks current scheduled"""

    def __init__(self):
        super().__init__("task aggregate", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        tasking = get_tasking()
        val = tasking["m_taskHandleDb"]
        db = TLHandleDatabase(val) if "ThreadLocalHandleDatabase" in val.type.name else HandleDatabase(val)
        if len(db.entries) == 0:
            print("** No tasks")
            return
        print("Count of all carb.tasking tasks by task function:")
        mapping = {}
        for tp in db.entries.values():
            tb = TaskBundle(tp[0])
            mapping[int(tb.task)] = (mapping.get(int(tb.task)) or 0) + 1
        fn_t = gdb.lookup_type("carb::tasking::OnTaskFn")
        for k, v in mapping.items():
            print(f"{Value(k).cast(fn_t)}: {v}")


class TaskCreationBTCmd(gdb.Command):
    """Prints a backtrace for the creation of a given task"""

    def __init__(self):
        super().__init__("task creationbt", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        tasking = get_tasking()
        val = tasking["m_taskHandleDb"]
        db = TLHandleDatabase(val) if "ThreadLocalHandleDatabase" in val.type.name else HandleDatabase(val)
        context = int(gdb.parse_and_eval(arg))
        tp = db.entries.get(context)
        if not tp:
            print(f"Task specified by {arg} not found. Use 'task list' to list all tasks")
            return
        tb = TaskBundle(tp[0])
        bt = tb.val["m_backtrace"]
        if is_null(bt):
            print(
                f"Task {context} does not have a creation backtrace. Is /plugins/carb.tasking.plugin/debugTaskBacktrace on?"
            )
            return
        print(bt.cast(gdb.lookup_type("carb::tasking::Backtrace").pointer()).dereference())


class TaskBTCmd(gdb.Command):
    """Prints a backtrace for a given task"""

    def __init__(self):
        super().__init__("task bt", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        tasking = get_tasking()
        val = tasking["m_taskHandleDb"]
        db = TLHandleDatabase(val) if "ThreadLocalHandleDatabase" in val.type.name else HandleDatabase(val)
        context = int(gdb.parse_and_eval(arg))
        tp = db.entries.get(context)
        if not tp:
            print(f"Task specified by {arg} not found. Use 'task list' to list all tasks")
            return
        tb = TaskBundle(tp[0])
        fiber = remove_atomic(tb.val["m_fiber"])
        if is_null(fiber):
            print(f"Task {context} has not started (no fiber assigned)")
            return
        fiber = Fiber(fiber)
        if tb.is_running() and fiber.flags & FiberFlag.eFlagOnThread:
            thr = get_thread_running_fiber(fiber.val)
            if thr:
                print(f"Task {context} is running in thread {thr.global_num} (LWP {thr.ptid[1]}) ({thr.name})")
                prev = gdb.selected_thread()
                thr.switch()
                gdb.execute("bt")
                prev.switch()
                return
            # Couldn't find the thread running it
            print(
                "Warning! Task fiber is currently running but thread not found; backtrace based on fiber may not be correct"
            )
        fctx = fiber.context
        print(f"Backtrace of task {context} (Fiber at address {fiber.val.address}; frame 0 may not be correct)")
        fctx.backtrace()


# Register commands
def register_commands():
    FiberCmd()  # 'fiber' prefix
    FiberBTCmd()  # 'fiber bt'
    FiberListCmd()  # 'fiber list'
    TaskCmd()  # 'task' prefix
    TaskListCmd()  # 'task list'
    TaskAggregateCmd()  # 'task aggregate'
    TaskThreadsCmd()  # 'task threads'
    TaskCreationBTCmd()  # 'task creationbt'
    TaskBTCmd()  # 'task bt'


# Register printers
def register_printers():
    pp = gdb.printing.RegexpCollectionPrettyPrinter("Carbonite")
    pp.add_printer("RString", "^carb::RString(U|Key|UKey)?$", RStringPrinter)
    pp.add_printer("HandleDatabase", "^carb::extras::HandleDatabase<.*?>$", HandleDatabasePrinter)
    pp.add_printer(
        "ThreadLocalHandleDatabase", "^carb::tasking::ThreadLocalHandleDatabase<.*?>$", HandleDatabasePrinter
    )
    pp.add_printer("FiberFlags", "^carb::tasking::FiberFlags$", FiberFlagsPrinter)
    pp.add_printer("TaskFlags", "^carb::tasking::TaskFlags$", TaskFlagsPrinter)
    pp.add_printer("Fiber", "^carb::tasking::Fiber$", FiberPrinter)
    pp.add_printer("TaskBundle", "^carb::tasking::TaskBundle$", TaskBundlePrinter)
    pp.add_printer("Backtrace", "^carb::tasking::Backtrace$", BacktracePrinter)
    pp.add_printer("TaskBacktrace", "^carb::tasking::TaskBundle::TaskBacktrace$", TaskBacktracePrinter)
    return pp


gdb.printing.register_pretty_printer(None, register_printers(), True)
register_commands()
