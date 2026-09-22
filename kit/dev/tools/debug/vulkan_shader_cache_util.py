#!/usr/bin/python

# Utility to inspect and compare Nvidia Linux Vulkan Driver shader caches

import sys
import re
import struct
import argparse
import os.path
import hashlib

# -------------------------------------
# indexes the vulkan shader cache structure and collects information the caches
class ShaderCacheFolderEntry:
    def __init__(self, driverUUID, deviceHash, appHash):
        self.driverUUID = driverUUID
        self.deviceHash = deviceHash
        self.appHash = appHash
        self.shader_cache = None
    
    def get_name(self):
        return "{}/{}/{}".format(self.driverUUID, self.deviceHash, self.appHash)

    def get_full_path(self, root_path):
        return os.path.join(root_path, self.driverUUID, self.deviceHash, self.appHash+".toc")

    def matches(self, other):
        return (self.driverUUID == other.driverUUID) and (self.deviceHash == other.deviceHash) and (self.appHash == other.appHash)

class ShaderCacheFolderIndexer:    
    def __init__(self, root_path):
        self.root_path = root_path
        self.tocs = []
        self.index()

    def index(self):
        # start with the folder pointing to "GlCache" root
        root_path = os.path.normpath(self.root_path)
        base_dir_name = os.path.basename(root_path)

        if base_dir_name != 'GLCache':
            raise RuntimeError("you must pass the root folder of the shader cache that ends with 'GLCache' ({} | {})".format(root_path, base_dir_name))

        # the cache folder structure is like the following:
        # GLCache/DRIVER_UUID/DEVICE_HASH/APP_HASH.toc|.bin
        self.parse_root_entries(root_path)

    def parse_root_entries(self, root_path):
        driver_uuids = os.listdir(root_path)
        for driverUUID in driver_uuids:
            driver_path = os.path.join(root_path, driverUUID)
            if os.path.isdir(driver_path):
                self.parse_driver_entry(driverUUID, driver_path)

    def parse_driver_entry(self, driverUUID, driver_path):
        print("driver: {}".format(driverUUID))
        devices = os.listdir(driver_path)
        for deviceHash in devices:
            device_path = os.path.join(driver_path, deviceHash)
            if os.path.isdir(device_path):
                self.parse_device_entry(driverUUID, deviceHash, device_path)

    def parse_device_entry(self, driverUUID, deviceHash, device_path):
        print("\t: Device: {}".format(deviceHash))
        apps = os.listdir(device_path)
        for app in apps:
            app_path = os.path.join(device_path, app)
            if os.path.isfile(app_path):
                split_file_name = os.path.splitext(app)
                if split_file_name[1] == ".toc":
                    appHash = split_file_name[0]
                    self.parse_app_entry(driverUUID, deviceHash, appHash, app_path)

    def parse_app_entry(self, driverUUID, deviceHash, appHash, file_path):
        print("\t\t: App: {}".format(appHash))
        entry = ShaderCacheFolderEntry(driverUUID, deviceHash, appHash)
        self.tocs.append(entry)

    def get_matching_entry(self, other_toc):
        for toc in self.tocs:
            if(toc.matches(other_toc)):
                return toc.shader_cache
        return None


# -------------------------------------
# parses an app log with shader module creation messages in the following format
# [shadercache]: ShaderModule creation: 'Prefix Scan Texture: Combine'(entry: 'taskCombineMain'), byteCodeHash: 1f40e998416ddb44, flags: 0x6
class ShaderModuleParser:
    def __init__(self):
        self.shader_module_entries = {}

    # -------------------------------------
    # read log and extract shader module names and matching hashes
    def parse(self, log_file):
        lineregex = re.compile('\[ShaderCache\]\: ShaderModule creation\: \'(.*)\'\(entry\: \'(.*)\'\), byteCodeHash: (.*), flags: (.*)')

        self.shader_module_entries = {}
        with open(log_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                #print(line)
                match = lineregex.search(line)
                if match:                    
                    name = match.group(1)
                    entrypoint = match.group(2)
                    hash = match.group(3)
                    flags = match.group(4)
                    #print("Found shader module: flags:{}, name:\'{}\', entry:\'{}\', hash:\'{}\'".format(flags, name, entrypoint, hash))
                    self.shader_module_entries[hash] = [name, entrypoint, flags]

    # -------------------------------------
    def get_matching_module_entry(self, moduleHash):
        moduleHashStr = "{:x}".format(moduleHash)
        return self.shader_module_entries.get(moduleHashStr)

    # -------------------------------------
    # print shader module index only if requested
    def print_shadermodules(self):
        print("=============== SHADER MODULE INDEX")
        for hash,contents in self.shader_module_entries.items():
            name = contents[0]
            entrypoint = contents[1]
            flags = contents[2]
            print("Shader module: flags:{}, name:\'{}\', entry:\'{}\', hash:\'{}\'".format(flags, name, entrypoint, hash))
      
# -------------------------------------
class TocEntry: 
    def __init__(self, moduleHash, compilerOptionHash, offset, size, matchingModule):
        self.moduleHash = moduleHash
        self.compilerOptionHash = compilerOptionHash
        self.offset = offset
        self.size = size
        self.matchingModule = matchingModule

    def get_contents_to_hash(self):
        return "{}{}{}".format(self.moduleHash, self.compilerOptionHash, self.size)

    def print_entry(self):
        print(" Entry: moduleHash:{:x}, optionsHash:{:x}, offset:{:x}, size:{} [{}]".
                format(self.moduleHash, self.compilerOptionHash, self.offset, self.size, self.matchingModule))

class ShaderCacheParser: 
    def __init__(self, name, toc_file, shaderModules, calculate_combined_hash=False):
        self.name = name
        self.toc_file = toc_file
        self.shaderModules = shaderModules

        self.toc_entries = {}
        self.total_entries = 0
        self.unamed_entries = 0
        self.combinedHash = None

        self.magic = 0
        self.version = 0
        self.deviceHash = 0
        self.driverUUID = ""

        self.parse(calculate_combined_hash)

    # -------------------------------------
    # decode TOC file, and try to match the entries to known shader module names based on the ones read from the log file
    def parse(self, calculate_combined_hash):
        self.total_entries = 0
        self.unamed_entries = 0

        with open(self.toc_file, "rb") as f:
            # Header:
            #NvU32 magic;
            #NvU32 version;
            #NvU64 deviceHash;
            #NvU32 driveruuid[4];
            header = f.read(32)
            self.magic, self.version, self.deviceHash, driveruuid0, driveruuid1, driveruuid2, driveruuid3 = struct.unpack('<IIQIIII', header)
            self.driverUUID = "{:x}{:x}{:x}{:x}".format(driveruuid0, driveruuid1, driveruuid2, driveruuid3)
            #print("Header: magic:{:x}, version:{:x}, deviceHash:{:x}, driverUUID:{}".format(self.magic, self.version, self.deviceHash, self.driverUUID))

            #uint64_t moduleHash; 
            #uint64_t compilerOptionHash;
            #uint32_t offset
            #uint32_t size
            entry = f.read(24)
            while entry:
                self.total_entries = self.total_entries + 1
                moduleHash, compilerOptionHash, offset, size = struct.unpack("=QQII", entry)

                matchingEntry = None

                if self.shaderModules != None:
                    matchingEntry = self.shaderModules.get_matching_module_entry(moduleHash)

                if matchingEntry == None:
                    matchingEntry = "<module_not_found>"
                    self.unamed_entries = self.unamed_entries + 1

                #print(" Entry: moduleHash:{:x}, optionsHash:{:x}, offset:{:x}, size:{} [{}]".format(moduleHash, compilerOptionHash, offset, size, matchingEntry));  
                combined_hash = "{:x}_{:x}".format(moduleHash, compilerOptionHash)
                self.toc_entries[combined_hash] = TocEntry(moduleHash, compilerOptionHash, offset, size, matchingEntry)
                entry = f.read(24)

            # after reading the whole TOC, hash the entries to be able to quicly compare TOCs
            if(calculate_combined_hash):
                combinedHash = hashlib.sha256()
                for key in sorted(self.toc_entries):
                    entry = self.toc_entries[key]
                    md5Hash = hashlib.md5(entry.get_contents_to_hash())
                    combinedHash.update(md5Hash.digest())

                self.combinedHash = combinedHash.hexdigest()

    def get_matching_module_entry(self, moduleHash):
        moduleHashStr = "{:x}".format(moduleHash)
        return self.shader_module_entries.get(moduleHashStr)

    # -------------------------------------
    def print_toc(self, print_entries):        
        print("=============== TOC: {}".format(self.toc_file))
        print("Header: magic:{:x}, version:{:x}, deviceHash:{:x}, driverUUID:{} | combined entry hash: {}".
              format(self.magic, self.version, self.deviceHash, self.driverUUID, self.combinedHash))
        total_size_in_bytes = 0
        for combined_hash,entry in self.toc_entries.items():
            if(print_entries):
                entry.print_entry()
            total_size_in_bytes = total_size_in_bytes + entry.size
        
        if self.total_entries > 0:
            total_size_in_mb = total_size_in_bytes / (1024*1024)
            print("* Statistics: total entries: {} (size: {} Mb), unamed entries: {}, named entries {}".
                  format(self.total_entries, total_size_in_mb, self.unamed_entries, self.total_entries - self.unamed_entries))

    # -------------------------------------
    def compare_to(self, other, print_matches, print_mismatched):
        entries_found_in_other = []
        entries_not_found_in_other = []

        for combined_hash, entry in self.toc_entries.items():
            matched_entry = other.toc_entries.get(combined_hash)
            if matched_entry == None:
                entries_not_found_in_other.append(entry)
            else:
                entries_found_in_other.append(entry)

        mismatched_count = len(entries_not_found_in_other)
        mached_count = self.total_entries - mismatched_count

        match_rate = 0.0 if (self.total_entries == 0) else ((float(mached_count) / float(self.total_entries)) * 100.0)
        print("* TOC {}: total entries: {}, also found in {}: {}, not found in {}: {} (matched: {}%)".
              format(self.name, self.total_entries, other.name, mached_count, other.name, mismatched_count, match_rate))
        if print_matches:
            print("matched entries {}:".format(mached_count))
            for entry in entries_found_in_other:
                entry.print_entry()
        if print_mismatched:
            print("mismatched entries {}:".format(mismatched_count))
            for entry in entries_not_found_in_other:
                entry.print_entry()

    def is_empty(self):
        return (self.total_entries == 0)
        
# -------------------------------------
# main()
parser = argparse.ArgumentParser()
parser.add_argument('-c', action='store_true', help="compare mode")
parser.add_argument('-l', '--log-list', nargs='+', default=[], help="list of log files to use to extract shader module information")
parser.add_argument('-d', '--dir-list', nargs='+', default=[], help="compare 2 shader cache directory structures, starting at the 'GLCache' folder")
parser.add_argument('-f', '--file-list', nargs='+', default=[], help="compare 2 shader cache directory structures, starting at the 'GLCache' folder")
parser.add_argument('-vm', action='store_true', help="print diff matching entries")
parser.add_argument('-vn', action='store_true', help="print diff non matching entries")
parser.add_argument('-verbose', action='store_true', help="verbose mode, print loads of debug info")
args = parser.parse_args()

def index_caches(root_path, shader_modules, name):
    print("=============== CACHE FOLDER INDEXING: {}={}".format(name, root_path))
    cache_indexer = ShaderCacheFolderIndexer(root_path)   
    for entry in cache_indexer.tocs:
        #name = entry.get_name()
        toc_path = entry.get_full_path(root_path)
        entry.shader_cache = ShaderCacheParser(name, toc_path, shader_modules)
        entry.shader_cache.print_toc(args.verbose)
    print("\n")
    return cache_indexer

def toc_diff(toc_a, toc_b, diff_name):
    if(toc_a != None and toc_b != None and toc_a.is_empty() and toc_b.is_empty()):
        return
    print("=============== TOC DIFF: {}".format(diff_name))
    if(toc_b != None):
        toc_a.compare_to(toc_b, args.vm, args.vn)
        toc_b.compare_to(toc_a, args.vm, args.vn)
    else:
        print("* TOC A:{}, does not have a matching entry in try to compare".format(toc_a.toc_file)) 

    
# -------------------------------------
# parse any shader module log files if passed in
shader_modules = None
if len(args.log_list) > 0:
    shader_modules = ShaderModuleParser()
    for log_path in args.log_list:
       shader_modules.parse(log_path) 
    if(args.verbose):
       shader_modules.print_shadermodules()

directory_count = len(args.dir_list)
toc_count = len(args.file_list)

# directory comparisson mode
if (directory_count > 0):      
    dir_a = index_caches(args.dir_list[0], shader_modules, "A")
    if(directory_count == 2):
        dir_b = index_caches(args.dir_list[1], shader_modules, "B")

    if (args.c and (directory_count == 2) ):
        print("=============== TOC directory diff: A={} | B={}".format(args.dir_list[0], args.dir_list[1]))
        for toc_entry in dir_a.tocs:
            toc_b = dir_b.get_matching_entry(toc_entry)
            diff_name = "TOC: {}".format(toc_entry.get_name())
            toc_diff(toc_entry.shader_cache, toc_b, diff_name)

# TOC direct comparisson mode
elif (toc_count > 0):
    toc_a = ShaderCacheParser("A", args.file_list[0], shader_modules)
    if(toc_count == 2):
        toc_b = ShaderCacheParser("B", args.file_list[1], shader_modules)
    if (args.c and (toc_count == 2) ):
        diff_name = "A={} | B={}".format(args.file_list[0],args.file_list[1])
        toc_diff(toc_a, toc_b, diff_name)
