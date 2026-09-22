
# Copyright (c) 2018-2024, NVIDIA CORPORATION.  All rights reserved.
#
# NVIDIA CORPORATION and its licensors retain all intellectual property
# and proprietary rights in and to this software, related documentation
# and any modifications thereto.  Any use, reproduction, disclosure or
# distribution of this software and related documentation without an express
# license agreement from NVIDIA CORPORATION is strictly prohibited.
#
__all__ = ["OmniClientWrapper"]

import os
import carb
import omni.client

import stat


def _encode_content(content):
    if type(content) == str:
        payload = bytes(content.encode("utf-8"))
    elif type(content) != type(None):
        payload = bytes(content)
    else:
        payload = bytes()

    return payload


class OmniClientWrapper:  # pragma: no cover
    @staticmethod
    async def exists(path):
        try:
            result, entry = await omni.client.stat_async(path)
            return result == omni.client.Result.OK
        except Exception:
            return False

    @staticmethod
    def exists_sync(path):
        try:
            result, entry = omni.client.stat(path)
            return result == omni.client.Result.OK
        except Exception:
            return False

    @staticmethod
    async def write(path: str, content):
        carb.log_info(f"Writing {path}...")
        try:
            result = await omni.client.write_file_async(path, _encode_content(content))
            if result != omni.client.Result.OK:
                carb.log_warn(f"Cannot write {path}, error code: {result}.")
                return False
        except Exception as e:
            carb.log_warn(f"Cannot write {path}: {str(e)}.")
            return False
        finally:
            carb.log_info(f"Writing {path} done...")

        return True

    @staticmethod
    async def delete(path: str):
        carb.log_info(f"Removing {path}...")
        try:
            result = await omni.client.delete_async(path)
            if result != omni.client.Result.OK:
                carb.log_warn(f"Cannot remove {path}, error code: {result}.")
                return False
        except Exception:
            carb.log_warn(f"Cannot delete {path}: {str(e)}.")
            return False

        return True

    @staticmethod
    async def set_write_permission(src_path: str):
        # It can change ACIs for o
        url = omni.client.break_url(src_path)

        # Local path
        try:
            if url.is_raw:
                st = os.stat(src_path)
                os.chmod(src_path, st.st_mode | stat.S_IWRITE)
            else:
                result, server_info = await omni.client.get_server_info_async(src_path)
                if result != omni.client.Result.OK:
                    return False

                user_acl = omni.client.AclEntry(
                    server_info.username,
                    omni.client.AccessFlags.READ | omni.client.AccessFlags.WRITE | omni.client.AccessFlags.ADMIN
                )

                result = await omni.client.set_acls_async(src_path, [user_acl])

                return result == omni.client.Result.OK
        except Exception as e:
            carb.log_warn(f"Failed to set write permission for url {src_path}: {str(e)}.")

        return False

    @staticmethod
    async def copy(src_path: str, dest_path: str, set_target_writable_if_read_only=False, raise_error=False):
        carb.log_info(f"Copying from {src_path} to {dest_path}...")
        from .collector import CollectorException
        try:
            # OM-119250: omni.client.copy has issues to copy checkpoint.
            src_url = omni.client.break_url(src_path)
            if src_url.query and omni.client.get_branch_and_checkpoint_from_query(src_url.query):
                set_target_writable_if_read_only = False
                result, _, content = await omni.client.read_file_async(src_path)
                if result == omni.client.Result.OK:
                    content = memoryview(content).tobytes()
                    result = await omni.client.write_file_async(dest_path, _encode_content(content))
                    if result != omni.client.Result.OK:
                        carb.log_warn(f"Cannot write {dest_path}, error code: {result}.")
                else:
                    carb.log_warn(f"Cannot read {src_path}, error code: {result}.")
            else:
                result = await omni.client.copy_async(src_path, dest_path, omni.client.CopyBehavior.OVERWRITE)

            if result != omni.client.Result.OK:
                # OMPE-36842: Make error of access denied or path not found more clear to user.
                if result == omni.client.Result.ERROR_ACCESS_DENIED and raise_error:
                    raise CollectorException(f"Access denied: {dest_path}.")
                carb.log_warn(f"Cannot copy from {src_path} to {dest_path}, error code: {result}.")
                return False

            if set_target_writable_if_read_only:
                await OmniClientWrapper.set_write_permission(dest_path)

            return True
        except CollectorException as e:
            if raise_error:
                raise e
            else:
                carb.log_warn(f"Cannot copy {src_path} to {dest_path}: {str(e)}.")
        except Exception as e:
            carb.log_warn(f"Cannot copy {src_path} to {dest_path}: {str(e)}.")

        return False

    @staticmethod
    async def read(src_path: str):
        carb.log_info(f"Reading {src_path}...")
        try:
            result, version, content = await omni.client.read_file_async(src_path)
            if result == omni.client.Result.OK:
                return memoryview(content).tobytes()
            else:
                carb.log_warn(f"Cannot read {src_path}, error code: {result}.")
        except Exception as e:
            carb.log_warn(f"Cannot read {src_path}: {str(e)}.")
        finally:
            carb.log_info(f"Reading {src_path} done.")

        return None

    @staticmethod
    async def create_folder(path):
        carb.log_info(f"Creating dir {path}...")
        result = await omni.client.create_folder_async(path)
        return result == omni.client.Result.OK
