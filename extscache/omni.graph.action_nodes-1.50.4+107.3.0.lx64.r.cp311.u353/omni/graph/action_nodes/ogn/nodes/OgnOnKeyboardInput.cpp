// SPDX-FileCopyrightText: Copyright (c) 2021-2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: LicenseRef-NvidiaProprietary
//
// NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
// property and proprietary rights in and to this material, related
// documentation and any modifications thereto. Any use, reproduction,
// disclosure or distribution of this material and related documentation
// without an express license agreement from NVIDIA CORPORATION or
// its affiliates is strictly prohibited.

#include "ActionNodeCommon.h"

#include <carb/input/IInput.h>
#include <carb/input/InputTypes.h>
#include <omni/graph/action/IActionGraph.h>
#include <omni/kit/IAppWindow.h>

#include <OgnOnKeyboardInputDatabase.h>

using namespace carb::input;

namespace omni
{
namespace graph
{
namespace action
{

constexpr size_t s_numNames = 106;
static constexpr std::array<const char*, s_numNames> s_keyNames = { "Unknown",
                                                                    "Space",
                                                                    "Apostrophe",
                                                                    "Comma",
                                                                    "Minus",
                                                                    "Period",
                                                                    "Slash",
                                                                    "Key0",
                                                                    "Key1",
                                                                    "Key2",
                                                                    "Key3",
                                                                    "Key4",
                                                                    "Key5",
                                                                    "Key6",
                                                                    "Key7",
                                                                    "Key8",
                                                                    "Key9",
                                                                    "Semicolon",
                                                                    "Equal",
                                                                    "A",
                                                                    "B",
                                                                    "C",
                                                                    "D",
                                                                    "E",
                                                                    "F",
                                                                    "G",
                                                                    "H",
                                                                    "I",
                                                                    "J",
                                                                    "K",
                                                                    "L",
                                                                    "M",
                                                                    "N",
                                                                    "O",
                                                                    "P",
                                                                    "Q",
                                                                    "R",
                                                                    "S",
                                                                    "T",
                                                                    "U",
                                                                    "V",
                                                                    "W",
                                                                    "X",
                                                                    "Y",
                                                                    "Z",
                                                                    "LeftBracket",
                                                                    "Backslash",
                                                                    "RightBracket",
                                                                    "GraveAccent",
                                                                    "Escape",
                                                                    "Tab",
                                                                    "Enter",
                                                                    "Backspace",
                                                                    "Insert",
                                                                    "Del",
                                                                    "Right",
                                                                    "Left",
                                                                    "Down",
                                                                    "Up",
                                                                    "PageUp",
                                                                    "PageDown",
                                                                    "Home",
                                                                    "End",
                                                                    "CapsLock",
                                                                    "ScrollLock",
                                                                    "NumLock",
                                                                    "PrintScreen",
                                                                    "Pause",
                                                                    "F1",
                                                                    "F2",
                                                                    "F3",
                                                                    "F4",
                                                                    "F5",
                                                                    "F6",
                                                                    "F7",
                                                                    "F8",
                                                                    "F9",
                                                                    "F10",
                                                                    "F11",
                                                                    "F12",
                                                                    "Numpad0",
                                                                    "Numpad1",
                                                                    "Numpad2",
                                                                    "Numpad3",
                                                                    "Numpad4",
                                                                    "Numpad5",
                                                                    "Numpad6",
                                                                    "Numpad7",
                                                                    "Numpad8",
                                                                    "Numpad9",
                                                                    "NumpadDel",
                                                                    "NumpadDivide",
                                                                    "NumpadMultiply",
                                                                    "NumpadSubtract",
                                                                    "NumpadAdd",
                                                                    "NumpadEnter",
                                                                    "NumpadEqual",
                                                                    "LeftShift",
                                                                    "LeftControl",
                                                                    "LeftAlt",
                                                                    "LeftSuper",
                                                                    "RightShift",
                                                                    "RightControl",
                                                                    "RightAlt",
                                                                    "RightSuper",
                                                                    "Menu" };

static std::array<NameToken, s_numNames> s_keyTokens;
static std::array<NameToken, s_numNames> s_keyTokensLowercase;

class OgnOnKeyboardInput
{
public:
    SubscriptionId m_keyEventId; // The subscription to the global input event source (one per authoring node)
    KeyboardEvent m_keyEvent; // The last key event received
    exec::unstable::Stamp m_keySetStamp; // The stamp set by the authoring node when the even occurs

    exec::unstable::SyncStamp m_keySetSyncStamp; // The stamp used by each instance

    static bool onKeyboardEvent(const InputEvent& e, void* userData)
    {
        if (e.deviceType != DeviceType::eKeyboard)
        {
            return false;
        }
        if (e.keyboardEvent.type != KeyboardEventType::eKeyPress && e.keyboardEvent.type != KeyboardEventType::eKeyRelease)
            return false;

        NodeHandle nodeHandle = reinterpret_cast<NodeHandle>(userData);

        auto iNode = carb::getCachedInterface<omni::graph::core::INode>();
        NodeObj nodeObj = iNode->getNodeFromHandle(nodeHandle);

        // Copy the event data and request the next compute()
        auto& authoringState = OgnOnKeyboardInputDatabase::sSharedState<OgnOnKeyboardInput>(nodeObj);

        authoringState.m_keyEvent = e.keyboardEvent;
#if CARB_VERSION_ATLEAST(carb_windowing_IWindowing, 1, 5)
        carb::windowing::IWindowing* windowing = carb::getCachedInterface<carb::windowing::IWindowing>();
        if (windowing)
            authoringState.m_keyEvent.key = windowing->translateKey(authoringState.m_keyEvent.key);
#endif
        authoringState.m_keySetStamp.next();
        iNode->requestCompute(nodeObj);

        return true;
    }


    static void initialize(const GraphContextObj& context, const NodeObj& nodeObj)
    {
        // First time look up all the tokens and their lowercase equivalents
        [[maybe_unused]] static bool callOnce = ([&context] {
            size_t i = 0;
            for (const char* name : s_keyNames)
            {
                s_keyTokens[i] = context.iToken->getHandle(name);
                std::string lower(strlen(name), '\0');
                std::transform(name, name + strlen(name), lower.begin(), [](unsigned char c) {return ::tolower(c);});
                s_keyTokensLowercase[i] = context.iToken->getHandle(lower.c_str());
                ++i;
            }
        } (), true);

        omni::kit::IAppWindow* appWindow = omni::kit::getDefaultAppWindow();
        if (!appWindow)
        {
            return;
        }

        Keyboard* keyboard = appWindow->getKeyboard();
        if (!keyboard)
        {
            CARB_LOG_ERROR_ONCE("No Keyboard!");
            return;
        }

        IInput* input = carb::getCachedInterface<IInput>();
        if (!input)
        {
            CARB_LOG_ERROR_ONCE("No Input!");
            return;
        }

        auto& authoringState = OgnOnKeyboardInputDatabase::sSharedState<OgnOnKeyboardInput>(nodeObj);
        authoringState.m_keyEventId =
            input->subscribeToInputEvents((carb::input::InputDevice*)keyboard, kEventTypeAll, onKeyboardEvent,
                                          reinterpret_cast<void*>(nodeObj.nodeHandle), kSubscriptionOrderDefault);
    }

    static void release(const NodeObj& nodeObj)
    {
        auto const& authoringState = OgnOnKeyboardInputDatabase::sSharedState<OgnOnKeyboardInput>(nodeObj);
        IInput* input = carb::getCachedInterface<IInput>();
        if (!input)
            return;

        if (authoringState.m_keyEventId > 0)
            input->unsubscribeToInputEvents(authoringState.m_keyEventId);
    }

    static bool compute(OgnOnKeyboardInputDatabase& db)
    {
        if (checkNodeDisabledForOnlyPlay(db))
            return true;

        static const NameToken emptyToken = db.stringToToken("");

        auto iActionGraph = getInterface();

        auto const& authoringState = db.sharedState<OgnOnKeyboardInput>();

        auto& localState = db.perInstanceState<OgnOnKeyboardInput>();

        if (localState.m_keySetSyncStamp.makeSync(authoringState.m_keySetStamp))
        {
            const NameToken& keyIn = db.inputs.keyIn();
            auto& keyEvent = authoringState.m_keyEvent;

            size_t keyIndex = static_cast<size_t>(keyEvent.key);
            if (keyIndex >= s_keyTokens.size())
            {
                db.logError("Invalid Key %zu detected", keyIndex);
            }
            else
            {

                if (keyIn == emptyToken || keyIn == s_keyTokens[keyIndex] || keyIn == s_keyTokensLowercase[keyIndex])
                {
                    // If the keyIn is one of the modifiers, the modifier requirement is always satisfied.
                    // For example: LeftShift. We still want to fire pressed execution when LeftShift is pressed
                    // although there is no modifier requirement And for case Shift-LeftShift, by pressing LeftShift,
                    // the modifier requirement has been satisfied naturally
                    bool shiftSatisfied =
                        (keyEvent.key == KeyboardInput::eLeftShift || keyEvent.key == KeyboardInput::eRightShift) ?
                            true :
                            db.inputs.shiftIn() ==
                                static_cast<const bool>(keyEvent.modifiers & kKeyboardModifierFlagShift);
                    bool ctrlSatisfied =
                        (keyEvent.key == KeyboardInput::eLeftControl || keyEvent.key == KeyboardInput::eRightControl) ?
                            true :
                            db.inputs.ctrlIn() ==
                                static_cast<const bool>(keyEvent.modifiers & kKeyboardModifierFlagControl);
                    bool altSatisfied =
                        (keyEvent.key == KeyboardInput::eLeftAlt || keyEvent.key == KeyboardInput::eRightAlt) ?
                            true :
                            db.inputs.altIn() == static_cast<const bool>(keyEvent.modifiers & kKeyboardModifierFlagAlt);
                    bool keyModifierConditionSatisfied = shiftSatisfied && ctrlSatisfied && altSatisfied;
                    // Pressed case: all special keys pressed with keyIn last pressed
                    if (keyEvent.type == KeyboardEventType::eKeyPress && keyModifierConditionSatisfied)
                    {
                        iActionGraph->setExecutionEnabled(outputs::pressed.token(), db.getInstanceIndex());
                        db.outputs.isPressed() = true;
                    }
                    // Release case 1: release keyIn while all other required special keys held
                    else if (keyEvent.type == KeyboardEventType::eKeyRelease && keyModifierConditionSatisfied &&
                             db.outputs.isPressed())
                    {
                        iActionGraph->setExecutionEnabled(outputs::released.token(), db.getInstanceIndex());
                        db.outputs.isPressed() = false;
                    }

                    db.outputs.keyOut() = keyIn;
                }
                // Release case 2: release any one of required special keys while keyIn and other special keys held and
                // the press key requirements have been met Check isPressed to make sure we only fire released event
                // once for each pressed event
                else if (keyEvent.type == KeyboardEventType::eKeyRelease && db.outputs.isPressed())
                {
                    if ((db.inputs.ctrlIn() && (keyEvent.key == KeyboardInput::eLeftControl || // check if ctrl required
                                                                                               // and ctrl released
                                                keyEvent.key == KeyboardInput::eRightControl)) ||
                        (db.inputs.shiftIn() && (keyEvent.key == KeyboardInput::eLeftShift || // check if shift required
                                                                                              // and shift released
                                                 keyEvent.key == KeyboardInput::eRightShift)) ||
                        (db.inputs.altIn() && (keyEvent.key == KeyboardInput::eLeftAlt || // check if alt required and
                                                                                          // alt released
                                               keyEvent.key == KeyboardInput::eRightAlt)))
                    {
                        iActionGraph->setExecutionEnabled(outputs::released.token(), db.getInstanceIndex());
                        db.outputs.isPressed() = false;
                    }
                }
            }
        }
        return true;
    }

    // ----------------------------------------------------------------------------

    static bool updateNodeVersion(const GraphContextObj& context, const NodeObj& nodeObj, int oldVersion, int newVersion)
    {
        if (oldVersion < newVersion)
        {
            INode const* iNode = nodeObj.iNode;
            if (oldVersion < 2)
            {
                // We added allowedTokens to keyIn, so uppercase the given string so that it matches
                // the upper case allowedToken list
                auto attrObj = iNode->getAttribute(nodeObj, "inputs:keyIn");
                auto attrDataHandle = attrObj.iAttribute->getAttributeDataHandle(attrObj, kAccordingToContextIndex);
                RawPtr dataPtr{ nullptr };
                size_t dataSize{ 0 };
                context.iAttributeData->getDataReferenceW(attrDataHandle, context, dataPtr, dataSize);
                if (dataPtr)
                {
                    NameToken* tokenData = (NameToken*)dataPtr;
                    NameToken oldKeyIn = *tokenData;
                    char const* oldKeyStr = context.iToken->getText(oldKeyIn);
                    std::string newKeyStr = oldKeyStr;
                    if (newKeyStr.size() >= 1)
                    {
                        if (std::find(begin(s_keyNames), end(s_keyNames), oldKeyStr) == end(s_keyNames))
                        {
                            newKeyStr[0] = ::toupper(oldKeyStr[0]);
                            if (std::find(begin(s_keyNames), end(s_keyNames), newKeyStr) != end(s_keyNames))
                            {
                                CARB_LOG_INFO("Updating %s.inputs:keyIn from \"%s\" to \"%s\" to match allowedTokens",
                                              iNode->getPrimPath(nodeObj), oldKeyStr, newKeyStr.data());

                                NameToken const newKeyIn = context.iToken->getHandle(newKeyStr.data());
                                *tokenData = newKeyIn;
                            }
                            // If we didn't find the upper-cased key we can't do much more. We will rely on runtime
                            // errors to inform the user.
                        }
                    }
                }
            }

            if (oldVersion < 3)
            {
                // We added inputs:onlyPlayback default true - to maintain previous behavior we should set this to false
                const bool val{ false };
                nodeObj.iNode->createAttribute(nodeObj, "inputs:onlyPlayback", Type(BaseDataType::eBool), &val, nullptr,
                                               kAttributePortType_Input, kExtendedAttributeType_Regular, nullptr);
            }
        }
        return true;
    }
};

REGISTER_OGN_NODE()

} // namespace action
} // namespace graph
} // namespace omni
