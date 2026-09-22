// Copyright (c) 2019-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/Defines.h>
#include <carb/extras/Unicode.h>

#include <string>
#include <utility>
#include <vector>

#if CARB_PLATFORM_WINDOWS
#    ifndef NOMINMAX
#        define NOMINMAX
#    endif
#    include <ShObjIdl_core.h>
#endif

#ifdef _MSC_VER
#    pragma warning(disable : 4996)
#endif


namespace omni
{
namespace kit
{
namespace ui
{
/**
 * Defines an NativeFileDialog class that handles file/folder selection using OS specific implementation.
 */
class NativeFileDialog
{
public:
    enum class Mode
    {
        eOpen, ///! OpenFileDialog.
        eSave, ///! SaveFileDialog.
    };

    enum class Type
    {
        eFile, ///! Select file.
        eDirectory, ///! Select directory.
    };

    /**
     * Constructor.
     *
     * @param mode Open or Save dialog.
     * @param type Choose File or Directory.
     * @param title Title text.
     * @param multiSelction If supporting selecting more than one file/directory.
     */
    NativeFileDialog(Mode mode, Type type, const std::string& title, bool multiSelection);

    /**
     * Add file type filter.
     *
     * @param name Name of the file type.
     * @param spec Specification of the file type.
     */
    void addFilter(const std::string& name, const std::string& spec);

    /**
     * Shows the open file dialog.
     */
    bool show();

    /**
     * Gets the selected path(s).
     *
     * @param urls The vector to write selected path(s) to.
     * @return True if the result is valid.
     */
    bool getFileUrls(std::vector<std::string>& urls) const;

private:
    struct FileTypeFilter
    {
        std::string name;
        std::string spec;
    };

    Mode m_mode;
    Type m_type;
    std::string m_title;
    std::vector<FileTypeFilter> m_filters;
    std::vector<std::string> m_fileUrls;
    bool m_multiSel;
};


inline NativeFileDialog::NativeFileDialog(Mode mode, Type type, const std::string& title, bool multiSelection)
    : m_mode(mode), m_type(type), m_title(title), m_multiSel(multiSelection)
{
}

inline void NativeFileDialog::addFilter(const std::string& name, const std::string& spec)
{
    m_filters.emplace_back(FileTypeFilter{ name, spec });
}

inline bool NativeFileDialog::show()
{
    bool ret = false;
#if CARB_PLATFORM_WINDOWS
    auto prepareDialogCommon = [this](::IFileDialog* fileDialog, std::vector<std::wstring>& wstrs) {
        // Set filters
        std::vector<COMDLG_FILTERSPEC> rgFilterSpec;
        rgFilterSpec.reserve(m_filters.size());
        wstrs.reserve(m_filters.size() * 2);
        for (auto& filter : m_filters)
        {
            wstrs.push_back(carb::extras::convertUtf8ToWide(filter.name));
            std::wstring& nameWstr = wstrs.back();
            wstrs.push_back(carb::extras::convertUtf8ToWide(filter.spec));
            std::wstring& specWstr = wstrs.back();
            rgFilterSpec.emplace_back(COMDLG_FILTERSPEC{ nameWstr.c_str(), specWstr.c_str() });
        }
        fileDialog->SetFileTypes(static_cast<UINT>(rgFilterSpec.size()), rgFilterSpec.data());

        std::wstring title = carb::extras::convertUtf8ToWide(m_title);
        fileDialog->SetTitle(title.c_str());
    };

    switch (m_mode)
    {
    case Mode::eOpen:
    {
        IFileOpenDialog* fileDialog;
        auto hr = CoCreateInstance(CLSID_FileOpenDialog, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&fileDialog));
        if (SUCCEEDED(hr))
        {
            DWORD options;
            fileDialog->GetOptions(&options);
            if (m_multiSel)
            {
                options |= OFN_ALLOWMULTISELECT;
            }
            if (m_type == Type::eDirectory)
            {
                options |= FOS_PICKFOLDERS;
            }
            fileDialog->SetOptions(options);

            std::vector<std::wstring> wstrs; // keep a reference of the converted string around
            prepareDialogCommon(fileDialog, wstrs);

            hr = fileDialog->Show(nullptr);
            if (SUCCEEDED(hr))
            {
                IShellItemArray* pItemArray;
                hr = fileDialog->GetResults(&pItemArray);
                if (SUCCEEDED(hr))
                {
                    DWORD dwNumItems = 0;
                    pItemArray->GetCount(&dwNumItems);
                    for (DWORD i = 0; i < dwNumItems; i++)
                    {
                        IShellItem* pItem = nullptr;
                        hr = pItemArray->GetItemAt(i, &pItem);

                        if (SUCCEEDED(hr))
                        {
                            PWSTR pszFilePath;
                            hr = pItem->GetDisplayName(SIGDN_FILESYSPATH, &pszFilePath);

                            if (SUCCEEDED(hr))
                            {
                                std::string path = carb::extras::convertWideToUtf8(pszFilePath);
                                m_fileUrls.emplace_back(std::move(path));

                                CoTaskMemFree(pszFilePath);
                            }
                            pItem->Release();
                        }
                    }
                    ret = true;
                    pItemArray->Release();
                }
            }
            fileDialog->Release();
        }
        break;
    }
    case Mode::eSave:
    {
        IFileSaveDialog* fileDialog;
        auto hr = CoCreateInstance(CLSID_FileSaveDialog, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&fileDialog));
        if (SUCCEEDED(hr))
        {
            std::vector<std::wstring> wstrs; // keep a reference of the converted string around
            prepareDialogCommon(fileDialog, wstrs);
            fileDialog->SetFileName(L"Untitled");

            hr = fileDialog->Show(nullptr);
            if (SUCCEEDED(hr))
            {
                IShellItem* pItem = nullptr;
                hr = fileDialog->GetResult(&pItem);
                if (SUCCEEDED(hr))
                {
                    PWSTR pszFilePath;
                    hr = pItem->GetDisplayName(SIGDN_FILESYSPATH, &pszFilePath);

                    if (SUCCEEDED(hr))
                    {
                        std::string path = carb::extras::convertWideToUtf8(pszFilePath);
                        UINT fileTypeIndex;
                        hr = fileDialog->GetFileTypeIndex(&fileTypeIndex);
                        fileTypeIndex--; // One based index. Convert it to zero based
                        if (SUCCEEDED(hr))
                        {
                            std::string& fileType = m_filters[fileTypeIndex].spec;
                            size_t extPos = path.rfind(".stage.usd");
                            path = path.substr(0, extPos) + fileType.substr(1);
                            m_fileUrls.emplace_back(std::move(path));
                        }
                        CoTaskMemFree(pszFilePath);
                    }
                    pItem->Release();
                    ret = true;
                }
            }
            fileDialog->Release();
        }
        break;
    }
    }
#endif
    return ret;
}

inline bool NativeFileDialog::getFileUrls(std::vector<std::string>& urls) const
{
    if (m_fileUrls.size())
    {
        urls = m_fileUrls;
        return true;
    }
    return false;
}


}
}
}
