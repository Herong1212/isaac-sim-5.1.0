// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <omni/kit/IApp.h>

#include <sstream>

namespace omni
{
namespace kit
{
/**
 * Defines a helper class to build and run python command from C++.
 * This class serves as a temporary solution before we can move editor completely into Python.
 * Do not rely on it.
 */
class PythonInterOpHelper
{
public:
    static void executeCommand(const char* command)
    {
        carb::getCachedInterface<omni::kit::IApp>()->getPythonScripting()->executeString(command);
    }

    static inline const char* pyBool(const bool value)
    {
        return (value ? "True" : "False");
    }

    template <typename T>
    static inline std::ostream& addArgument(std::ostream& strm, const T& value)
    {
        strm << value;
        return strm;
    }

    static inline std::ostream& addArgument(std::ostream& strm, const bool value)
    {
        strm << pyBool(value);
        return strm;
    }

    template <typename T> static inline std::ostream&
    addNamedArgument(std::ostream& strm, const char* name, const T& value)
    {
        strm << name << " = ";
        return addArgument(strm, value);
    }

#if defined(PXR_USD_USD_TIME_CODE_H)

    static inline std::ostream& addArgument(std::ostream& strm, const pxr::UsdTimeCode& value)
    {
        strm << "Usd.TimeCode";
        if (value == pxr::UsdTimeCode::Default())
            strm << ".Default()";
        else
            strm << '(' << value.GetValue() << ')';
        return strm;
    }

    template <typename T>
    static inline std::ostream& addArrayArgument(std::ostream& strm, const char* pyType, const T* values, size_t N)
    {
        static_assert(std::is_same<double, T>::value || std::is_same<float, T>::value || std::is_same<int, T>::value, "Unsupported array type");
        constexpr char typeMode = std::is_same<double, T>::value ? 'd' : (std::is_same<float, T>::value ? 'f' : 'i');
        strm << pyType << typeMode << "(";
        for (unsigned i = 0; i < (N-1); ++i)
        {
            strm << values[i] << ", ";
        }
        strm << values[N - 1] << ')';
        return strm;
    }

    static inline std::ostream& addArgument(std::ostream& strm, const pxr::GfVec3i& value)
    {
        return addArrayArgument(strm , "Gf.Vec3", value.data(), 3);
    }

    static inline std::ostream& addArgument(std::ostream& strm, const pxr::GfVec3f& value)
    {
        return addArrayArgument(strm, "Gf.Vec3", value.data(), 3);
    }

    static inline std::ostream& addArgument(std::ostream& strm, const pxr::GfVec3d& value)
    {
        return addArrayArgument(strm, "Gf.Vec3", value.data(), 3);
    }

    static inline std::ostream& addArgument(std::ostream& strm, const pxr::GfMatrix4d& value)
    {
        return addArrayArgument(strm, "Gf.Matrix4", value.data(), 16);
    }

    static void runTransformPrimCommand(const std::string& path,
                                        const pxr::GfMatrix4d& o,
                                        const pxr::GfMatrix4d& n,
                                        pxr::UsdTimeCode time_code = pxr::UsdTimeCode::Default(),
                                        bool had_transform_at_key = false)
    {
        // Inject python command for undo/redo
        std::ostringstream command;
        command <<
            "import omni.kit.commands\n"
            "from pxr import Gf, Usd\n"
            "omni.kit.commands.execute('TransformPrimCommand', path='" << path << "', ";
        addNamedArgument(command, "old_transform_matrix", o) << ", ";
        addNamedArgument(command, "new_transform_matrix", n) << ", ";
        addNamedArgument(command, "time_code", time_code) << ", ";
        addNamedArgument(command, "had_transform_at_key", had_transform_at_key) << ")\n";

        executeCommand(command.str().c_str());
    }

    static void runTransformPrimSRTCommand(const std::string& path,
                                           const pxr::GfVec3d o_t,
                                           const pxr::GfVec3d o_re,
                                           const pxr::GfVec3i o_ro,
                                           const pxr::GfVec3d o_s,
                                           const pxr::GfVec3d n_t,
                                           const pxr::GfVec3d n_re,
                                           const pxr::GfVec3i n_ro,
                                           const pxr::GfVec3d n_s,
                                           pxr::UsdTimeCode time_code = pxr::UsdTimeCode::Default(),
                                           bool had_transform_at_key = false)
    {
        // Inject python command for undo/redo
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                   "from pxr import Gf, Usd\n"
                   "omni.kit.commands.execute('TransformPrimSRTCommand', path='" << path << "', ";

        addNamedArgument(command, "old_translation", o_t) << ", ";
        addNamedArgument(command, "old_rotation_euler", o_re) << ", ";
        addNamedArgument(command, "old_rotation_order", o_ro) << ", ";
        addNamedArgument(command, "old_scale", o_s) << ", ";

        addNamedArgument(command, "new_translation", n_t) << ", ";
        addNamedArgument(command, "new_rotation_euler", n_re) << ", ";
        addNamedArgument(command, "new_rotation_order", n_ro) << ", ";
        addNamedArgument(command, "new_scale", n_s) << ", ";

        addNamedArgument(command, "time_code", time_code) << ", ";
        addNamedArgument(command, "had_transform_at_key", had_transform_at_key) << ")\n";

        executeCommand(command.str().c_str());
    }

    struct TransformPrimsEntry
    {
        std::string path;
        pxr::GfMatrix4d newTransform;
        pxr::GfMatrix4d oldTransform;
        bool hadTransformAtTime;
    };
    static void runTransformPrimsCommand(const std::vector<TransformPrimsEntry>& primsToTransform,
                                         pxr::UsdTimeCode time_code)
    {
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                   "from pxr import Gf, Usd\n"
                   "omni.kit.commands.execute('TransformPrimsCommand', prims_to_transform=[\n";

        char separator = ' ';
        for (auto& entry : primsToTransform)
        {
            command << separator << "('" << entry.path << "', ";
            addArgument(command, entry.newTransform) << ", ";
            addArgument(command, entry.oldTransform) << ", ";
            addArgument(command, time_code) << ", ";
            addArgument(command, entry.hadTransformAtTime) << ")\n";
            separator = ',';
        }

        command << "])\n";

        executeCommand(command.str().c_str());
    }

    struct TransformPrimsSRTEntry
    {
        std::string path;
        pxr::GfVec3d newTranslation;
        pxr::GfVec3d newRotationEuler;
        pxr::GfVec3i newRotationOrder;
        pxr::GfVec3d newScale;
        pxr::GfVec3d oldTranslation;
        pxr::GfVec3d oldRotationEuler;
        pxr::GfVec3i oldRotationOrder;
        pxr::GfVec3d oldScale;
        bool hadTransformAtTime;
    };
    static void runTransformPrimsSRTCommand(const std::vector<TransformPrimsSRTEntry>& primsToTransform,
                                            pxr::UsdTimeCode time_code)
    {
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                   "from pxr import Gf, Usd\n"
                   "omni.kit.commands.execute('TransformPrimsSRTCommand', prims_to_transform=[\n";

        char separator = ' ';
        for (auto& entry : primsToTransform)
        {
            command << separator << "('" << entry.path << "', ";
            addArgument(command, entry.newTranslation) << ", ";
            addArgument(command, entry.newRotationEuler) << ", ";
            addArgument(command, entry.newRotationOrder) << ", ";
            addArgument(command, entry.newScale) << ", ";

            addArgument(command, entry.oldTranslation) << ", ";
            addArgument(command, entry.oldRotationEuler) << ", ";
            addArgument(command, entry.oldRotationOrder) << ", ";
            addArgument(command, entry.oldScale) << ", ";

            addArgument(command, time_code) << ", ";
            addArgument(command, entry.hadTransformAtTime) << ")\n";
            separator = ',';
        }

        command << "])\n";

        executeCommand(command.str().c_str());
    }

    template <typename StrT>
    static std::string serializePrimPaths(StrT* paths, size_t count)
    {
        std::ostringstream out;
        for (size_t i = 0; i < count; i++)
        {
            out << "'" << paths[i] << "'";
            if (i != count - 1)
            {
                out << ",";
            }
        }
        return out.str();
    }

    static void runSetSelectedPrimsCommand(const std::string& oldPaths, const std::string& newPaths, bool expandInStage)
    {
        // Inject python command for undo/redo
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                   "omni.kit.commands.execute('SelectPrimsCommand'"
                << ", old_selected_paths=[" << oldPaths << "]"
                << ", new_selected_paths=[" << newPaths << "]"
                << ", expand_in_stage=" << pyBool(expandInStage)
                << ")\n";

        executeCommand(command.str().c_str());
    }

    static void runMovePrimCommand(const std::string& pathFrom, const std::string& pathTo, bool keepWorldTransfrom)
    {
        // Inject python command for undo/redo
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                   "omni.kit.commands.execute('MovePrimCommand', path_from='"
                << pathFrom << "', path_to='" << pathTo << "', keep_world_transform=" << pyBool(keepWorldTransfrom)
                << ")\n";

        executeCommand(command.str().c_str());
    }

    static void runMovePrimsCommand(const std::vector<std::pair<pxr::SdfPath, pxr::SdfPath>>& pathsToMove,
                                    bool keepWorldTransfrom)
    {
        // Inject python command for undo/redo
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                   "omni.kit.commands.execute('MovePrimsCommand', paths_to_move={";

        for (auto& entry : pathsToMove)
        {
            command << "'" << entry.first << "' : '" << entry.second << "',";
        }
        command.seekp(-1, std::ios_base::end);
        command << "}, keep_world_transform=" << pyBool(keepWorldTransfrom) << ")\n";

        executeCommand(command.str().c_str());
    }

    static void runCopyPrimCommand(const char* srcPath, const char* tarPath, bool dupLayers, bool combineLayers)
    {
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                   "omni.kit.commands.execute('CopyPrimCommand', path_from='"
                << srcPath << "', path_to=" << (tarPath ? std::string("'") + tarPath + "'" : "None")
                << ", duplicate_layers=" << pyBool(dupLayers)
                << ", combine_layers=" << pyBool(combineLayers) << ")\n";

        executeCommand(command.str().c_str());
    }

    static void runOpenStageCommand(const std::string& path)
    {
        std::ostringstream command;
        command << "import omni.kit.window.file\n"
                   "omni.kit.window.file.open_stage('"
                << path << "')\n";

        executeCommand(command.str().c_str());
    }

    // Open stage as a edit layer, that it will be a sublayer of an empty stage
    // with a edit layer above this sublayer to make edits in.
    static void runOpenStageAsEditLayerCommand(const std::string& path)
    {
        std::ostringstream command;
        command << "import omni.kit.window.file\n"
                   "omni.kit.window.file.open_with_new_edit_layer('"
                << path << "')\n";

        executeCommand(command.str().c_str());
    }

    static void runCreateReferenceCommand(const std::string& url, const std::string& pathTo, bool instanceable)
    {
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                << "import omni.usd\n"
                << "omni.kit.commands.execute('CreateReferenceCommand', usd_context=omni.usd.get_context(), path_to='"
                << pathTo << "', asset_path='" << url << "',"
                << "instanceable=" << pyBool(instanceable) << ")\n";

        executeCommand(command.str().c_str());
    }

    static void runCreatePayloadCommand(const std::string& url, const std::string& pathTo, bool instanceable)
    {
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                << "import omni.usd\n"
                << "omni.kit.commands.execute('CreatePayloadCommand', usd_context=omni.usd.get_context(), path_to='"
                << pathTo << "', asset_path='" << url << "',"
                << "instanceable=" << pyBool(instanceable) << ")\n";

        executeCommand(command.str().c_str());
    }

    static void runCreateAudioPrimFromAssetPathCommand(const std::string& url, const std::string& pathTo)
    {
        std::ostringstream command;
        command
            << "import omni.kit.commands\n"
            << "import omni.usd\n"
            << "omni.kit.commands.execute('CreateAudioPrimFromAssetPathCommand', usd_context=omni.usd.get_context(), path_to='"
            << pathTo << "', asset_path='" << url << "')\n";

        executeCommand(command.str().c_str());
    }

    static void runCreatePrimCommand(const char* primPath,
                                     const char* primType,
                                     const bool selectNewPrim,
                                     const char* usdContextName = "")
    {
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                << "omni.kit.commands.execute('CreatePrimCommand', prim_path='" << primPath << "', prim_type='"
                << primType << "', select_new_prim=" << pyBool(selectNewPrim) << ", context_name='"
                << usdContextName << "' )\n";

        executeCommand(command.str().c_str());
    }

    static void runCreateMdlMaterialPrimCommand(const std::string& mdlUrl,
                                                const std::string& mtlName,
                                                const std::string& mdlPrimPath,
                                                const std::string& targetPrimPath = "$$$")
    {
        std::ostringstream command;

        // targetPrimPath "" is valid param, use "$$$" for no parameter passed
        if (targetPrimPath.compare("$$$") == 0)
        {
            command << "import omni.kit.commands\n"
                    << "omni.kit.commands.execute('CreateMdlMaterialPrimCommand', mtl_url='" << mdlUrl
                    << "', mtl_name='" << mtlName << "', mtl_path='" << mdlPrimPath << "', select_new_prim=False)\n";
        }
        else
        {
            command << "import asyncio\n"
                    << "import omni.kit.commands\n"
                    << "import omni.kit.material.library\n"
                    << "import carb\n"
                    << "async def create_material(prim_path):\n"
                    << "    def have_subids(subids):\n"
                    << "        if len(subids) > 1:\n"
                    << "            omni.kit.material.library.custom_material_dialog(mdl_path='" << mdlUrl
                    << "', bind_prim_paths=[prim_path])\n"
                    << "            return\n";

            if (targetPrimPath.empty())
            {
                command << "        omni.kit.commands.execute('CreateMdlMaterialPrimCommand', mtl_url='" << mdlUrl
                        << "', mtl_name='" << mtlName << "', mtl_path='" << mdlPrimPath << "', select_new_prim=True)\n";
                command << "    await omni.kit.material.library.get_subidentifier_from_mdl('" << mdlUrl
                        << "', on_complete_fn=have_subids)\n";
                command << "asyncio.ensure_future(create_material(None))\n";
            }
            else
            {
                command
                    << "        with omni.kit.undo.group():\n"
                    << "             omni.kit.commands.execute('CreateMdlMaterialPrimCommand', mtl_url='" << mdlUrl
                    << "', mtl_name='" << mtlName << "', mtl_path='" << mdlPrimPath << "', select_new_prim=False)\n"
                    << "             omni.kit.commands.execute('BindMaterialCommand', prim_path = prim_path, material_path = '"
                    << mdlPrimPath << "', strength = None )\n";

                command << "    await omni.kit.material.library.get_subidentifier_from_mdl('" << mdlUrl
                        << "', on_complete_fn=have_subids)\n";
                command << "omni.kit.material.library.multi_descendents_dialog(prim_paths=['" << targetPrimPath
                        << "'], on_click_fn=lambda p: asyncio.ensure_future(create_material(prim_path=p)))\n";
            }
        }
        executeCommand(command.str().c_str());
    }

    static void beginUndoGroup()
    {
        static constexpr char kCmd[] =
            "import omni.kit.undo\n"
            "omni.kit.undo.begin_group()";

        executeCommand(kCmd);
    }

    static void endUndoGroup()
    {
        static constexpr char kCmd[] =
            "import omni.kit.undo\n"
            "omni.kit.undo.end_group()";

        executeCommand(kCmd);
    }

    static void popLastUndoGroup()
    {
        static constexpr char kCmd[] =
            "import omni.kit.undo\n"
            "keep_going = True\n"
            "undo_stack = omni.kit.undo.get_undo_stack()\n"
            "while keep_going:\n"
            "    entry = undo_stack.pop()\n"
            "    if entry.level == 0:\n"
            "        keep_going = False\n";

        executeCommand(kCmd);
    }

    static void createBuiltinCamera(const char* path, bool ortho, const char* usdContextName = "")
    {
        beginUndoGroup();

        runCreatePrimCommand(path, "Camera", false, usdContextName);

        std::ostringstream command;
        command << "from pxr import Usd, UsdGeom, Gf, Kind\n"
                   "import omni.usd\n"
                   "import omni.kit.commands\n"
                   "stage = omni.usd.get_context('" << usdContextName << "').get_stage()\n"
                   "camera = UsdGeom.Camera.Get(stage, '" << path << "')\n"
                   "camera.CreateClippingRangeAttr(Gf.Vec2f(" << (ortho ? "2e4" : "1.0") << ", 1e7))\n"
                   "Usd.ModelAPI(camera).SetKind(Kind.Tokens.component)\n"
                   "camera.GetPrim().SetMetadata('no_delete', True)\n";

        command << "import carb\n"
                << "cam_settings = carb.settings.get_settings().get_settings_dictionary('/persistent/app/primCreation/typedDefaults/"
                    << (ortho ? "orthoCamera" : "camera") << "')\n"
                << "if cam_settings:\n"
                << "  for name, value in cam_settings.get_dict().items():\n"
                // Catch failures and issue an error, but continue on
                << "    try:\n"
                << "      attr = camera.GetPrim().GetAttribute(name)\n"
                << "      if attr:\n"
                << "        attr.Set(value)\n"
                << "    except Exception:\n"
                << "      import traceback\n"
                << "      carb.log_error(traceback.format_exc())\n";

        executeCommand(command.str().c_str());

        endUndoGroup();
    }

    static void runFramePrimsCommand(const std::string& camera, const PXR_NS::SdfPathVector& paths, double aspectRatio, const pxr::UsdTimeCode& timeCode, const std::string& usdContext)
    {
        std::ostringstream command;
        command << "import omni.kit.commands\n"
            << "omni.kit.commands.execute('FramePrimsCommand'"
            << ", prim_to_move='" << camera << "'"
            << ", aspect_ratio=" << (std::isfinite(aspectRatio) ? aspectRatio : 1.0)
            << ", usd_context_name='" << usdContext << "'"
            << ", time_code=";
        addArgument(command, timeCode);
        if (!paths.empty())
        {
            auto pathItr = paths.begin();
            command << ", prims_to_frame = [ '" << *pathItr << "'";
            ++pathItr;
            for (auto pathEnd = paths.end(); pathItr != pathEnd; ++pathItr)
            {
                command << ", '" << *pathItr << "'";
            }
            command << "]";
        }
        command << ")\n";

        executeCommand(command.str().c_str());
    }

    static void runDuplicateFromActiveViewportCameraCommand(const char* viewportName)
    {
        std::ostringstream command;
        command << "import omni.kit.commands\n"
                   "omni.kit.commands.execute('DuplicateFromActiveViewportCameraCommand', viewport_name='"
                << viewportName << "')\n";

        executeCommand(command.str().c_str());
    }

    // Post notification utility from python
    static void postNotification(const std::string& message, bool hide_after_timeout = true, bool info = true)
    {
        std::ostringstream command;
        command << "try:\n"
            << "    import omni.kit.notification_manager as nm\n"
            << "    nm.post_notification(\"" << message << "\", hide_after_timeout=" << pyBool(hide_after_timeout);
        if (!info)
        {
            command << ", status=nm.NotificationStatus.WARNING";
        }
        command << ")\n"
            << "except Exception:\n"
            << "    pass\n";

        executeCommand(command.str().c_str());
    }
#endif // PXR_USD_USD_TIME_CODE_H
};
}
}
