// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "KitTypes.h"

#include <carb/Interface.h>

namespace omni
{
namespace kit
{

struct FileDialog;
typedef void (*OnFileDialogFileSelected)(const char* realpath, void* userData);
typedef void (*OnFileDialogCancelled)(void* userData);

enum class FileDialogOpenMode
{
    eOpen,
    eSave
};

enum class FileDialogSelectType
{
    eFile,
    eDirectory,
    eAll
};

enum class FileDialogDataSource
{
    eLocal, ///! Show local files only
    eOmniverse, ///! Show omniverse files only
    eAll ///! Show files form all data sources
};

/**
 * Defines an interface for the editor stage update API part.
 */
struct IFileDialog
{
    CARB_PLUGIN_INTERFACE("omni::kit::IFileDialog", 0, 6);

    /**
     * Create file dialog that uses for file/folder picker
     * @param title Window title.
     * @param mode Create dialog for save or open.
     * @param type Create dialog to select file or folder.
     * @param onFileSelectedFn Callback for file selection.
     * @param onDialogCancelled Callback for dialog cancel.
     * @param width Initial window width.
     * @param height Initial window height.
     * @return FileDialog instance
     */
    FileDialog*(CARB_ABI* createFileDialog)(const char* title,
                                            FileDialogOpenMode mode,
                                            FileDialogSelectType type,
                                            OnFileDialogFileSelected onFileSelectedFn,
                                            void* selectedFnUserData,
                                            OnFileDialogCancelled onDialogCancelled,
                                            void* cancelFnUserData,
                                            float width,
                                            float height);

    /**
     * Destroy file dialog
     * @param dialog FileDialog instance
     */
    void(CARB_ABI* destroyFileDialog)(FileDialog* dialog);

    /**
     * Sets file selection callback.
     * @param dialog FileDialog instance.
     * @param onFileSelctedFn Callback if file is selected.
     */
    void(CARB_ABI* setFileSelectedFnForFileDialog)(FileDialog* dialog,
                                                   OnFileDialogFileSelected onFileSelctedFn,
                                                   void* userData);

    /**
     * Sets file dialog cancelled callback.
     * @param dialog FileDialog instance.
     * @param onDialogCancelled Callback ifdialog is cancelled.
     */
    void(CARB_ABI* setCancelFnForFileDialog)(FileDialog* dialog, OnFileDialogCancelled onDialogCancelled, void* userData);

    /**
     * Adds filter to file dialog to filter file type
     * @param dialog FileDialog instance
     */
    void(CARB_ABI* addFilterToFileDialog)(FileDialog* dialog, const char* name, const char* spec);

    /**
     * Clear all filters of file dialog
     * @param dialog FileDialog instance
     */
    void(CARB_ABI* clearAllFiltersOfFileDialog)(FileDialog* dialog);

    /**
     * Show file dialog
     */
    void(CARB_ABI* showFileDialog)(FileDialog* dialog, FileDialogDataSource dataSource);

    /**
     * Draw file dialog
     */
    void(CARB_ABI* drawFileDialog)(FileDialog* dialog, float elapsedTime);

    /**
     * If file dialog is opened or not
     */
    bool(CARB_ABI* isFileDialogOpened)(FileDialog* dialog);

    /**
     * Gets title of file dialog
     */
    const char*(CARB_ABI* getTitleOfFileDialog)(FileDialog* dialog);

    /**
     * Sets title for file dialog
     */
    void(CARB_ABI* setTitleForFileDialog)(FileDialog* dialog, const char* title);

    /**
     * Gets selection type for file dialog
     */
    FileDialogSelectType(CARB_ABI* getSelectionType)(FileDialog* dialog);

    /**
     * Sets selection type for file dialog
     */
    void(CARB_ABI* setSelectionType)(FileDialog* dialog, FileDialogSelectType type);

    /**
     * Sets the directory where the dialog will open
     */
    void(CARB_ABI* setCurrentDirectory)(FileDialog* dialog, const char* dir);

    /** sets the default name to use for the filename on save dialogs.
     *
     *  @param[in] dialog   the file picker dialog to set the default save name for.  This
     *                      may not be nullptr.
     *  @param[in] name     the default filename to use for this dialog.  This may be nullptr
     *                      or an empty string to use the USD stage's default prim name.  In
     *                      this case, if the prim name cannot be retrieved, "Untitled" will
     *                      be used instead.  If a non-empty string is given here, this will
     *                      always be used as the initial suggested filename.
     *  @returns no return value.
     *
     *  @remarks This sets the default filename to be used when saving a file.  This name will
     *           be ignored if the dialog is not in @ref FileDialogOpenMode::eSave mode.  The
     *           given name will still be stored regardless.  This default filename may omit
     *           the file extension to take the extension from the current filter.  If an
     *           extension is explicitly given here, no extension will be appended regardless
     *           of the current filter.
     */
    void(CARB_ABI* setDefaultSaveName)(FileDialog* dialog, const char* name);
};

}
}
