// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include "Api.h"

#include <omni/kit/IFileDialog.h>
#include <omni/ui/windowmanager/IWindowCallbackManager.h>

#include <functional>
#include <string>

namespace omni
{
namespace kit
{
namespace ui
{

/**
 * Defines an FilePicker class that handles file/folder selection.
 */
class OMNI_KIT_UI_CLASS_API FilePicker
{
public:
    using OnFileSelected = std::function<void(const char* path)>;
    using OnDialogCancelled = std::function<void()>;

    enum class Mode
    {
        eOpen, ///! OpenFileDialog.
        eSave, ///! SaveFileDialog.
    };

    enum class Type
    {
        eFile, ///! Select file.
        eDirectory, ///! Select directory.
        eAll ///! Select file or directory
    };

    enum class DataSource
    {
        eLocal, ///! Show local files only
        eOmniverse, ///! Show omniverse files only
        eAll ///! Show files form all data sources
    };

    /**
     * Constructor.
     *
     * @param mode Open or Save dialog.
     * @param type Choose File or Directory.
     * @param title Title text.
     * @param onFileSelctedFn Callback for path selection.
     * @param onDialogCancelled Callback for dialog cancel.
     * @param width Initial window width.
     * @param height Initial window height.
     * @param dataSource Data source that files come from.
     */
    OMNI_KIT_UI_API FilePicker(const std::string& title,
                               Mode mode,
                               Type type,
                               OnFileSelected onFileSelctedFn,
                               OnDialogCancelled onDialogCancelled,
                               float width,
                               float height);

    OMNI_KIT_UI_API ~FilePicker();

    /**
     * Shows the open file dialog.
     */
    OMNI_KIT_UI_API void show(DataSource dataSource = DataSource::eAll);

    OMNI_KIT_UI_API bool isVisible() const;

    OMNI_KIT_UI_API const char* getTitle() const;

    OMNI_KIT_UI_API void setTitle(const char* title);

    OMNI_KIT_UI_API Type getSelectionType() const;

    OMNI_KIT_UI_API void setSelectionType(Type type);

    OMNI_KIT_UI_API void setFileSelectedFn(const OnFileSelected& fn);

    OMNI_KIT_UI_API void setDialogCancelled(const OnDialogCancelled& fn);

    /**
     * Add file type filter.
     *
     * @param name Name of the file type.
     * @param spec Specification of the file type.
     */
    OMNI_KIT_UI_API void addFilter(const std::string& name, const std::string& spec);

    /**
     * Clear all filters.
     */
    OMNI_KIT_UI_API void clearAllFilters();

    /**
     * Sets the directory where the dialog will open
     */
    OMNI_KIT_UI_API void setCurrentDirectory(const char* dir);

    /** sets the default name to use for the filename on save dialogs.
     *
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
    OMNI_KIT_UI_API void setDefaultSaveName(const char* name);

private:
    void _draw(float dt);

    FileDialog* m_fileDialog = nullptr;
    omni::ui::windowmanager::IWindowCallbackPtr m_handle;
    OnFileSelected m_fileSelectedFn;
    OnDialogCancelled m_dialogCancelledFn;
};

}
}
}
