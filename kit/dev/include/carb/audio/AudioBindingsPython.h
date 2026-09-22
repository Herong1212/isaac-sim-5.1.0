// Copyright (c) 2020-2024, NVIDIA CORPORATION. All rights reserved.
//
// NVIDIA CORPORATION and its licensors retain all intellectual property
// and proprietary rights in and to this software, related documentation
// and any modifications thereto. Any use, reproduction, disclosure or
// distribution of this software and related documentation without an express
// license agreement from NVIDIA CORPORATION is strictly prohibited.
//
#pragma once

#include <carb/BindingsPythonUtils.h>

#include "IAudioPlayback.h"
#include "IAudioData.h"
#include "IAudioUtils.h"
#include "AudioUtils.h"

namespace carb
{
namespace audio
{

// ********************************** Custom exception objects ************************************
/** Custom exception types used here.  These are all registered as translatable exceptions
 *  on the Python side through pybind11.
 *  @{
 */

#define CARBLOCAL_DEFINE_EXCEPTION(type, base)                                                                         \
    class type : public base                                                                                           \
    {                                                                                                                  \
    public:                                                                                                            \
        explicit type(const std::string& msg) : base(msg)                                                              \
        {                                                                                                              \
        }                                                                                                              \
        explicit type(const char* msg) : base(msg)                                                                     \
        {                                                                                                              \
        }                                                                                                              \
        virtual ~type()                                                                                                \
        {                                                                                                              \
        }                                                                                                              \
    }

CARBLOCAL_DEFINE_EXCEPTION(SoundDataError, std::runtime_error);
CARBLOCAL_DEFINE_EXCEPTION(NotAvailable, std::runtime_error);
CARBLOCAL_DEFINE_EXCEPTION(DecoderError, std::runtime_error);
CARBLOCAL_DEFINE_EXCEPTION(EncoderError, std::runtime_error);
CARBLOCAL_DEFINE_EXCEPTION(ReadOnly, std::runtime_error);
CARBLOCAL_DEFINE_EXCEPTION(ContextError, std::runtime_error);

#undef CARBLOCAL_DEFINE_EXCEPTION
/** @} */


// ********************************** Object wrapper classes **************************************
/** Local replacement/alias struct for `carb::Float2`.  The Python bindings choke on parsing the
 *  `carb::Float2` name when generating the docs for a function binding that it in a list
 *  parameter (ie: `std::vector` on the C++ side or `List` parameter on the Python side).
 *  This results in a "failed to parse arglist" error in Sphinx since the extracted argument
 *  list contains "List[carb::Float2]".  Sphinx then sees this as a Python slice object and
 *  fails to parse it properly.  This could also be caused by Python/Sphinx not having any
 *  knowledge of the `carb::Float2` type since it isn't also exported through bindings.
 */
class Float2Ex : public carb::Float2
{
public:
    Float2Ex(float x_, float y_)
    {
        x = x_;
        y = y_;
    }
    Float2Ex(const std::vector<float>& list)
    {
        x = list.size() > 0 ? list[0] : 0;
        y = list.size() > 1 ? list[1] : 0;
    }
};

/** A helper class to wrap the Voice* object for python.
 *  There is no way to actually create Voices from these bindings yet.
 *
 *  @note This wrapper only exposes functions to alter voice parameters at the
 *        moment. This is done because IAudioPlayback is not thread-safe yet
 *        and allowing other changes would cause thread safety issues with
 *        Omniverse Kit.
 */
class PythonVoice
{
public:
    PythonVoice(IAudioPlayback* iface, audio::Voice* voice)
    {
        m_iface = iface;
        m_voice = voice;
    }

    void stop()
    {
        m_iface->stopVoice(m_voice);
    }

    bool isPlaying()
    {
        return m_iface->isPlaying(m_voice);
    }

    bool setLoopPoint(const LoopPointDesc* desc)
    {
        return m_iface->setLoopPoint(m_voice, desc);
    }

    size_t getPlayCursor(UnitType type)
    {
        return m_iface->getPlayCursor(m_voice, type);
    }

    void setParameters(VoiceParamFlags paramsToSet, const VoiceParams* params)
    {
        m_iface->setVoiceParameters(m_voice, paramsToSet, params);
    }

    void getParameters(VoiceParamFlags paramsToGet, VoiceParams* params)
    {
        m_iface->getVoiceParameters(m_voice, paramsToGet, params);
    }

    void setPlaybackMode(PlaybackModeFlags mode)
    {
        VoiceParams params = {};
        params.playbackMode = mode;
        m_iface->setVoiceParameters(m_voice, fVoiceParamPlaybackMode, &params);
    }

    void setVolume(float volume)
    {
        VoiceParams params = {};
        params.volume = volume;
        m_iface->setVoiceParameters(m_voice, fVoiceParamVolume, &params);
    }

    void setMute(bool muted)
    {
        VoiceParams params = {};
        params.playbackMode = muted ? fPlaybackModeMuted : 0;
        m_iface->setVoiceParameters(m_voice, fVoiceParamMute, &params);
    }

    void setBalance(float pan, float fade)
    {
        VoiceParams params = {};
        params.balance.pan = pan;
        params.balance.fade = fade;
        m_iface->setVoiceParameters(m_voice, fVoiceParamBalance, &params);
    }

    void setFrequencyRatio(float ratio)
    {
        VoiceParams params = {};
        params.frequencyRatio = ratio;
        m_iface->setVoiceParameters(m_voice, fVoiceParamFrequencyRatio, &params);
    }

    void setPriority(int32_t priority)
    {
        VoiceParams params = {};
        params.priority = priority;
        m_iface->setVoiceParameters(m_voice, fVoiceParamPriority, &params);
    }

    void setSpatialMixLevel(float level)
    {
        VoiceParams params = {};
        params.spatialMixLevel = level;
        m_iface->setVoiceParameters(m_voice, fVoiceParamSpatialMixLevel, &params);
    }

    void setDopplerScale(float scale)
    {
        VoiceParams params = {};
        params.dopplerScale = scale;
        m_iface->setVoiceParameters(m_voice, fVoiceParamDopplerScale, &params);
    }

    void setOcclusion(float direct, float reverb)
    {
        VoiceParams params = {};
        params.occlusion.direct = direct;
        params.occlusion.reverb = reverb;
        m_iface->setVoiceParameters(m_voice, fVoiceParamOcclusionFactor, &params);
    }

    void setMatrix(std::vector<float> matrix)
    {
        // FIXME: This should probably validate the source/destination channels.
        //        We can get the source channels by retrieving the currently playing sound,
        //        but we have no way to retrieve the context's channel count here.
        VoiceParams params = {};
        params.matrix = matrix.data();
        m_iface->setVoiceParameters(m_voice, fVoiceParamMatrix, &params);
    }

    void setPosition(Float3 position)
    {
        VoiceParams params = {};
        params.emitter.flags = fEntityFlagPosition;
        params.emitter.position = position;
        m_iface->setVoiceParameters(m_voice, fVoiceParamEmitter, &params);
    }

    void setVelocity(Float3 velocity)
    {
        VoiceParams params = {};
        params.emitter.flags = fEntityFlagVelocity;
        params.emitter.velocity = velocity;
        m_iface->setVoiceParameters(m_voice, fVoiceParamEmitter, &params);
    }

    void setRolloffCurve(RolloffType type,
                         float nearDistance,
                         float farDistance,
                         std::vector<Float2Ex>& volume,
                         std::vector<Float2Ex>& lowFrequency,
                         std::vector<Float2Ex>& lowPassDirect,
                         std::vector<Float2Ex>& lowPassReverb,
                         std::vector<Float2Ex>& reverb)
    {
        RolloffCurve volumeCurve = {};
        RolloffCurve lowFrequencyCurve = {};
        RolloffCurve lowPassDirectCurve = {};
        RolloffCurve lowPassReverbCurve = {};
        RolloffCurve reverbCurve = {};
        VoiceParams params = {};
        params.emitter.flags = fEntityFlagRolloff;
        params.emitter.rolloff.type = type;
        params.emitter.rolloff.nearDistance = nearDistance;
        params.emitter.rolloff.farDistance = farDistance;
        if (!volume.empty())
        {
            volumeCurve.points = volume.data();
            volumeCurve.pointCount = volume.size();
            params.emitter.rolloff.volume = &volumeCurve;
        }
        if (!lowFrequency.empty())
        {
            lowFrequencyCurve.points = lowFrequency.data();
            lowFrequencyCurve.pointCount = lowFrequency.size();
            params.emitter.rolloff.lowFrequency = &lowFrequencyCurve;
        }
        if (!lowPassDirect.empty())
        {
            lowPassDirectCurve.points = lowPassDirect.data();
            lowPassDirectCurve.pointCount = lowPassDirect.size();
            params.emitter.rolloff.lowPassDirect = &lowPassDirectCurve;
        }
        if (!lowPassReverb.empty())
        {
            lowPassReverbCurve.points = lowPassReverb.data();
            lowPassReverbCurve.pointCount = lowPassReverb.size();
            params.emitter.rolloff.lowPassReverb = &lowPassReverbCurve;
        }
        if (!reverb.empty())
        {
            reverbCurve.points = reverb.data();
            reverbCurve.pointCount = reverb.size();
            params.emitter.rolloff.reverb = &reverbCurve;
        }
        m_iface->setVoiceParameters(m_voice, fVoiceParamEmitter, &params);
    }

private:
    Voice* m_voice;
    IAudioPlayback* m_iface;
};

class PythonSoundData
{
public:
    PythonSoundData(IAudioData* iface, SoundData* data) noexcept
    {
        m_iface = iface;
        m_data = data;
        m_utils = carb::getFramework()->acquireInterface<IAudioUtils>();
    }

    PythonSoundData(const PythonSoundData& other)
    {
        *this = other;
    }

    ~PythonSoundData() noexcept
    {
        m_iface->release(m_data);
    }

    PythonSoundData& operator=(const PythonSoundData& other)
    {
        if (&other == this)
            return *this;

        m_iface = other.m_iface;
        m_utils = other.m_utils;
        auto data = m_iface->acquire(other.m_data);

        if (m_data != nullptr)
            m_iface->release(std::exchange(m_data, nullptr));

        m_data = data;
        return *this;
    }

    static PythonSoundData* fromRawBlob(IAudioData* iface,
                                        const void* blob,
                                        size_t samples,
                                        SampleFormat format,
                                        size_t channels,
                                        size_t frameRate,
                                        SpeakerMode channelMask)
    {
        SoundFormat fmt;
        size_t bytes = samples * sampleFormatToBitsPerSample(format) / CHAR_BIT;
        SoundData* tmp;

        generateSoundFormat(&fmt, format, channels, frameRate, channelMask);

        tmp = createSoundFromRawPcmBlob(iface, blob, bytes, bytesToFrames(bytes, &fmt), &fmt);
        if (tmp == nullptr)
            throw SoundDataError("failed to create a SoundData object");
        return new PythonSoundData(iface, tmp);
    }

    const char* getName()
    {
        return m_iface->getName(m_data);
    }

    bool isDecoded()
    {
        return (m_iface->getFlags(m_data) & fDataFlagStream) == 0;
    }

    SoundFormat getFormat()
    {
        SoundFormat fmt;
        m_iface->getFormat(m_data, CodecPart::eEncoder, &fmt);
        return fmt;
    }

    size_t getLength(UnitType units)
    {
        return m_iface->getLength(m_data, units);
    }

    void setValidLength(size_t length, UnitType units)
    {
        m_iface->setValidLength(m_data, length, units);
    }

    size_t getValidLength(UnitType units)
    {
        return m_iface->getValidLength(m_data, units);
    }

    std::vector<uint8_t> getBufferU8(size_t offset, size_t length, UnitType units)
    {
        return getBuffer<uint8_t>(offset, length, units);
    }

    std::vector<int16_t> getBufferS16(size_t offset, size_t length, UnitType units)
    {
        return getBuffer<int16_t>(offset, length, units);
    }

    std::vector<int32_t> getBufferS32(size_t offset, size_t length, UnitType units)
    {
        return getBuffer<int32_t>(offset, length, units);
    }

    std::vector<float> getBufferFloat(size_t offset, size_t length, UnitType units)
    {
        return getBuffer<float>(offset, length, units);
    }

    void writeBufferU8(const std::vector<uint8_t>& data, size_t offset, UnitType units)
    {
        return writeBuffer<uint8_t>(data, offset, units);
    }

    void writeBufferS16(const std::vector<int16_t>& data, size_t offset, UnitType units)
    {
        return writeBuffer<int16_t>(data, offset, units);
    }

    void writeBufferS32(const std::vector<int32_t>& data, size_t offset, UnitType units)
    {
        return writeBuffer<int32_t>(data, offset, units);
    }

    void writeBufferFloat(const std::vector<float>& data, size_t offset, UnitType units)
    {
        return writeBuffer<float>(data, offset, units);
    }

    size_t getMemoryUsed()
    {
        return m_iface->getMemoryUsed(m_data);
    }

    uint32_t getMaxInstances()
    {
        return m_iface->getMaxInstances(m_data);
    }

    void setMaxInstances(uint32_t limit)
    {
        m_iface->setMaxInstances(m_data, limit);
    }

    PeakVolumes getPeakLevel()
    {
        PeakVolumes vol;
        if (!m_iface->getPeakLevel(m_data, &vol))
        {
            throw NotAvailable("this sound has no peak volume information");
        }

        return vol;
    }

    std::vector<EventPoint> getEventPoints()
    {
        size_t count = m_iface->getEventPoints(m_data, nullptr, 0);
        size_t retrieved;
        std::vector<EventPoint> out;
        out.resize(count);
        retrieved = m_iface->getEventPoints(m_data, out.data(), count);
        if (retrieved < count)
        {
            CARB_LOG_ERROR("retrieved fewer event points than expected (%zu < %zu)\n", retrieved, count);
            out.resize(retrieved);
        }
        return out;
    }

    const EventPoint* getEventPointById(EventPointId id)
    {
        return wrapEventPoint(m_iface->getEventPointById(m_data, id));
    }

    const EventPoint* getEventPointByIndex(size_t index)
    {
        return wrapEventPoint(m_iface->getEventPointByIndex(m_data, index));
    }

    const EventPoint* getEventPointByPlayIndex(size_t index)
    {
        return wrapEventPoint(m_iface->getEventPointByPlayIndex(m_data, index));
    }

    size_t getEventPointMaxPlayIndex()
    {
        return m_iface->getEventPointMaxPlayIndex(m_data);
    }

    bool setEventPoints(std::vector<EventPoint> eventPoints)
    {
        // text does not work properly in bindings
        for (size_t i = 0; i < eventPoints.size(); i++)
        {
            eventPoints[i].label = nullptr;
            eventPoints[i].text = nullptr;
        }

        return m_iface->setEventPoints(m_data, eventPoints.data(), eventPoints.size());
    }

    void clearEventPoints()
    {
        m_iface->setEventPoints(m_data, kEventPointTableClear, 0);
    }

    std::pair<const char*, const char*> getMetaDataByIndex(size_t index)
    {
        const char* value;
        const char* key = m_iface->getMetaDataTagName(m_data, index, &value);
        return std::pair<const char*, const char*>(key, value);
    }

    const char* getMetaData(const char* tagName)
    {
        return m_iface->getMetaData(m_data, tagName);
    }

    bool setMetaData(const char* tagName, const char* tagValue)
    {
        return m_iface->setMetaData(m_data, tagName, tagValue);
    }

    bool saveToFile(const char* fileName, SampleFormat format = SampleFormat::eDefault, SaveFlags flags = 0)
    {
        return saveSoundToDisk(m_utils, m_data, fileName, format, flags);
    }

    SoundData* getNativeObject()
    {
        return m_data;
    }

private:
    EventPoint* wrapEventPoint(const EventPoint* point)
    {
        if (point == nullptr)
            return nullptr;

        EventPoint* out = new EventPoint;
        *out = *point;
        return out;
    }

    template <typename T>
    SampleFormat getFormatFromType()
    {
        // I'd do this with template specialization but GCC won't accept that
        // for some reason
        if (std::is_same<T, uint8_t>::value)
        {
            return SampleFormat::ePcm8;
        }
        else if (std::is_same<T, int16_t>::value)
        {
            return SampleFormat::ePcm16;
        }
        else if (std::is_same<T, int32_t>::value)
        {
            return SampleFormat::ePcm32;
        }
        else if (std::is_same<T, float>::value)
        {
            return SampleFormat::ePcmFloat;
        }
        else
        {
            return SampleFormat::eDefault;
        }
    }

    template <typename T>
    std::vector<T> getBuffer(size_t offset, size_t length, UnitType units)
    {
        size_t samples;
        size_t soundLength = getValidLength(UnitType::eFrames);
        SoundFormat fmt = getFormat();
        std::vector<T> out;

        if (units == UnitType::eBytes && offset % fmt.frameSize != 0)
        {
            throw std::invalid_argument("byte offset was not aligned correctly for the data type");
        }

        length = convertUnits(length, units, UnitType::eFrames, &fmt);
        offset = convertUnits(offset, units, UnitType::eFrames, &fmt);

        if (length == 0 || length > soundLength)
            length = soundLength;

        if (length == 0)
            return {};

        offset = CARB_MIN(soundLength - 1, offset);

        if (offset + length > soundLength)
        {
            length = soundLength - offset;
        }

        samples = length * fmt.channels;
        out.resize(samples);

        if (isDecoded())
        {
            size_t byteOffset = convertUnits(offset, UnitType::eFrames, UnitType::eBytes, &fmt);
            const void* buffer = m_iface->getReadBuffer(m_data);

            writeGenericBuffer(static_cast<const uint8_t*>(buffer) + byteOffset, out.data(), fmt.format,
                               getFormatFromType<T>(), samples);
        }
        else
        {
            size_t decoded = 0;
            CodecState* state = nullptr;
            CodecStateDesc desc = {};

            desc.part = CodecPart::eDecoder;
            desc.decode.flags =
                fDecodeStateFlagCoarseSeek | fDecodeStateFlagSkipMetaData | fDecodeStateFlagSkipEventPoints;
            desc.decode.soundData = m_data;
            desc.decode.outputFormat = getFormatFromType<T>();
            desc.decode.readCallbackContext = nullptr;
            desc.decode.ext = nullptr;

            state = m_iface->createCodecState(&desc);
            if (state == nullptr)
            {
                m_iface->destroyCodecState(state);
                throw DecoderError("failed to initialize the decoder");
            }

            if (offset != 0 && !m_iface->setCodecPosition(state, offset, UnitType::eFrames))
            {
                m_iface->destroyCodecState(state);
                throw DecoderError("failed to seek into the sound");
            }

            if (m_iface->decodeData(state, out.data(), length, &decoded) == nullptr)
            {
                m_iface->destroyCodecState(state);
                throw DecoderError("failed to decode the sound");
            }

            if (decoded < length)
            {
                CARB_LOG_ERROR("decoded fewer frames that expected (%zu < %zu)\n", decoded, length);
                out.resize(decoded * fmt.channels);
            }

            m_iface->destroyCodecState(state);
        }

        return out;
    }

    template <typename T>
    void writeBuffer(const std::vector<T>& data, size_t offset, UnitType units)
    {
        SoundFormat fmt = getFormat();
        void* buffer = m_iface->getBuffer(m_data);
        size_t length = data.size();
        size_t maxLength = getLength(UnitType::eBytes);

        if (!isDecoded())
        {
            throw ReadOnly("this SoundData object is read-only");
        }

        if (units == UnitType::eBytes && offset % fmt.frameSize != 0)
        {
            throw std::invalid_argument("byte offset was not aligned correctly for the data type");
        }

        offset = convertUnits(offset, units, UnitType::eBytes, &fmt);
        if (offset + length > maxLength)
        {
            length = maxLength - offset;
        }

        writeGenericBuffer(
            data.data(), static_cast<uint8_t*>(buffer) + offset, getFormatFromType<T>(), fmt.format, length);
    }

    void writeGenericBuffer(const void* in, void* out, SampleFormat inFmt, SampleFormat outFmt, size_t samples)
    {
        if (inFmt != outFmt)
        {
            TranscodeDesc desc = {};
            desc.inFormat = inFmt;
            desc.outFormat = outFmt;
            desc.inBuffer = in;
            desc.outBuffer = out;
            desc.samples = samples;
            if (!m_utils->transcodePcm(&desc))
                throw EncoderError("PCM transcoding failed unexpectedly");
        }
        else
        {
            memcpy(out, in, samples * sampleFormatToBitsPerSample(inFmt) / CHAR_BIT);
        }
    }

    IAudioData* m_iface;
    IAudioUtils* m_utils;
    SoundData* m_data;
};

/** A helper class to wrap the Context* object for python.
 *  There is no way to actually create or destroy the Context* object in these
 *  bindings yet.
 *
 *  @note This wrapper only exposes functions to alter Context parameters at the
 *        moment. This is done because IAudioPlayback is not thread-safe yet
 *        and allowing other changes would cause thread safety issues with
 *        Omniverse Kit.
 */
class PythonContext
{
public:
    CARB_PREVENT_COPY(PythonContext);

    PythonContext(IAudioPlayback* iface, Context* context) : m_context(context), m_iface(iface)
    {
    }

    PythonContext(PythonContext&& other)
    {
        *this = std::move(other);
    }

    ~PythonContext()
    {
        m_iface->destroyContext(m_context);
        m_context = nullptr;
    }

    PythonContext& operator=(PythonContext&& other)
    {
        if (&other == this)
            return *this;

        m_context = other.m_context;
        m_iface = other.m_iface;

        other.m_context = nullptr;
        return *this;
    }

    /** Wrappers for IAudioPlayback functions @{ */
    AudioResult update()
    {
        return m_iface->update(m_context);
    }

    const ContextCaps* getContextCaps()
    {
        return m_iface->getContextCaps(m_context);
    }

    bool setBusCount(size_t count)
    {
        return m_iface->setBusCount(m_context, count);
    }

    AudioResult setOutput(const OutputDesc* desc)
    {
        return m_iface->setOutput(m_context, desc);
    }

    void setContextParameters(ContextParamFlags paramsToSet, const ContextParams* params)
    {
        m_iface->setContextParameters(m_context, paramsToSet, params);
    }

    void getContextParameters(ContextParamFlags paramsToGet, ContextParams* params)
    {
        m_iface->getContextParameters(m_context, paramsToGet, params);
    }

    PythonVoice* playSound(PythonSoundData* sound,
                           PlayFlags flags,
                           VoiceParamFlags validParams,
                           VoiceParams* params,
                           EventPoint* loopPoint,
                           size_t playStart,
                           size_t playLength,
                           UnitType playUnits)
    {
        PlaySoundDesc desc = {};
        desc.flags = flags;
        desc.sound = sound->getNativeObject();
        desc.validParams = validParams;
        desc.params = params;
        desc.loopPoint.loopPoint = loopPoint;
        if (loopPoint != nullptr)
        {
            desc.loopPoint.loopPointIndex = 0;
        }

        desc.playStart = playStart;
        desc.playLength = playLength;
        desc.playUnits = playUnits;
        return new PythonVoice(m_iface, m_iface->playSound(m_context, &desc));
    }
    /** @} */

private:
    Context* m_context;
    IAudioPlayback* m_iface;
};


// *************************** Binding definition helper functions *******************
namespace detail
{

inline void definePythonModuleExceptions(py::module& m)
{
    // these C++ exception types will be automatically translated to the corresponding python
    // exception if they are thrown while calling into a binding.
    py::register_exception<SoundDataError>(m, "SoundDataError");
    py::register_exception<NotAvailable>(m, "NotAvailable");
    py::register_exception<DecoderError>(m, "DecoderError");
    py::register_exception<EncoderError>(m, "EncoderError");
    py::register_exception<ReadOnly>(m, "ReadOnly");
    py::register_exception<ContextError>(m, "ContextError");
}

inline void definePythonModuleConstants(py::module& m)
{
    /////// AudioTypes.h ///////
    m.attr("MAX_NAME_LENGTH") = py::int_(kMaxNameLength);
    m.attr("MAX_CHANNELS") = py::int_(kMaxChannels);
    m.attr("MIN_CHANNELS") = py::int_(kMinChannels);
    m.attr("MAX_FRAMERATE") = py::int_(kMaxFrameRate);
    m.attr("MIN_FRAMERATE") = py::int_(kMinFrameRate);

    m.attr("SPEAKER_FLAG_FRONT_LEFT") = py::int_(fSpeakerFlagFrontLeft);
    m.attr("SPEAKER_FLAG_FRONT_RIGHT") = py::int_(fSpeakerFlagFrontRight);
    m.attr("SPEAKER_FLAG_FRONT_CENTER") = py::int_(fSpeakerFlagFrontCenter);
    m.attr("SPEAKER_FLAG_LOW_FREQUENCY_EFFECT") = py::int_(fSpeakerFlagLowFrequencyEffect);
    m.attr("SPEAKER_FLAG_BACK_LEFT") = py::int_(fSpeakerFlagSideLeft);
    m.attr("SPEAKER_FLAG_BACK_RIGHT") = py::int_(fSpeakerFlagSideRight);
    m.attr("SPEAKER_FLAG_BACK_CENTER") = py::int_(fSpeakerFlagBackLeft);
    m.attr("SPEAKER_FLAG_SIDE_LEFT") = py::int_(fSpeakerFlagBackRight);
    m.attr("SPEAKER_FLAG_SIDE_RIGHT") = py::int_(fSpeakerFlagBackCenter);
    m.attr("SPEAKER_FLAG_TOP_FRONT_LEFT") = py::int_(fSpeakerFlagTopFrontLeft);
    m.attr("SPEAKER_FLAG_TOP_FRONT_RIGHT") = py::int_(fSpeakerFlagTopFrontRight);
    m.attr("SPEAKER_FLAG_TOP_BACK_LEFT") = py::int_(fSpeakerFlagTopBackLeft);
    m.attr("SPEAKER_FLAG_TOP_BACK_RIGHT") = py::int_(fSpeakerFlagTopBackRight);
    m.attr("SPEAKER_FLAG_FRONT_LEFT_WIDE") = py::int_(fSpeakerFlagFrontLeftWide);
    m.attr("SPEAKER_FLAG_FRONT_RIGHT_WIDE") = py::int_(fSpeakerFlagFrontRightWide);
    m.attr("SPEAKER_FLAG_TOP_LEFT") = py::int_(fSpeakerFlagTopLeft);
    m.attr("SPEAKER_FLAG_TOP_RIGHT") = py::int_(fSpeakerFlagTopRight);

    m.attr("INVALID_SPEAKER_NAME") = py::int_(kInvalidSpeakerName);
    m.attr("SPEAKER_MODE_DEFAULT") = py::int_(kSpeakerModeDefault);
    m.attr("SPEAKER_MODE_MONO") = py::int_(kSpeakerModeMono);
    m.attr("SPEAKER_MODE_STEREO") = py::int_(kSpeakerModeStereo);
    m.attr("SPEAKER_MODE_TWO_POINT_ONE") = py::int_(kSpeakerModeTwoPointOne);
    m.attr("SPEAKER_MODE_QUAD") = py::int_(kSpeakerModeQuad);
    m.attr("SPEAKER_MODE_FOUR_POINT_ONE") = py::int_(kSpeakerModeFourPointOne);
    m.attr("SPEAKER_MODE_FIVE_POINT_ONE") = py::int_(kSpeakerModeFivePointOne);
    m.attr("SPEAKER_MODE_SIX_POINT_ONE") = py::int_(kSpeakerModeSixPointOne);
    m.attr("SPEAKER_MODE_SEVEN_POINT_ONE") = py::int_(kSpeakerModeSevenPointOne);
    m.attr("SPEAKER_MODE_NINE_POINT_ONE") = py::int_(kSpeakerModeNinePointOne);
    m.attr("SPEAKER_MODE_SEVEN_POINT_ONE_POINT_FOUR") = py::int_(kSpeakerModeSevenPointOnePointFour);
    m.attr("SPEAKER_MODE_NINE_POINT_ONE_POINT_FOUR") = py::int_(kSpeakerModeNinePointOnePointFour);
    m.attr("SPEAKER_MODE_NINE_POINT_ONE_POINT_SIX") = py::int_(kSpeakerModeNinePointOnePointSix);
    m.attr("SPEAKER_MODE_THREE_POINT_ZERO") = py::int_(kSpeakerModeThreePointZero);
    m.attr("SPEAKER_MODE_FIVE_POINT_ZERO") = py::int_(kSpeakerModeFivePointZero);
    m.attr("SPEAKER_MODE_COUNT") = py::int_(kSpeakerModeCount);
    m.attr("SPEAKER_MODE_VALID_BITS") = py::int_(fSpeakerModeValidBits);

    m.attr("DEVICE_FLAG_NOT_OPEN") = py::int_(fDeviceFlagNotOpen);
    m.attr("DEVICE_FLAG_CONNECTED") = py::int_(fDeviceFlagConnected);
    m.attr("DEVICE_FLAG_DEFAULT") = py::int_(fDeviceFlagDefault);
    m.attr("DEVICE_FLAG_STREAMER") = py::int_(fDeviceFlagStreamer);

    // this is intentionally not bound since there is currently no python
    // functionality that could make use of this behavior
    // m.attr("AUDIO_IMAGE_FLAG_NO_CLEAR") = py::int_(fAudioImageNoClear);
    m.attr("AUDIO_IMAGE_FLAG_USE_LINES") = py::int_(fAudioImageUseLines);
    m.attr("AUDIO_IMAGE_FLAG_NOISE_COLOR") = py::int_(fAudioImageNoiseColor);
    m.attr("AUDIO_IMAGE_FLAG_MULTI_CHANNEL") = py::int_(fAudioImageMultiChannel);
    m.attr("AUDIO_IMAGE_FLAG_ALPHA_BLEND") = py::int_(fAudioImageAlphaBlend);
    m.attr("AUDIO_IMAGE_FLAG_SPLIT_CHANNELS") = py::int_(fAudioImageSplitChannels);

    m.attr("INVALID_DEVICE_INDEX") = py::int_(kInvalidDeviceIndex);

    m.attr("DEFAULT_FRAME_RATE") = py::int_(kDefaultFrameRate);
    m.attr("DEFAULT_CHANNEL_COUNT") = py::int_(kDefaultChannelCount);

    m.attr("DEFAULT_FORMAT") = py::int_((int)kDefaultFormat);

    /////// IAudioPlayback.h ///////
    m.attr("CONTEXT_FLAG_BAKING") = py::int_(fContextFlagBaking);
    m.attr("CONTEXT_FLAG_MANUAL_STOP") = py::int_(fContextFlagManualStop);

    m.attr("OUTPUT_FLAG_DEVICE") = py::int_(fOutputFlagDevice);

    m.attr("CONTEXT_PARAM_ALL") = py::int_(fContextParamAll);
    m.attr("CONTEXT_PARAM_SPEED_OF_SOUND") = py::int_(fContextParamSpeedOfSound);
    m.attr("CONTEXT_PARAM_WORLD_UNIT_SCALE") = py::int_(fContextParamWorldUnitScale);
    m.attr("CONTEXT_PARAM_LISTENER") = py::int_(fContextParamListener);
    m.attr("CONTEXT_PARAM_DOPPLER_SCALE") = py::int_(fContextParamDopplerScale);
    m.attr("CONTEXT_PARAM_VIRTUALIZATION_THRESHOLD") = py::int_(fContextParamVirtualizationThreshold);
    m.attr("CONTEXT_PARAM_SPATIAL_FREQUENCY_RATIO") = py::int_(fContextParamSpatialFrequencyRatio);
    m.attr("CONTEXT_PARAM_NON_SPATIAL_FREQUENCY_RATIO") = py::int_(fContextParamNonSpatialFrequencyRatio);
    m.attr("CONTEXT_PARAM_MASTER_VOLUME") = py::int_(fContextParamMasterVolume);
    m.attr("CONTEXT_PARAM_SPATIAL_VOLUME") = py::int_(fContextParamSpatialVolume);
    m.attr("CONTEXT_PARAM_NON_SPATIAL_VOLUME") = py::int_(fContextParamNonSpatialVolume);
    m.attr("CONTEXT_PARAM_DOPPLER_LIMIT") = py::int_(fContextParamDopplerLimit);
    m.attr("CONTEXT_PARAM_DEFAULT_PLAYBACK_MODE") = py::int_(fContextParamDefaultPlaybackMode);
    m.attr("CONTEXT_PARAM_VIDEO_LATENCY") = py::int_(fContextParamVideoLatency);

    m.attr("DEFAULT_SPEED_OF_SOUND") = py::float_(kDefaultSpeedOfSound);

    m.attr("VOICE_PARAM_ALL") = py::int_(fVoiceParamAll);
    m.attr("VOICE_PARAM_PLAYBACK_MODE") = py::int_(fVoiceParamPlaybackMode);
    m.attr("VOICE_PARAM_VOLUME") = py::int_(fVoiceParamVolume);
    m.attr("VOICE_PARAM_MUTE") = py::int_(fVoiceParamMute);
    m.attr("VOICE_PARAM_BALANCE") = py::int_(fVoiceParamBalance);
    m.attr("VOICE_PARAM_FREQUENCY_RATIO") = py::int_(fVoiceParamFrequencyRatio);
    m.attr("VOICE_PARAM_PRIORITY") = py::int_(fVoiceParamPriority);
    m.attr("VOICE_PARAM_PAUSE") = py::int_(fVoiceParamPause);
    m.attr("VOICE_PARAM_SPATIAL_MIX_LEVEL") = py::int_(fVoiceParamSpatialMixLevel);
    m.attr("VOICE_PARAM_DOPPLER_SCALE") = py::int_(fVoiceParamDopplerScale);
    m.attr("VOICE_PARAM_OCCLUSION_FACTOR") = py::int_(fVoiceParamOcclusionFactor);
    m.attr("VOICE_PARAM_EMITTER") = py::int_(fVoiceParamEmitter);
    m.attr("VOICE_PARAM_MATRIX") = py::int_(fVoiceParamMatrix);

    m.attr("PLAYBACK_MODE_SPATIAL") = py::int_(fPlaybackModeSpatial);
    m.attr("PLAYBACK_MODE_LISTENER_RELATIVE") = py::int_(fPlaybackModeListenerRelative);
    m.attr("PLAYBACK_MODE_DISTANCE_DELAY") = py::int_(fPlaybackModeDistanceDelay);
    m.attr("PLAYBACK_MODE_INTERAURAL_DELAY") = py::int_(fPlaybackModeInterauralDelay);
    m.attr("PLAYBACK_MODE_USE_DOPPLER") = py::int_(fPlaybackModeUseDoppler);
    m.attr("PLAYBACK_MODE_USE_REVERB") = py::int_(fPlaybackModeUseReverb);
    m.attr("PLAYBACK_MODE_USE_FILTERS") = py::int_(fPlaybackModeUseFilters);
    m.attr("PLAYBACK_MODE_MUTED") = py::int_(fPlaybackModeMuted);
    m.attr("PLAYBACK_MODE_PAUSED") = py::int_(fPlaybackModePaused);
    m.attr("PLAYBACK_MODE_FADE_IN") = py::int_(fPlaybackModeFadeIn);
    m.attr("PLAYBACK_MODE_SIMULATE_POSITION") = py::int_(fPlaybackModeSimulatePosition);
    m.attr("PLAYBACK_MODE_NO_POSITION_SIMULATION") = py::int_(fPlaybackModeNoPositionSimulation);
    m.attr("PLAYBACK_MODE_SPATIAL_MIX_LEVEL_MATRIX") = py::int_(fPlaybackModeSpatialMixLevelMatrix);
    m.attr("PLAYBACK_MODE_NO_SPATIAL_LOW_FREQUENCY_EFFECT") = py::int_(fPlaybackModeNoSpatialLowFrequencyEffect);
    m.attr("PLAYBACK_MODE_STOP_ON_SIMULATION") = py::int_(fPlaybackModeStopOnSimulation);
    m.attr("PLAYBACK_MODE_DEFAULT_USE_DOPPLER") = py::int_(fPlaybackModeDefaultUseDoppler);
    m.attr("PLAYBACK_MODE_DEFAULT_DISTANCE_DELAY") = py::int_(fPlaybackModeDefaultDistanceDelay);
    m.attr("PLAYBACK_MODE_DEFAULT_INTERAURAL_DELAY") = py::int_(fPlaybackModeDefaultInterauralDelay);
    m.attr("PLAYBACK_MODE_DEFAULT_USE_REVERB") = py::int_(fPlaybackModeDefaultUseReverb);
    m.attr("PLAYBACK_MODE_DEFAULT_USE_FILTERS") = py::int_(fPlaybackModeDefaultUseFilters);

    m.attr("ENTITY_FLAG_ALL") = py::int_(fEntityFlagAll);
    m.attr("ENTITY_FLAG_POSITION") = py::int_(fEntityFlagPosition);
    m.attr("ENTITY_FLAG_VELOCITY") = py::int_(fEntityFlagVelocity);
    m.attr("ENTITY_FLAG_FORWARD") = py::int_(fEntityFlagForward);
    m.attr("ENTITY_FLAG_UP") = py::int_(fEntityFlagUp);
    m.attr("ENTITY_FLAG_CONE") = py::int_(fEntityFlagCone);
    m.attr("ENTITY_FLAG_ROLLOFF") = py::int_(fEntityFlagRolloff);

    m.attr("ENTITY_FLAG_MAKE_PERP") = py::int_(fEntityFlagMakePerp);
    m.attr("ENTITY_FLAG_NORMALIZE") = py::int_(fEntityFlagNormalize);

    m.attr("INSTANCES_UNLIMITED") = py::int_(kInstancesUnlimited);

    m.attr("CONE_ANGLE_OMNI_DIRECTIONAL") = py::float_(kConeAngleOmnidirectional);

    // this won't be done through flags in python
    // m.attr("DATA_FLAG_FORMAT_MASK") = py::int_(fDataFlagFormatMask);
    // m.attr("DATA_FLAG_FORMAT_AUTO") = py::int_(fDataFlagFormatAuto);
    // m.attr("DATA_FLAG_FORMAT_RAW") = py::int_(fDataFlagFormatRaw);
    // m.attr("DATA_FLAG_IN_MEMORY") = py::int_(fDataFlagInMemory);
    // m.attr("DATA_FLAG_STREAM") = py::int_(fDataFlagStream);
    // m.attr("DATA_FLAG_DECODE") = py::int_(fDataFlagDecode);
    // m.attr("DATA_FLAG_FORMAT_PCM") = py::int_(fDataFlagFormatPcm);
    // m.attr("DATA_FLAG_EMPTY") = py::int_(fDataFlagEmpty);
    // m.attr("DATA_FLAG_NO_NAME") = py::int_(fDataFlagNoName);
    // this won't ever be supported in python
    // m.attr("DATA_FLAG_USER_MEMORY") = py::int_(fDataFlagUserMemory);
    // not supported yet - we may not support it
    // m.attr("DATA_FLAG_USER_DECODE") = py::int_(fDataFlagUserDecode);
    m.attr("DATA_FLAG_SKIP_METADATA") = py::int_(fDataFlagSkipMetaData);
    m.attr("DATA_FLAG_SKIP_EVENT_POINTS") = py::int_(fDataFlagSkipEventPoints);
    m.attr("DATA_FLAG_CALC_PEAKS") = py::int_(fDataFlagCalcPeaks);

    m.attr("SAVE_FLAG_DEFAULT") = py::int_(fSaveFlagDefault);
    m.attr("SAVE_FLAG_STRIP_METADATA") = py::int_(fSaveFlagStripMetaData);
    m.attr("SAVE_FLAG_STRIP_EVENT_POINTS") = py::int_(fSaveFlagStripEventPoints);
    m.attr("SAVE_FLAG_STRIP_PEAKS") = py::int_(fSaveFlagStripPeaks);

    m.attr("MEMORY_LIMIT_THRESHOLD") = py::int_(kMemoryLimitThreshold);

    m.attr("META_DATA_TAG_ARCHIVAL_LOCATION") = std::string(kMetaDataTagArchivalLocation);
    m.attr("META_DATA_TAG_COMMISSIONED") = std::string(kMetaDataTagCommissioned);
    m.attr("META_DATA_TAG_CROPPED") = std::string(kMetaDataTagCropped);
    m.attr("META_DATA_TAG_DIMENSIONS") = std::string(kMetaDataTagDimensions);
    m.attr("META_DATA_TAG_DISC") = std::string(kMetaDataTagDisc);
    m.attr("META_DATA_TAG_DPI") = std::string(kMetaDataTagDpi);
    m.attr("META_DATA_TAG_EDITOR") = std::string(kMetaDataTagEditor);
    m.attr("META_DATA_TAG_ENGINEER") = std::string(kMetaDataTagEngineer);
    m.attr("META_DATA_TAG_KEYWORDS") = std::string(kMetaDataTagKeywords);
    m.attr("META_DATA_TAG_LANGUAGE") = std::string(kMetaDataTagLanguage);
    m.attr("META_DATA_TAG_LIGHTNESS") = std::string(kMetaDataTagLightness);
    m.attr("META_DATA_TAG_MEDIUM") = std::string(kMetaDataTagMedium);
    m.attr("META_DATA_TAG_PALETTE_SETTING") = std::string(kMetaDataTagPaletteSetting);
    m.attr("META_DATA_TAG_SUBJECT") = std::string(kMetaDataTagSubject);
    m.attr("META_DATA_TAG_SOURCE_FORM") = std::string(kMetaDataTagSourceForm);
    m.attr("META_DATA_TAG_SHARPNESS") = std::string(kMetaDataTagSharpness);
    m.attr("META_DATA_TAG_TECHNICIAN") = std::string(kMetaDataTagTechnician);
    m.attr("META_DATA_TAG_WRITER") = std::string(kMetaDataTagWriter);
    m.attr("META_DATA_TAG_ALBUM") = std::string(kMetaDataTagAlbum);
    m.attr("META_DATA_TAG_ARTIST") = std::string(kMetaDataTagArtist);
    m.attr("META_DATA_TAG_COPYRIGHT") = std::string(kMetaDataTagCopyright);
    m.attr("META_DATA_TAG_CREATION_DATE") = std::string(kMetaDataTagCreationDate);
    m.attr("META_DATA_TAG_DESCRIPTION") = std::string(kMetaDataTagDescription);
    m.attr("META_DATA_TAG_GENRE") = std::string(kMetaDataTagGenre);
    m.attr("META_DATA_TAG_ORGANIZATION") = std::string(kMetaDataTagOrganization);
    m.attr("META_DATA_TAG_TITLE") = std::string(kMetaDataTagTitle);
    m.attr("META_DATA_TAG_TRACK_NUMBER") = std::string(kMetaDataTagTrackNumber);
    m.attr("META_DATA_TAG_ENCODER") = std::string(kMetaDataTagEncoder);
    m.attr("META_DATA_TAG_ISRC") = std::string(kMetaDataTagISRC);
    m.attr("META_DATA_TAG_LICENSE") = std::string(kMetaDataTagLicense);
    m.attr("META_DATA_TAG_PERFORMER") = std::string(kMetaDataTagPerformer);
    m.attr("META_DATA_TAG_VERSION") = std::string(kMetaDataTagVersion);
    m.attr("META_DATA_TAG_LOCATION") = std::string(kMetaDataTagLocation);
    m.attr("META_DATA_TAG_CONTACT") = std::string(kMetaDataTagContact);
    m.attr("META_DATA_TAG_COMMENT") = std::string(kMetaDataTagComment);
    m.attr("META_DATA_TAG_SPEED") = std::string(kMetaDataTagSpeed);
    m.attr("META_DATA_TAG_START_TIME") = std::string(kMetaDataTagStartTime);
    m.attr("META_DATA_TAG_END_TIME") = std::string(kMetaDataTagEndTime);
    m.attr("META_DATA_TAG_SUBGENRE") = std::string(kMetaDataTagSubGenre);
    m.attr("META_DATA_TAG_BPM") = std::string(kMetaDataTagBpm);
    m.attr("META_DATA_TAG_PLAYLIST_DELAY") = std::string(kMetaDataTagPlaylistDelay);
    m.attr("META_DATA_TAG_FILE_NAME") = std::string(kMetaDataTagFileName);
    m.attr("META_DATA_TAG_ALBUM") = std::string(kMetaDataTagOriginalAlbum);
    m.attr("META_DATA_TAG_WRITER") = std::string(kMetaDataTagOriginalWriter);
    m.attr("META_DATA_TAG_PERFORMER") = std::string(kMetaDataTagOriginalPerformer);
    m.attr("META_DATA_TAG_ORIGINAL_YEAR") = std::string(kMetaDataTagOriginalYear);
    m.attr("META_DATA_TAG_PUBLISHER") = std::string(kMetaDataTagPublisher);
    m.attr("META_DATA_TAG_RECORDING_DATE") = std::string(kMetaDataTagRecordingDate);
    m.attr("META_DATA_TAG_INTERNET_RADIO_STATION_NAME") = std::string(kMetaDataTagInternetRadioStationName);
    m.attr("META_DATA_TAG_INTERNET_RADIO_STATION_OWNER") = std::string(kMetaDataTagInternetRadioStationOwner);
    m.attr("META_DATA_TAG_INTERNET_RADIO_STATION_URL") = std::string(kMetaDataTagInternetRadioStationUrl);
    m.attr("META_DATA_TAG_PAYMENT_URL") = std::string(kMetaDataTagPaymentUrl);
    m.attr("META_DATA_TAG_INTERNET_COMMERCIAL_INFORMATION_URL") =
        std::string(kMetaDataTagInternetCommercialInformationUrl);
    m.attr("META_DATA_TAG_INTERNET_COPYRIGHT_URL") = std::string(kMetaDataTagInternetCopyrightUrl);
    m.attr("META_DATA_TAG_WEBSITE") = std::string(kMetaDataTagWebsite);
    m.attr("META_DATA_TAG_INTERNET_ARTIST_WEBSITE") = std::string(kMetaDataTagInternetArtistWebsite);
    m.attr("META_DATA_TAG_AUDIO_SOURCE_WEBSITE") = std::string(kMetaDataTagAudioSourceWebsite);
    m.attr("META_DATA_TAG_COMPOSER") = std::string(kMetaDataTagComposer);
    m.attr("META_DATA_TAG_OWNER") = std::string(kMetaDataTagOwner);
    m.attr("META_DATA_TAG_TERMS_OF_USE") = std::string(kMetaDataTagTermsOfUse);
    m.attr("META_DATA_TAG_INITIAL_KEY") = std::string(kMetaDataTagInitialKey);

    m.attr("META_DATA_TAG_CLEAR_ALL_TAGS") = kMetaDataTagClearAllTags;

    m.attr("EVENT_POINT_INVALID_FRAME") = py::int_(kEventPointInvalidFrame);
    m.attr("EVENT_POINT_LOOP_INFINITE") = py::int_(kEventPointLoopInfinite);
}

inline void definePythonModuleEnums(py::module& m)
{
    const char* docString;


    /** AudioResult enum binding definitions.
     *  @{
     */
    docString = "Possible result codes for audio operations.";
    py::enum_<AudioResult> audioResult(m, "AudioResult", docString);
    docString = "The operation either completed successfully or was successfully queued to complete asynchronously.";
    audioResult.value("OK", AudioResult::eOk, docString);
    docString =
        "The device that was in use was physically disconnected from the system.  There is no possibility of using it again until it is reconnected to the system.";
    audioResult.value("DEVICE_DISCONNECTED", AudioResult::eDeviceDisconnected, docString);
    docString =
        "The device that was in use lost its connection to the software.  This mostly occurs on Linux under the ALSA backend.";
    audioResult.value("DEVICE_LOST", AudioResult::eDeviceLost, docString);
    docString = "The requested device has not been opened yet but the requested operation requires that it be open.";
    audioResult.value("DEVICE_NOT_OPEN", AudioResult::eDeviceNotOpen, docString);
    docString = "The requested device has been opened but the requested operation requires that it not be open.";
    audioResult.value("DEVICE_OPEN", AudioResult::eDeviceOpen, docString);
    docString = "The requested device index or parameter value was outside of the accepted range.";
    audioResult.value("OUT_OF_RANGE", AudioResult::eOutOfRange, docString);
    docString =
        "The operation failed on this attempt but may succeed if tried again at a later time.  This is often related to hardware resources that may be busy at the time.";
    audioResult.value("TRY_AGAIN", AudioResult::eTryAgain, docString);
    docString = "The requested amount of memory could not be allocated for the current operation.";
    audioResult.value("OUT_OF_MEMORY", AudioResult::eOutOfMemory, docString);
    docString = "One or more invalid parameters was passed in to a function.";
    audioResult.value("INVALID_PARAMETER", AudioResult::eInvalidParameter, docString);
    docString = "The requested operation is not allowed at this time.";
    audioResult.value("NOT_ALLOWED", AudioResult::eNotAllowed, docString);
    docString = "The requested resource could not be found or is not known.";
    audioResult.value("NOT_FOUND", AudioResult::eNotFound, docString);
    docString = "A hardware I/O error occurred during the operation.";
    audioResult.value("IO_ERROR", AudioResult::eIoError, docString);
    docString = "An invalid sound format was requested for an audio capture or data seek operation.";
    audioResult.value("INVALID_FORMAT", AudioResult::eInvalidFormat, docString);
    docString = "The requested operation, data format, or feature is not supported.";
    audioResult.value("NOT_SUPPORTED", AudioResult::eNotSupported, docString);
    /** @} */


    /** Speaker enum binding definition.
     *  @{
     */
    docString =
        "Names for each supported standard speaker.  Positions are given relative to the unit circle "
        "where the listener is at the circle's center and angles run in the clockwise direction with "
        "0 degrees being directly in front of the listener.  Note that some of these speakers may have "
        "different positions depending on the overall speaker layout.  For example, in a stereo layout "
        "the 'front left' and 'front right' speakers are typically used but are located at 270 and 90 "
        "degrees respectively instead of 315 and 45 degrees.";
    py::enum_<Speaker> speaker(m, "Speaker", docString);
    docString = "The front left speaker.  Usually located at 315 degrees and an inclination of 0 degrees.";
    speaker.value("FRONT_LEFT", Speaker::eFrontLeft, docString);
    docString = "The front right speaker.  Usually located at 45 degrees and an inclination of 0 degrees.";
    speaker.value("FRONT_RIGHT", Speaker::eFrontRight, docString);
    docString = "The front center speaker.  Usually located at 0 degrees and an inclination of 0 degrees.";
    speaker.value("FRONT_CENTER", Speaker::eFrontCenter, docString);
    docString =
        "The low frequency (ie: subwoofer) channel.  This is always treated as a non-directional source and "
        "behaves mathematically as if it were located at the listener's position.";
    speaker.value("LOW_FREQUENCY_EFFECT", Speaker::eLowFrequencyEffect, docString);
    docString = "The back left speaker.  Usually located at 225 degrees and an inclination of 0 degrees.";
    speaker.value("BACK_LEFT", Speaker::eBackLeft, docString);
    docString = "The back right speaker.  Usually located at 135 degrees and an inclination of 0 degrees.";
    speaker.value("BACK_RIGHT", Speaker::eBackRight, docString);
    docString = "The back center speaker.  Usually located at 180 degrees and an inclination of 0 degrees.";
    speaker.value("BACK_CENTER", Speaker::eBackCenter, docString);
    docString = "The side left speaker.  Usually located at 270 degrees and an inclination of 0 degrees.";
    speaker.value("SIDE_LEFT", Speaker::eSideLeft, docString);
    docString = "The side right speaker.  Usually located at 90 degrees and an inclination of 0 degrees.";
    speaker.value("SIDE_RIGHT", Speaker::eSideRight, docString);
    docString = "The top front left speaker.  Usually located at 315 degrees and an inclination of 45 degrees.";
    speaker.value("TOP_FRONT_LEFT", Speaker::eTopFrontLeft, docString);
    docString = "The top front right speaker.  Usually located at 45 degrees and an inclination of 45 degrees.";
    speaker.value("TOP_FRONT_RIGHT", Speaker::eTopFrontRight, docString);
    docString = "The top back left speaker.  Usually located at 225 degrees and an inclination of 45 degrees.";
    speaker.value("TOP_BACK_LEFT", Speaker::eTopBackLeft, docString);
    docString = "The top back right speaker.  Usually located at 135 degrees and an inclination of 45 degrees.";
    speaker.value("TOP_BACK_RIGHT", Speaker::eTopBackRight, docString);
    docString = "The front left wide speaker.  Usually located at 300 degrees and an inclination of 0 degrees.";
    speaker.value("FRONT_LEFT_WIDE", Speaker::eFrontLeftWide, docString);
    docString = "The front right wide speaker.  Usually located at 60 degrees and an inclination of 0 degrees.";
    speaker.value("FRONT_RIGHT_WIDE", Speaker::eFrontRightWide, docString);
    docString = "The top left speaker.  Usually located at 270 degrees and an inclination of 45 degrees.";
    speaker.value("TOP_LEFT", Speaker::eTopLeft, docString);
    docString = "The top right speaker.  Usually located at 90 degrees and an inclination of 45 degrees.";
    speaker.value("TOP_RIGHT", Speaker::eTopRight, docString);
    docString = "The total number of supported standard speaker names.  This is not a valid speaker name.";
    speaker.value("COUNT", Speaker::eCount, docString);
    /** @} */


    /** SampleFormat enum binding definition.
     *  @{
     */
    docString =
        "the data type for a single sample of raw audio data.  This describes how each sample in "
        "the data buffer should be interpreted.  In general, audio data can only be uncompressed "
        "Pulse Code Modulation (PCM) data, or encoded in some kind of compressed format.";
    py::enum_<SampleFormat> sampleFormat(m, "SampleFormat", docString);
    docString =
        "8 bits per sample unsigned integer PCM data.  Sample values will range from 0 to 255 with a value "
        "of 128 being 'silence'.";
    sampleFormat.value("PCM8", SampleFormat::ePcm8, docString);
    docString =
        "16 bits per sample signed integer PCM data.  Sample values will range from -32768 to 32767 with a "
        "value of 0 being 'silence'.";
    sampleFormat.value("PCM16", SampleFormat::ePcm16, docString);
    docString =
        "24 bits per sample signed integer PCM data.  Sample values will range from -16777216 to 16777215 "
        "with a value of 0 being 'silence'.";
    sampleFormat.value("PCM24", SampleFormat::ePcm24, docString);
    docString =
        "32 bits per sample signed integer PCM data.  Sample values will range from -2147483648 to 2147483647 "
        "with a value of 0 being 'silence'.";
    sampleFormat.value("PCM32", SampleFormat::ePcm32, docString);
    docString =
        "32 bits per sample floating point PCM data.  Sample values will range from -1.0 to 1.0 with a value "
        "of 0.0 being 'silence'.  Note that floating point samples can extend out of their range (-1.0 to 1.0) "
        "without a problem during mixing.  However, once the data reaches the device, any samples beyond the "
        "range from -1.0 to 1.0 will clip and cause distortion artifacts.";
    sampleFormat.value("PCM_FLOAT", SampleFormat::ePcmFloat, docString);
    docString =
        "The total number of PCM formats.  This is not a valid format and is only used internally to determine "
        "how many PCM formats are available.";
    sampleFormat.value("PCM_COUNT", SampleFormat::ePcmCount, docString);
    docString = R"(The Vorbis codec.  Vorbis is a lossy compressed codec that is capable of producing high quality
                   audio that is difficult to differentiate from lossless codecs.  Vorbis is suitable for music and
                   other applications that require minimal quality loss.  Vorbis is stored in Ogg file containers
                   (.ogg or .oga).  Vorbis has a variable block size, with a maximum of 8192 frames per block, which
                   makes it non-optimal for low latency audio transfer (e.g. voice chat); additionally, the Ogg
                   container combines Vorbis blocks into chunks that can be seconds long.  The `libvorbis` library
                   will accept frame rates of 1Hz - 200KHz (Note that `IAudioPlayback` does not supports framerates
                   below 1KHz).  Vorbis is able to handle up to 255 channels, but sounds with more than 8 channels
                   have no official ordering. (Note that `IAudioPlayback` does not support more than 64 channels).

                   Vorbis has a defined channel mapping for audio with 1-8 channels.  Channel counts 3 and 5 have an
                   incompatible speaker layout with the default layouts in `carb.audio`.  A 3 channel layout uses
                   a 3.0 standard layout (front left and right, plus front center).  A 5 channel layout uses a 5.0
                   standard layout (front left and right, side left and right, plus front center).  For streams with
                   more than 8 channels, the mapping is undefined and must be determined by the application.)";
    sampleFormat.value("VORBIS", SampleFormat::eVorbis, docString);
    docString = R"(The Free Lossless Audio Codec.  This is a codec capable of moderate compression with a perfect
                   reproduction of the original uncompressed signal.  This encodes and decodes reasonably fast, but
                   the file size is much larger than the size of a high quality lossy codec.  This is suitable in
                   applications where audio data will be repeatedly encoded, such as an audio editor.  Unlike a
                   lossy codec, repeatedly encoding the file with FLAC will not degrade the quality.  FLAC is very
                   fast to encode and decode compared to other compressed codecs.  Note that FLAC only stores integer
                   data, so audio of type `PCM_FLOAT` will lose precision when stored as FLAC.  Additionally, the FLAC
                   encoder used only supports up to 24 bit, so `PCM32` will lose some precision when being stored if
                   there are more than 24 valid bits per sample.  FLAC supports frame rates from 1Hz - 655350Hz (Note
                   that `IAudioPlayback` only support framerates of 1KHz to 200KHz).  FLAC supports up to 8 channels.)";
    sampleFormat.value("FLAC", SampleFormat::eFlac, docString);
    docString = R"(The Opus codec.  This is a lossy codec that is designed to be suitable for almost any application.
                   Opus can encode very high quality lossy audio, similarly to `VORBIS`.  Opus can encode very low
                   bitrate audio at a much higher quality than `VORBIS`.  Opus also offers much lower bitrates than
                   `VORBIS`.  Opus is designed for low latency usage, with a minimum latency of 5ms and a block size
                   configurable between 2.5ms and 60ms.  Opus also offers forward error correction to handle packet
                   loss during transmission.

                   Opus is stored in Ogg file containers (.ogg or .oga), but in use cases such as network transmission,
                   Ogg containers are not necessary.  Opus only supports sample rates of 48000Hz, 24000Hz, 16000Hz,
                   12000Hz and 8000Hz.  Passing unsupported frame rates below 48KHz to the encoder will result in the
                   input audio being resampled to the next highest supported frame rate.  Passing frame rates above
                   48KHz to the encoder will result in the input audio being resampled down to 48KHz.  The 'Opus Custom'
                   format, which removes this frame rate restriction, is not supported.

                   Opus has a defined channel mapping for audio with 1-8 channels.  The channel mapping is identical to
                   that of `VORBIS`.  For streams with more than 8 channels, the mapping is undefined and must be
                   determined by the application.  Up to 255 audio channels are supported.

                   Opus has three modes of operation: a linear predictive coding (LPC) mode, a modified discrete cosine
                   transform (MCDT) mode and a hybrid mode which combines both the LPC and MCDT mode.  The LPC mode is
                   optimized to encode voice data at low bitrates and has the ability to use forward error correction
                   and packet loss compensation.  The MCDT mode is suitable for general purpose audio and is optimized
                   for minimal latency.)";
    sampleFormat.value("OPUS", SampleFormat::eOpus, docString);
    docString = R"(MPEG audio layer 3 audio encoding.  This is currently supported for decoding only.  To compress
                   audio with a lossy algorithm, `VORBIS` or `OPUS` should be used.

                   The MP3 decoder currently only has experimental support for seeking.  Files encoded by LAME seem
                   to seek with frame-accurate precision, but results may vary on other encoders.  It is recommended
                   to load the file with `DATA_FLAG_DECODE` if you intend to use frame-accurate loops.

                   MP3 is faster to decode than `VORBIS` and `OPUS`.  This is particularly noticeable because MP3's
                   decoding speed is not affected as significantly by increasing bitrates as with `VORBIS` or `OPUS`.
                   The quality degradation of MP3 with low bitrates is much more severe than with `VORBIS` and `OPUS`,
                   so this difference in performance is not as severe as it may appear.)";
    sampleFormat.value("MP3", SampleFormat::eMp3, docString);
    docString =
        "The data is in an unspecified compressed format.  Being able to interpret the data in the sound "
        "requires extra information on the caller's part.";
    sampleFormat.value("RAW", SampleFormat::eRaw, docString);
    docString =
        "The default or preferred sample format for a device.  This format name is only valid when selecting a "
        "device or decoding data.";
    sampleFormat.value("DEFAULT", SampleFormat::eDefault, docString);
    docString =
        "The number of supported sample formats.  This is not a valid format and is only used internally to "
        "determine how many formats are available.";
    sampleFormat.value("COUNT", SampleFormat::eCount, docString);
    /** @} */


    /** RolloffType enum binding definition.
     *  @{
     */
    docString =
        "Distance based DSP value rolloff curve types.  These represent the formula that will be "
        "used to calculate the spatial DSP values given the distance between an emitter and the "
        "listener.  This represents the default attenuation calculation that will be performed "
        "for all curves that are not overridden with custom curves.  The default rolloff model "
        "will follow the inverse square law (ie: `INVERSE`).";
    py::enum_<RolloffType> rolloffType(m, "RolloffType", docString);
    docString =
        "Defines an inverse attenuation curve where a distance at the 'near' distance is full volume and "
        "at the 'far' distance gives silence.  This is calculated with a formula proportional to "
        "(1 / distance).";
    rolloffType.value("INVERSE", RolloffType::eInverse, docString);
    docString =
        "Defines a linear attenuation curve where a distance at the 'near' distance is full volume and at "
        "the 'far' distance gives silence.  This is calculated with (max - distance) / (max - min).";
    rolloffType.value("LINEAR", RolloffType::eLinear, docString);
    docString =
        "Defines a linear square attenuation curve where a distance at the 'near' distance is full volume "
        "and at the 'far' distance gives silence.  This is calculated with ((max - distance) / (max - min)) ^ 2.";
    rolloffType.value("LINEAR_SQUARE", RolloffType::eLinearSquare, docString);
    /** @} */


    /** UnitType enum binding definition.
     *  @{
     */
    docString = "Description of how a size or offset value is defined.";
    py::enum_<UnitType> unitType(m, "UnitType", docString);
    docString = "The size or offset is given as a byte count.";
    unitType.value("BYTES", UnitType::eBytes, docString);
    docString = "The size or offset is given as a frame count.";
    unitType.value("FRAMES", UnitType::eFrames, docString);
    docString = "The size or offset is given as a time in milliseconds.";
    unitType.value("MILLISECONDS", UnitType::eMilliseconds, docString);
    docString = "The size or offset is given as a time in microseconds.";
    unitType.value("MICROSECONDS", UnitType::eMicroseconds, docString);
    /** @} */
}

inline void definePythonModuleStructs(py::module& m)
{
    const char* docString;


    /** SoundFormat struct binding definition.
     *  @{
     */
    py::class_<Float2Ex> float2Ex(m, "Float2");
    float2Ex.doc() = "A Python friendly replacement of the carb::Float2 struct.";
    float2Ex.def(py::init<float, float>());
    float2Ex.def(py::init<const std::vector<float>&>());
    float2Ex.def_readwrite("x", &Float2Ex::x, "An X coordinate value.");
    float2Ex.def_readwrite("y", &Float2Ex::y, "An Y coordinate value.");
    /** @} */

    /** SoundFormat struct binding definition.
     *  @{
     */
    py::class_<SoundFormat> soundFormat(m, "SoundFormat");
    soundFormat.doc() =
        "Provides information about the format of a sound.  When a sound is loaded from a file, its "
        "format will be implicitly set on load.  The actual format can then be retrieved later with "
        "get_format() on a sound data object.";
    soundFormat.def(py::init<>());
    docString = "The number of channels of data in each frame of the audio data.";
    soundFormat.def_readwrite("channels", &SoundFormat::channels, docString);
    docString =
        "The number of bits per sample of the audio data.  This is also encoded in the `format` value, but it "
        "is given here as well for ease of use in calculations.  This represents the number of bits in the "
        "decoded samples of the sound stream.  This will be 0 for variable bitrate compressed formats.";
    soundFormat.def_readwrite("bits_per_sample", &SoundFormat::bitsPerSample, docString);
    docString =
        "The size in bytes of each frame of data in the format.  A frame consists of one sample per channel.  "
        "This represents the size of a single frame of decoded data from the sound stream.  This will be 0 for "
        "variable bitrate compressed formats.";
    soundFormat.def_readwrite("frame_size", &SoundFormat::frameSize, docString);
    docString =
        "The size in bytes of a single 'block' of encoded data.  For PCM data, this is the same as a frame.  "
        "For formats with a fixed bitrate, this is the size of a single unit of data that can be decoded.  "
        "For formats with a variable bitrate, this will be 0.  Note that certain codecs can be fixed or variable "
        "bitrate depending on the encoder settings.";
    soundFormat.def_readwrite("block_size", &SoundFormat::blockSize, docString);
    docString =
        "The number of frames that will be decoded from a single block of data.  For PCM formats, this will "
        "be 1.  For formats with a fixed number of frames per block, this will be number of frames of data "
        "that will be produced when decoding a single block of data. Note that variable bitrate formats can "
        "have a fixed number of frames per block.  For formats with a variable number of frames per block, "
        "this will be 0.  Note that certain codecs can have a fixed or variable number of frames per block "
        "depending on the encoder settings.";
    soundFormat.def_readwrite("frames_per_block", &SoundFormat::framesPerBlock, docString);
    docString =
        "The number of frames per second that must be played back for the audio data to sound 'normal' (ie: "
        "the way it was recorded or produced).";
    soundFormat.def_readwrite("frame_rate", &SoundFormat::frameRate, docString);
    docString =
        "The channel mask for the audio data.  This specifies which speakers the stream is intended for and "
        "will be a combination of one or more of the `Speaker` names or a `SPEAKER_MODE_*` name.  This may be "
        "calculated from the number of channels present in the original audio data or it may be explicitly "
        "specified in the original audio data on load.";
    soundFormat.def_readwrite("channel_mask", &SoundFormat::channelMask, docString);
    docString =
        "The number of bits of valid data that are present in the audio data.  This may be used to specify "
        "that (for example) a stream of 24-bit sample data is being processed in 32-bit containers.  Each "
        "sample will actually consist of 32-bit data in the buffer, using the full 32-bit range, but only "
        "the top 24 bits of each sample will be valid useful data.  This represents the valid number of bits "
        "per sample in the decoded data for the sound stream.";
    soundFormat.def_readwrite("valid_bits_per_sample", &SoundFormat::validBitsPerSample, docString);
    docString =
        "The format of each sample of audio data.  This is given as a symbolic name so that the data can be "
        "interpreted properly.  The size of each sample in bits is also given in the `bits_per_sample` value.";
    soundFormat.def_readwrite("format", &SoundFormat::format, docString);
    /** @} */


    /** carb::extras::Guid struct binding definition.
     *  @{
     */
    py::class_<carb::extras::Guid> guid(m, "Guid");
    guid.doc() =
        "Representation of a globally unique identifier.  This is a 128 bit identifier that is often "
        "printed in the format '{00000000-0000-0000-0000-000000000000}'.";
    guid.def(py::init<>());

    docString = R"(Converts GUID to string format.

                   Returns:
                       The requested GUID converted to a string.)";
    guid.def("__str__",
             [](const carb::extras::Guid& self) -> std::string {
                 std::string str;
                 carb::extras::guidToString(&self, str);
                 return str;
             },
             docString);

    docString = R"(Converts a string to GUID.

                   Args:
                       src: The source string to be converted to a GUID.  This string may optionally be surrounded
                            with curly braces (ie: "{}").

                   Returns:
                       `True` if the GUID was successfully parsed.
                       `False` if the GUID contained invalid characters or was not in the expected format.)";
    guid.def("from_string",
             [](carb::extras::Guid& self, const char* src) -> bool { return carb::extras::stringToGuid(src, &self); },
             docString, py::arg("src"));
    /** @} */


    /** DeviceCaps struct binding definition.
     *  @{
     */
    py::class_<DeviceCaps> deviceCaps(m, "DeviceCaps");
    deviceCaps.doc() =
        "Contains information about a single audio input or output device.  Note that this information "
        "should not be stored since it can change at any time due to user activity (ie: unplugging a "
        "device, plugging in a new device, changing system default devices, etc).  Device information "
        "should only be queried just before deciding which device to select.";
    docString =
        "The current index of this device in the enumeration order.  Note that this value is highly volatile "
        "and can change at any time due to user action (ie: plugging in or removing a device from the system).  "
        "When a device is added to or removed from the system, the information for the device at this index may "
        "change.  It is the caller's responsibility to refresh its collected device information if the device "
        "list changes.  The device at index 0 will always be considered the system's 'default' device.";
    deviceCaps.def_readwrite("index", &DeviceCaps::index, docString);
    docString =
        "Flags to indicate some attributes about this device.  These may change at any time due to user action "
        "(ie: unplugging a device or switching system defaults).  This may be 0 or any combination of the "
        "`DEVICE_FLAG*` flags.";
    deviceCaps.def_readwrite("flags", &DeviceCaps::flags, docString);
    docString =
        "A GUID that can be used to uniquely identify the device.  The GUID for a given device may not be the "
        "same from one process to the next, or if the device is removed from the system and reattached.  The "
        "GUID will remain constant for the entire time the device is connected to the system however.";
    deviceCaps.def_readwrite("guid", &DeviceCaps::guid, docString);
    docString =
        "The preferred number of channels of data in each frame of the audio data.  Selecting a device using a "
        "different format than this will result in extra processing overhead due to the format conversion.";
    deviceCaps.def_readwrite("channels", &DeviceCaps::channels, docString);
    docString =
        "The preferred number of frames per second that must be played back for the audio data to sound 'normal' "
        "(ie: the way it was recorded or produced).  Selecting a device using a different frame rate than this "
        "will result in extra processing overhead due to the frame rate conversion.";
    deviceCaps.def_readwrite("frame_rate", &DeviceCaps::frameRate, docString);
    docString =
        "The preferred format of each sample of audio data.  This is given as a symbolic name so that the data "
        "can be interpreted properly.  Selecting a device using a different format than this will result in extra "
        "processing overhead due to the format conversion.";
    deviceCaps.def_readwrite("format", &DeviceCaps::format, docString);
    // python doesn't seem to like it when an array member is exposed
    docString =
        "A UTF-8 string that describes the name of the audio device.  This will most often be a 'friendly' name "
        "for the device that is suitable for display to the user.  This cannot be guaranteed for all devices or "
        "platforms since its contents are defined by the device driver.  The string may have been truncated if "
        "it was too long.";
    deviceCaps.def("get_name", [](const DeviceCaps* self) -> const char* { return self->name; }, docString);
    /** @} */


    /** PeakVolumes struct binding definition.
     *  @{
     */
    py::class_<PeakVolumes> peakVolumes(m, "PeakVolumes");
    peakVolumes.doc() =
        "Used to retrieve the peak volume information for a sound data object.  This contains one "
        "volume level per channel in the stream and the frame in the stream at which the peak "
        "occurs.";
    docString = "The number of channels with valid peak data in the arrays below.";
    peakVolumes.def_readwrite("channels", &PeakVolumes::channels, docString);
    // docString = "The frame that each peak volume level occurs at for each channel.  This will be the first frame "
    //            "this peak volume level occurs at if it is reached multiple times in the stream.";
    // peakVolumes.def_readwrite("frame", &PeakVolumes::frame, docString);
    // docString = "The peak volume level that is reached for each channel in the stream.  This will be in the range "
    //            "[0.0, 1.0].  This information can be used to normalize the volume level for a sound.";
    // peakVolumes.def_readwrite("peak", &PeakVolumes::peak, docString);
    docString = "The frame that the overall peak volume occurs at in the sound.";
    peakVolumes.def_readwrite("peak_frame", &PeakVolumes::peakFrame, docString);
    docString = "The peak volume among all channels of data.";
    peakVolumes.def_readwrite("peak_volume", &PeakVolumes::peakVolume, docString);
    /** @} */


    /** EventPoint struct binding definition.
     *  @{
     */
    py::class_<EventPoint> eventPoint(m, "EventPoint");
    eventPoint.doc() = R"(An event point parsed from a data file.  This contains the ID of the event point, its name
                          label (optional), and the frame in the stream at which it should occur.)";
    eventPoint.def(py::init<>());
    docString =
        "The ID of the event point.  This is used to identify it in the file information but is not used "
        "internally except to match up labels or loop points to the event point.";
    eventPoint.def_readwrite("id", &EventPoint::id, docString);
    docString = R"(The frame that the event point occurs at.  This is relative to the start of the stream for the
                   sound.  When updating event points with `set_event_points()`, this can be set to `EVENT_POINT_INVALID_FRAME`
                   to indicate that the event point with the ID `id` should be removed from the sound data object.
                   Otherwise, this frame index must be within the bounds of the sound data object's stream.)";
    eventPoint.def_readwrite("frame", &EventPoint::frame, docString);
    // docString = "The user-friendly label given to this event point.  This may be parsed from a different "
    //            "information chunk in the file and will be matched up later based on the event point ID. This "
    //            "value is optional and may be nullptr.";
    // eventPoint.def_readwrite("label", &EventPoint::label, docString);
    // docString = "Optional text associated with this event point.  This may be additional information related "
    //            "to the event point's position in the stream such as closed captioning text or a message of "
    //            "some sort.  It is the host app's responsibility to interpret and use this text appropriately.  "
    //            "This text will always be UTF-8 encoded.";
    // eventPoint.def_readwrite("text", &EventPoint::text, docString);
    docString =
        "Length of the segment of audio referred to by this event point.  If `length` is non-zero, then "
        "`length` is treated as the number of frames after `frame` that this event point refers to.  "
        "If `length` is zero, then this event point refers to the segment from `frame` to the end of "
        "the sound.  If `loop_count` is non-zero, then the region specified will refer to a looping "
        "region.  If `play_index` is non-zero, then the region can additionally specify the length of "
        "audio to play.";
    eventPoint.def_readwrite("length", &EventPoint::length, docString);
    docString =
        "Number of times this section of audio in the playlist should be played.  The region of audio "
        "to play in a loop is specified by `length`.  If `loop_count` is 0, then this is a non-looping "
        "segment.  If `loop_count` is set to `EVENT_POINT_LOOP_INFINITE`, this specifies that this region "
        "should be looped infinitely.";
    eventPoint.def_readwrite("loop_count", &EventPoint::loopCount, docString);
    docString =
        "An optional method to specify an ordering for the event points or a subset of event points.  A "
        "value of 0 indicates that there is no intended ordering for this event point.  The playlist "
        "indexes will always be a contiguous range starting from 1.  If a user attempts to set a "
        "non-contiguous range of event point playlist indexes on a SoundData, the event point system "
        "will correct this and make the range contiguous.";
    eventPoint.def_readwrite("play_index", &EventPoint::playIndex, docString);
    // FIXME: maybe we want to bind userdata
    /** @} */


    /** ContextCaps struct binding definition.
     *  @{
     */
    py::class_<ContextCaps> ctxCaps(m, "ContextCaps");
    ctxCaps.doc() = R"(The capabilities of the context object.  Some of these values are set
                       at the creation time of the context object.  Others are updated when
                       speaker positions are set or an output device is opened.)";
    docString =
        "The maximum number of data buses to process simultaneously.  This is equivalent to the maximum "
        "number of potentially audible sounds that could possibly affect the output on the speakers.  If "
        "more voices than this are active, the quietest or furthest voice will be deactivated.  This value "
        "is set at creation time of the context object.  This can be changed after creation with "
        "`set_bus_count()`.";
    ctxCaps.def_readonly("max_buses", &ContextCaps::maxBuses, docString);
    docString =
        "The info for the connection to the currently selected device.  If no device is selected, its "
        "`flags` member will be set to `DEVICE_FLAG_NOT_OPEN`.  If a device is selected, its information "
        "will be set in here, including its preferred output format.  Note that the format information "
        "may differ from the information returned by `get_device_caps()` as this is the format that the "
        "audio is being processed at before being sent to the device.";
    ctxCaps.def_readonly("selected_device", &ContextCaps::selectedDevice, docString);
    docString =
        "The output target that is currently in use for the context.  This will provide access to any "
        "streamer objects in use or the index of the currently active output device.  The device index "
        "stored in here will match the one in @ref selectedDevice if a real audio device is in use.";
    ctxCaps.def_readonly("output", &ContextCaps::output, docString);
    /** @} */


    /** ContextParams struct binding definition.
     *  @{
     */
    py::class_<ContextParams> ctxParams(m, "ContextParams");
    ctxParams.doc() = R"(Context parameters block.  This can potentially contain all of a
                         context's parameters and their current values.  This is used to both
                         set and retrieve one or more of a context's parameters in a single
                         call.  The set of `CONTEXT_PARAM_*` flags that are passed to the
                         `get_parameter()` or `set_parameter()` functions on the Context object
                         indicates which values in the block are guaranteed to be valid.)";
    ctxParams.def(py::init<>());
    docString =
        "The speed of sound for the context.  This is valid when the `CONTEXT_PARAM_SPEED_OF_SOUND` "
        "flag is used.  This is measured in meters per second.  This will affect the calculation of "
        "Doppler shift factors and interaural time difference for spatial voices.  The default value "
        "is `DEFAULT_SPEED_OF_SOUND` m/s.  This value can be changed at any time to affect Doppler "
        "calculations globally.  This should only change when the sound environment itself changes "
        "(ie: move from air into water).";
    ctxParams.def_readwrite("speed_of_sound", &ContextParams::speedOfSound, docString);
    docString =
        "The number of arbitrary world units per meter.  This is valid when the `CONTEXT_PARAM_WORLD_UNIT_SCALE` "
        "flag is used.  World units are arbitrary and often determined by the level/world designers.  "
        "For example, if the world units are in feet, this value would need to be set to 3.28.  All "
        "spatial audio calculations are performed in SI units (ie: meters for distance, seconds for "
        "time).  This provides a conversion factor from arbitrary world distance units to SI units.  "
        "This conversion factor will affect all audio distance and velocity calculations.  This defaults "
        "to 1.0, indicating that the world units are assumed to be measured in meters.  This must not "
        "be 0.0 or negative.";
    ctxParams.def_readwrite("units_per_meter", &ContextParams::unitsPerMeter, docString);
    docString =
        "The global Doppler scale value for this context.  This is applied to all calculated Doppler "
        "factors to enhance or diminish the effect of the Doppler factor.  A value of 1.0 will leave "
        "the calculated Doppler levels unmodified.  A value lower than 1.0 will have the result of "
        "diminishing the Doppler effect.  A value higher than 1.0 will have the effect of enhancing "
        "the Doppler effect.  This is useful for handling global time warping effects.  This parameter "
        "is a unitless scaling factor.  This defaults to 1.0.";
    ctxParams.def_readwrite("doppler_scale", &ContextParams::dopplerScale, docString);
    docString =
        "The global Doppler limit value for this context.  This will cap the calculated Doppler factor "
        "at the high end.  This is to avoid excessive aliasing effects for very fast moving emitters or "
        "listener.  When the relative velocity between the listener and an emitter is nearing the speed "
        "of sound, the calculated Doppler factor can approach ~11 million.  Accurately simulating this "
        "would require a very large scale anti-aliasing or filtering pass on all resampling operations "
        "on the emitter.  That is unfortunately not possible in general.  Clamping the Doppler factor "
        "to something relatively small like 16 will still result in the effect being heard but will "
        "reduce the resampling artifacts related to high frequency ratios.  A Doppler factor of 16 "
        "represents a relative velocity of ~94% the speed of sound so there shouldn't be too much of "
        "a loss in the frequency change simulation.  This defaults to 16.  This should not be negative "
        "or zero.";
    ctxParams.def_readwrite("doppler_limit", &ContextParams::dopplerLimit, docString);
    docString =
        "The effective volume level at which a voice will become virtual.  A virtual voice will not "
        "decode any data and will perform only minimal update tasks when needed.  This is expressed as "
        "a linear volume value from 0.0 (silence) to 1.0 (full volume).  The default volume is 0.0.";
    ctxParams.def_readwrite("virtualization_threshold", &ContextParams::virtualizationThreshold, docString);
    docString =
        "The global frequency ratio to apply to all active spatial voices.  This should only be used "
        "to handle time dilation effects on the voices, not to deal with pitch changes (ie: record a "
        "sound at a high frequency to save on storage space and load time, but then always play it back "
        "at a reduced pitch).  If this is used for pitch changes, it will interfere with distance delay "
        "calculations and possibly lead to other undesirable behavior.  This will not affect any "
        "non-spatial voices.  This defaults to 1.0.";
    ctxParams.def_readwrite("spatial_frequency_ratio", &ContextParams::spatialFrequencyRatio, docString);
    docString =
        "The global frequency ratio to apply to all active non-spatial voices.  This can be used to "
        "perform a pitch change (and as a result play time change) on all non-spatial voices, or it "
        "can be used to simulate a time dilation effect on all non-spatial voices.  This will not "
        "affect any spatial voices.  This defaults to 1.0.";
    ctxParams.def_readwrite("non_spatial_frequency_ratio", &ContextParams::nonSpatialFrequencyRatio, docString);
    docString =
        "The global master volume for this context.  This will only affect the volume level of the "
        "final mixed output signal.  It will not directly affect the relative volumes of each voice "
        "being played.  No individual voice will be able to produce a signal louder than this volume "
        "level.  This is set to 0.0 to silence all output.  This defaults to 1.0 (ie: full volume).  "
        "This should not be set beyond 1.0.";
    ctxParams.def_readwrite("master_volume", &ContextParams::masterVolume, docString);
    docString =
        "The relative volume of all spatial voices.  This will be the initial volume level of any new "
        "spatial voice.  The volume specified in that voice's parameters will be multiplied by this "
        "volume.  This does not affect the volume level of non-spatial voices.  This is set to 0.0 to "
        "silence all spatial voices.  This defaults to 1.0 (ie: full volume).  This should not be set "
        "beyond 1.0.  This volume is independent of the `master_volume` value but will effectively be "
        "multiplied by it for the final output.";
    ctxParams.def_readwrite("spatial_volume", &ContextParams::spatialVolume, docString);
    docString =
        "The relative volume of all non-spatial voices.  This will be the initial volume level of any "
        "new non-spatial voice.  The volume specified in that voice's parameters will be multiplied by "
        "this volume.  This does not affect the volume level of spatial voices.  This is set to 0.0 to "
        "silence all non-spatial voices.  This defaults to 1.0 (ie: full volume).  This should not be "
        "set beyond 1.0.  This volume is independent of the `master_volume` value but will effectively "
        "be multiplied by it for the final output.";
    ctxParams.def_readwrite("non_spatial_volume", &ContextParams::nonSpatialVolume, docString);
    docString = R"(Attributes of the listener.  This is valid when the `CONTEXT_PARAM_LISTENER` flag is used.
                   Only the values that have their corresponding `ENTITY_FLAG_*` flags set will be updated on a
                   set operation.  Any values that do not have their corresponding flag set will just be ignored
                   and the previous value will remain current.  This can be used to (for example) only update
                   the position for the listener but leave its orientation and velocity unchanged.  The flags
                   would also indicate whether the orientation vectors need to be normalized or made perpendicular
                   before continuing.  Fixing up these orientation vectors should only be left up to this call if
                   it is well known that the vectors are not already correct.

                   It is the caller's responsibility to decide on the listener's appropriate position and
                   orientation for any given situation.  For example, if the listener is represented by a third
                   person character, it would make the most sense to set the position to the character's head
                   position, but to keep the orientation relative to the camera's forward and up vectors
                   (possibly have the camera's forward vector projected onto the character's forward vector).
                   If the character's orientation were used instead, the audio may jump from one speaker to
                   another as the character rotates relative to the camera.)";
    ctxParams.def_readwrite("listener", &ContextParams::listener, docString);
    docString =
        "Defines the default playback mode flags for the context.  These will provide 'default' "
        "behavior for new voices.  Any new voice that uses the `PLAYBACK_MODE_DEFAULT_*` flags in "
        "its voice parameters block will inherit the default playback mode behavior from this value.  "
        "Note that only specific playback modes are supported in these defaults. This also provides a "
        "means to either 'force on' or 'force off' certain features for each voice.  This value is a "
        "collection of zero or more of the `PLAYBACK_MODE_DEFAULT_*` flags, and flags that have been "
        "returned from either `get_force_off_playback_mode_flags()` or `get_force_on_playback_mode_flags()`.  "
        "This may not include any of the other `PLAYBACK_MODE_*` flags that are not part of the "
        "`PLAYBACK_MODE_DEFAULT_*` set.  If the other playback mode flags are used, the results will "
        "be undefined.  This defaults to 0.";
    ctxParams.def_readwrite("default_playback_mode", &ContextParams::defaultPlaybackMode, docString);
    docString =
        "Flags to control the behavior of the context.  This is zero or more of the `CONTEXT_PARAM_*` "
        "flags.  This defaults to 0.";
    ctxParams.def_readwrite("flags", &ContextParams::flags, docString);
    /** @} */


    /** ContextParams2 struct binding definition.
     *  @{
     */
    py::class_<ContextParams2> ctxParams2(m, "ContextParams2");
    ctxParams2.doc() = R"(
        Extended context parameters block.  This is used to set and retrieve
        extended context parameters and their current values.  This object
        must be attached to the 'ContextParams.ext' value and the
        'ContextParams.flags' value must have one or more flags related
        to the extended parameters set for them to be modified or retrieved.
    )";
    ctxParams2.def(py::init<>());
    /** @} */


    /** LoopPointDesc struct binding definition.
     *  @{
     */
    py::class_<LoopPointDesc> loopPointDesc(m, "LoopPointDesc");
    loopPointDesc.doc() = R"(
        Descriptor of a loop point to set on a voice.  This may be specified
        to change the current loop point on a voice with set_Loop_Point().
    )";
    loopPointDesc.def(py::init<>());
    /** @} */


    /** DspValuePair struct binding definition.
     *  @{
     */
    py::class_<DspValuePair> dspValuePair(m, "DspValuePair");
    dspValuePair.doc() =
        "Specifies a pair of values that define a DSP value range to be interpolated between "
        "based on an emitter-listener angle that is between a cone's inner and outer angles.  "
        "For angles that are smaller than the cone's inner angle, the 'inner' DSP value will "
        "always be used.  Similarly, for angles that are larger than the cone's outer angle, "
        "the 'outer' DSP value will always be used.  Interpolation will only occur when the "
        "emitter-listener angle is between the cone's inner and outer angles.  No specific "
        "meaning or value range is attached to the 'inner' and 'outer' DSP values.  These "
        "come from the specific purpose that this object is used for.";
    dspValuePair.def(py::init<>());
    docString =
        "The DSP value to be used for angles less than the cone's inner angle and as one of the "
        "interpolation endpoints for angles between the cone's inner and outer angles.";
    dspValuePair.def_readwrite("inner", &DspValuePair::inner, docString);
    docString =
        "The DSP value to be used for angles greater than the cone's outer angle and as one of the "
        "interpolation endpoints for angles between the cone's inner and outer angles.";
    dspValuePair.def_readwrite("outer", &DspValuePair::outer, docString);
    /** @} */


    /** EntityCone struct binding definition.
     *  @{
     */
    py::class_<EntityCone> cone(m, "EntityCone");
    cone.doc() = R"(Defines a sound cone relative to an entity's front vector.  It is defined by two angles -
                    the inner and outer angles.  When the angle between an emitter and the listener (relative
                    to the entity's front vector) is smaller than the inner angle, the resulting DSP value
                    will be the 'inner' value.  When the emitter-listener angle is larger than the outer angle,
                    the resulting DSP value will be the 'outer' value.  For emitter-listener angles that are
                    between the inner and outer angles, the DSP value will be interpolated between the inner
                    and outer angles.  If a cone is valid for an entity, the `ENTITY_FLAG_CONE` flag should
                    be set in `EntityAttributes.flags`.

                    Note that a cone's effect on the spatial volume of a sound is purely related to the angle
                    between the emitter and listener.  Any distance attenuation is handled separately.)";
    cone.def(py::init<>());
    docString =
        "The inside angle of the entity's sound cone in radians.  This describes the angle around "
        "the entity's forward vector within which the entity's DSP values will always use their "
        "'inner' values.  This angle will extend half way in all directions around the forward "
        "vector.  For example, a 30 degree (as converted to radians to store here) inside angle "
        "will extend 15 degrees in all directions around the forward vector.  Set this to "
        "`CONE_ANGLE_OMNI_DIRECTIONAL` to define an omni-directional entity.  This must be greater "
        "than or equal to 0 and less than or equal to `outside_angle`.";
    cone.def_readwrite("inside_angle", &EntityCone::insideAngle, docString);
    docString =
        "The outside angle of the entity's sound cone in radians.  This describes the angle around "
        "the entity's forward vector up to which the volume will be interpolated.  When the "
        "emitter-listener angle is larger than this angle, the 'outer' DSP values will always be "
        "used.  This angle will extend half way in all directions around the forward vector.  For "
        "example, a 30 degree (as converted to radians to store here) inside angle will extend 15 "
        "degrees in all directions around the forward vector.  Set this to `CONE_ANGLE_OMNI_DIRECTIONAL` "
        "to define an omni-directional entity.  This must be greater than or equal to `inside_angle`.";
    cone.def_readwrite("outside_angle", &EntityCone::outsideAngle, docString);
    docString =
        "The volumes to use for emitter-listener lines that are inside and outside the entity's cone "
        "angles.  These will be used as the endpoint values to interpolate to for angles between the "
        "inner and outer angles, and for the values for all angles outside the cone's inner and outer "
        "angles.  These should be in the range 0.0 (silence) to 1.0 (full volume).";
    cone.def_readwrite("volume", &EntityCone::volume, docString);
    docString =
        "The low pass filter parameter values to use for emitter-listener lines that are inside and "
        "outside the entity's cone angles.  These will be used as the endpoint values to interpolate "
        "to for angles between the inner and outer angles, and for the values for all angles outside "
        "the cone's inner and outer angles.  There is no specific range for these values other than "
        "what is commonly accepted for low pass filter parameters.  This multiplies by member `direct` "
        "of `VoiceParams.occlusion`, if that is set to anything other than 1.0.  Setting this to a "
        "value outside of [0.0, 1.0] will result in an undefined low pass filter value being used.";
    cone.def_readwrite("low_pass_filter", &EntityCone::lowPassFilter, docString);
    docString =
        "The reverb mix level values to use for emitter-listener lines that are inside and outside "
        "the entity's cone angles.  These will be used as the endpoint values to interpolate to for "
        "angles between the inner and outer angles, and for the values for all angles outside the "
        "cone's inner and outer angles.  This should be in the range 0.0 (no reverb) to 1.0 (full "
        "reverb).";
    cone.def_readwrite("reverb", &EntityCone::reverb, docString);
    /** @} */


    /** EntityAttributes struct binding definition.
     *  @{
     */
    py::class_<EntityAttributes> entityAttributes(m, "EntityAttributes");
    entityAttributes.doc() =
        "Base spatial attributes of the entity.  This includes its position, orientation, "
        "and velocity and an optional cone.";
    entityAttributes.def(py::init<>());
    docString =
        "A set of flags that indicate which of members of this struct are valid.  This may be "
        "`ENTITY_FLAG_ALL` to indicate that all members contain valid data.";
    entityAttributes.def_readwrite("flags", &EntityAttributes::flags, docString);
    docString =
        "The current position of the listener in world units.  This should only be expressed in meters "
        "if the world units scale is set to 1.0 for this context.  This value is ignored if the "
        "`ENTITY_FLAG_POSITION` flag is not set in `flags`.";
    entityAttributes.def_readwrite("position", &EntityAttributes::position, docString);
    docString =
        "The current velocity of the listener in world units per second.  This should only be expressed "
        "in meters per second if the world units scale is set to 1.0 with for the context.  The magnitude "
        "of this vector will be taken as the listener's current speed and the vector's direction will "
        "indicate the listener's current direction.  This vector should not be normalized unless the "
        "listener's speed is actually 1.0 units per second.  This may be a zero vector if the listener "
        "is not moving.  This value is ignored if the `ENTITY_FLAG_VELOCITY` flag is not set in `flags`.  "
        "This vector will not be modified in any way before use.";
    entityAttributes.def_readwrite("velocity", &EntityAttributes::velocity, docString);
    docString =
        "A vector indicating the direction the listener is currently facing.  This does not need to be "
        "normalized, but should be for simplicity.  If the `ENTITY_FLAG_NORMALIZE` flag is set in `flags`, "
        "this vector will be normalized internally before being used.  This vector should be perpendicular "
        "to the `up` vector unless the `ENTITY_FLAG_MAKE_PERP` flag is set in `flags`.  This must not be a "
        "zero vector unless the `ENTITY_FLAG_FORWARD` flag is not set in `flags`.";
    entityAttributes.def_readwrite("forward", &EntityAttributes::forward, docString);
    docString =
        "A vector indicating the upward direction for the listener.  This does not need to be normalized, "
        "but should be for simplicity.  If the `ENTITY_FLAG_NORMALIZE` flag is set in `flags`, this vector "
        "will be normalized internally before being used.  This vector should be perpendicular to the "
        "`forward` vector unless the `ENTITY_FLAG_MAKE_PERP` flag is set in `flags`.  This must not be a "
        "zero vector unless the `ENTITY_FLAG_UP` flag is not set in `flags`.";
    entityAttributes.def_readwrite("up", &EntityAttributes::up, docString);
    docString =
        "Defines an optional sound cone for an entity.  The cone is a segment of a sphere around the "
        "entity's position opening up toward its front vector.  The cone is defined by an inner and outer "
        "angle, and several DSP values to be interpolated between for those two endpoint angles.  This cone "
        "is valid if the @ref `ENTITY_FLAG_CONE` flag is set in `flags`.";
    entityAttributes.def_readwrite("cone", &EntityAttributes::cone, docString);
    /** @} */


    /** RolloffDesc struct binding definition.
     *  @{
     */
    py::class_<RolloffDesc> rolloffDesc(m, "RolloffDesc");
    rolloffDesc.doc() = R"(Descriptor of the rolloff mode and range.  The C++ API allows rolloff curves to be set
                           through this struct, but in python you need to use voice.set_rolloff_curve() to do this
                           instead.)";
    rolloffDesc.def(py::init<>());
    docString =
        "The default type of rolloff calculation to use for all DSP values that are not overridden by a "
        "custom curve.  This defaults to `RolloffType.LINEAR`.";
    rolloffDesc.def_readwrite("type", &RolloffDesc::type, docString);
    docString =
        "The near distance range for the sound.  This is specified in arbitrary world units.  When a custom "
        "curve is used, this near distance will map to a distance of 0.0 on the curve.  This must be less "
        "than the `far_distance` distance.  The near distance is the closest distance that the emitter's "
        "attributes start to rolloff at.  At distances closer than this value, the calculated DSP values "
        "will always be the same as if they were at the near distance.  This defaults to 0.0.";
    rolloffDesc.def_readwrite("near_distance", &RolloffDesc::nearDistance, docString);
    docString =
        "The far distance range for the sound.  This is specified in arbitrary world units.  When a custom "
        "curve is used, this far distance will map to a distance of 1.0 on the curve.  This must be greater "
        "than the `near_distance` distance.  The far distance is the furthest distance that the emitters "
        "attributes will rolloff at.  At distances further than this value, the calculated DSP values will "
        "always be the same as if they were at the far distance (usually silence).  Emitters further than "
        "this distance will often become inactive in the scene since they cannot be heard any more.  This "
        "defaults to 10000.0.";
    rolloffDesc.def_readwrite("far_distance", &RolloffDesc::farDistance, docString);
    /** @} */


    /** EmitterAttributes struct binding definition.
     *  @{
     */
    py::class_<EmitterAttributes> emitterAttributes(m, "EmitterAttributes");
    emitterAttributes.doc() = "Spatial attributes of an emitter entity.";
    docString =
        "A set of flags that indicate which of members of this struct are valid.  This may be "
        "`ENTITY_FLAG_ALL` to indicate that all members contain valid data.";
    emitterAttributes.def(py::init<>());
    emitterAttributes.def_readwrite("flags", &EmitterAttributes::flags, docString);
    docString =
        "The current position of the listener in world units.  This should only be expressed in meters "
        "if the world units scale is set to 1.0 for this context.  This value is ignored if the "
        "`ENTITY_FLAG_POSITION` flag is not set in `flags`.";
    emitterAttributes.def_readwrite("position", &EmitterAttributes::position, docString);
    docString =
        "The current velocity of the listener in world units per second.  This should only be expressed "
        "in meters per second if the world units scale is set to 1.0 with for the context.  The magnitude "
        "of this vector will be taken as the listener's current speed and the vector's direction will "
        "indicate the listener's current direction.  This vector should not be normalized unless the "
        "listener's speed is actually 1.0 units per second.  This may be a zero vector if the listener "
        "is not moving.  This value is ignored if the `ENTITY_FLAG_VELOCITY` flag is not set in `flags`.  "
        "This vector will not be modified in any way before use.";
    emitterAttributes.def_readwrite("velocity", &EmitterAttributes::velocity, docString);
    docString =
        "A vector indicating the direction the listener is currently facing.  This does not need to be "
        "normalized, but should be for simplicity.  If the `ENTITY_FLAG_NORMALIZE` flag is set in `flags`, "
        "this vector will be normalized internally before being used.  This vector should be perpendicular "
        "to the `up` vector unless the `ENTITY_FLAG_MAKE_PERP` flag is set in `flags`.  This must not be a "
        "zero vector unless the `ENTITY_FLAG_FORWARD` flag is not set in `flags`.";
    emitterAttributes.def_readwrite("forward", &EmitterAttributes::forward, docString);
    docString =
        "A vector indicating the upward direction for the listener.  This does not need to be normalized, "
        "but should be for simplicity.  If the `ENTITY_FLAG_NORMALIZE` flag is set in `flags`, this vector "
        "will be normalized internally before being used.  This vector should be perpendicular to the "
        "`forward` vector unless the `ENTITY_FLAG_MAKE_PERP` flag is set in `flags`.  This must not be a "
        "zero vector unless the `ENTITY_FLAG_UP` flag is not set in `flags`.";
    emitterAttributes.def_readwrite("up", &EmitterAttributes::up, docString);
    docString =
        "Defines an optional sound cone for an entity.  The cone is a segment of a sphere around the "
        "entity's position opening up toward its front vector.  The cone is defined by an inner and outer "
        "angle, and several DSP values to be interpolated between for those two endpoint angles.  This cone "
        "is valid if the @ref `ENTITY_FLAG_CONE` flag is set in `flags`.";
    emitterAttributes.def_readwrite("cone", &EmitterAttributes::cone, docString);
    docString =
        "A descriptor of the rolloff parameters for this emitter.  This is valid and accessed only if the "
        "`ENTITY_FLAG_ROLLOFF` flag is set in `EmitterAttributes.flags`.  The curves (if any) in this "
        "descriptor must remain valid for the entire time a voice is playing the sound represented by this "
        "emitter.";
    emitterAttributes.def_readwrite("rolloff", &EmitterAttributes::rolloff, docString);
    /** @} */


    /** VoiceParams::VoiceParamBalance struct binding definition.
     *  @{
     */
    py::class_<VoiceParams::VoiceParamBalance> voiceParamBalance(m, "VoiceParamBalance");
    voiceParamBalance.doc() =
        "Non-spatial sound positioning parameters.  These provide pan and fade values for the "
        "voice to give the impression that the sound is located closer to one of the quadrants "
        "of the acoustic space versus the others.  These values are ignored for spatial sounds.";
    docString = R"(Sets the non-spatial panning value for a voice.  This value is valid when the `VOICE_PARAM_BALANCE`
                   flag is used.  This is 0.0 to have the sound 'centered' in all speakers.  This is -1.0 to have the
                   sound balanced to the left side.  This is 1.0 to have the sound balanced to the right side.  The way
                   the sound is balanced depends on the number of channels.  For example, a mono sound will be balanced
                   between the left and right sides according to the panning value, but a stereo sound will just have the
                   left or right channels' volumes turned down according to the panning value.  This value is ignored
                   for spatial sounds.  The default value is 0.0.

                   Note that panning on non-spatial sounds should only be used for mono or stereo sounds.  When it is
                   applied to sounds with more channels, the results are often undefined or may sound odd.)";
    voiceParamBalance.def(py::init<>());
    voiceParamBalance.def_readwrite("pan", &VoiceParams::VoiceParamBalance::pan, docString);
    docString = R"(Sets the non-spatial fade value for a voice.  This value is valid when the `VOICE_PARAM_BALANCE`
                   flag is used.  This is 0.0 to have the sound 'centered' in all speakers.  This is -1.0 to have
                   the sound balanced to the back side.  This is 1.0 to have the sound balanced to the front side.
                   The way the sound is balanced depends on the number of channels.  For example, a mono sound will
                   be balanced between the front and back speakers according to the fade value, but a 5.1 sound
                   will just have the front or back channels' volumes turned down according to the fade value.
                   This value is ignored for spatial sounds.  The default value is 0.0.

                   Note that using fade on non-spatial sounds should only be used for mono or stereo sounds.  When
                   it is applied to sounds with more channels, the results are often undefined or may sound odd.)";
    voiceParamBalance.def_readwrite("fade", &VoiceParams::VoiceParamBalance::fade, docString);
    /** @} */


    /** VoiceParams::VoiceParamOcclusion struct binding definition.
     *  @{
     */
    py::class_<VoiceParams::VoiceParamOcclusion> voiceParamOcclusion(m, "VoiceParamOcclusion");
    voiceParamOcclusion.doc() =
        "The occlusion factors for a voice.  This is valid when the "
        "`VOICE_PARAM_OCCLUSION_FACTOR` flag is used.  These values control automatic low "
        "pass filters that get applied to the spatial sounds to simulate object occlusion "
        "between the emitter and listener positions.";
    docString =
        "The occlusion factor for the direct path of the sound.  This is the path directly from the "
        "emitter to the listener.  This factor describes how occluded the sound's path actually is.  "
        "A value of 1.0 means that the sound is fully occluded by an object between the voice and the "
        "listener.  A value of 0.0 means that the sound is not occluded by any object at all.  This "
        "defaults to 0.0.  This factor multiplies by `EntityCone.low_pass_filter`, if a cone with a "
        "non 1.0 `low_pass_filter` value is specified.  Setting this to a value outside of [0.0, 1.0] "
        "will result in an undefined low pass filter value being used.";
    voiceParamOcclusion.def(py::init<>());
    voiceParamOcclusion.def_readwrite("direct", &VoiceParams::VoiceParamOcclusion::direct, docString);
    docString =
        "The occlusion factor for the reverb path of the sound.  This is the path taken for  sounds "
        "reflecting back to the listener after hitting a wall or other object.  A value of 1.0 means "
        "that the sound is fully occluded by an object between the listener and the object that the "
        "sound reflected off of.  A value of 0.0 means that the sound is not occluded by any object "
        "at all.  This defaults to 1.0.";
    voiceParamOcclusion.def_readwrite("reverb", &VoiceParams::VoiceParamOcclusion::reverb, docString);
    /** @} */


    /** VoiceParams struct binding definition.
     *  @{
     */
    py::class_<VoiceParams> voiceParams(m, "VoiceParams");
    voiceParams.doc() = R"(Voice parameters block.  This can potentially contain all of a voice's
                           parameters and their current values.  This is used to both set and
                           retrieve one or more of a voice's parameters in a single call.  The
                           VOICE_PARAM_* flags that are passed to set_voice_parameters() or
                           get_voice_parameters() determine which values in this block are
                           guaranteed to be valid.
                           The matrix parameter isn't available from this struct due to limitations
                           in python; use voice.set_matrix() instead.)";
    voiceParams.def(py::init<>());
    docString =
        "Flags to indicate how a sound is to be played back.  This value is valid only when the "
        "`VOICE_PARAM_PLAYBACK_MODE`, `VOICE_PARAM_MUTE`, or `VOICE_PARAM_PAUSE` flags are used.  "
        "This controls whether the sound is played as a spatial or non-spatial sound and how the "
        "emitter's attributes will be interpreted (ie: either world coordinates or listener relative).";
    voiceParams.def_readwrite("playback_mode", &VoiceParams::playbackMode, docString);
    docString =
        "The volume level for the voice.  This is valid when the `VOICE_PARAM_VOLUME` flag is used.  "
        "This should be 0.0 for silence or 1.0 for normal volume.  A negative value may be used to "
        "invert the signal.  A value greater than 1.0 will amplify the signal.  The volume level can "
        "be interpreted as a linear scale where a value of 0.5 is half volume and 2.0 is double volume.  "
        "Any volume values in decibels must first be converted to a linear volume scale before setting "
        "this value.  The default value is 1.0.";
    voiceParams.def_readwrite("volume", &VoiceParams::volume, docString);
    docString =
        "Non-spatial sound positioning parameters.  These provide pan and fade values for the voice to "
        "give the impression that the sound is located closer to one of the quadrants of the acoustic "
        "space versus the others.  These values are ignored for spatial sounds.";
    voiceParams.def_readwrite("balance", &VoiceParams::balance, docString);
    docString = R"(The frequency ratio for a voice.  This is valid when the `VOICE_PARAM_FREQUENCY_RATIO`
                   flag is used.  This will be 1.0 to play back a sound at its normal rate, a value less than
                   1.0 to lower the pitch and play it back more slowly, and a value higher than 1.0 to increase
                   the pitch and play it back faster.  For example, a pitch scale of 0.5 will play back at half
                   the pitch (ie: lower frequency, takes twice the time to play versus normal), and a pitch
                   scale of 2.0 will play back at double the pitch (ie: higher frequency, takes half the time
                   to play versus normal).  The default value is 1.0.

                   On some platforms, the frequency ratio may be silently clamped to an acceptable range
                   internally.  For example, a value of 0.0 is not allowed.  This will be clamped to the
                   minimum supported value instead.

                   Note that the even though the frequency ratio *can* be set to any value in the range from
                   1/1024 to 1024, this very large range should only be used in cases where it is well known
                   that the particular sound being operated on will still sound valid after the change.  In
                   the real world, some of these extreme frequency ratios may make sense, but in the digital
                   world, extreme frequency ratios can result in audio corruption or even silence.  This
                   happens because the new frequency falls outside of the range that is faithfully
                   representable by either the audio device or sound data itself.  For example, a 4KHz tone
                   being played at a frequency ratio larger than 6.0 will be above the maximum representable
                   frequency for a 48KHz device or sound file.  This case will result in a form of corruption
                   known as aliasing, where the frequency components above the maximum representable
                   frequency will become audio artifacts.  Similarly, an 800Hz tone being played at a
                   frequency ratio smaller than 1/40 will be inaudible because it falls below the frequency
                   range of the human ear.

                   In general, most use cases will find that the frequency ratio range of [0.1, 10] is more
                   than sufficient for their needs.  Further, for many cases, the range from [0.2, 4] would
                   suffice.  Care should be taken to appropriately cap the used range for this value.)";
    voiceParams.def_readwrite("frequency_ratio", &VoiceParams::frequencyRatio, docString);
    docString =
        "The playback priority of this voice.  This is valid when the `VOICE_PARAM_PRIORITY` flag "
        "is used.  This is an arbitrary value whose scale is defined by the host app.  A value of 0 "
        "is the default priority.  Negative values indicate lower priorities and positive values "
        "indicate higher priorities.  This priority value helps to determine which voices are the "
        "most important to be audible at any given time.  When all buses are busy, this value will "
        "be used to compare against other playing voices to see if it should steal a bus from another "
        "lower priority sound or if it can wait until another bus finishes first.  Higher priority "
        "sounds will be ensured a bus to play on over lower priority sounds.  If multiple sounds "
        "have the same priority levels, the louder sound(s) will take priority.  When a higher "
        "priority sound is queued, it will try to steal a bus from the quietest sound with lower or "
        "equal priority.";
    voiceParams.def_readwrite("priority", &VoiceParams::priority, docString);
    docString = R"(The spatial mix level.  This is valid when `VOICE_PARAM_SPATIAL_MIX_LEVEL` flag is used.
                   This controls the mix between the results of a voice's spatial sound calculations and its
                   non-spatial calculations.  When this is set to 1.0, only the spatial sound calculations
                   will affect the voice's playback.  This is the default when state.  When set to 0.0, only
                   the non-spatial sound calculations will affect the voice's playback.  When set to a value
                   between 0.0 and 1.0, the results of the spatial and non-spatial sound calculations will
                   be mixed with the weighting according to this value.  This value will be ignored if
                   `PLAYBACK_MODE_SPATIAL` is not set.  The default value is 1.0.  Values above 1.0 will be
                   treated as 1.0. Values below 0.0 will be treated as 0.0.

                   `PLAYBACK_MODE_SPATIAL_MIX_LEVEL_MATRIX` affects the non-spatial mixing behavior of this
                   parameter for multi-channel voices. By default, a multi-channel spatial voice's non-spatial
                   component will treat each channel as a separate mono voice. With the
                   `PLAYBACK_MODE_SPATIAL_MIX_LEVEL_MATRIX` flag set, the non-spatial component will be set
                   with the specified output matrix or the default output matrix.)";
    voiceParams.def_readwrite("spatial_mix_level", &VoiceParams::spatialMixLevel, docString);
    docString =
        "The Doppler scale value.  This is valid when the @ref fVoiceParamDopplerScale flag is used.  "
        "This allows the result of internal Doppler calculations to be scaled to emulate a time "
        "warping effect.  This should be near 0.0 to greatly reduce the effect of the Doppler "
        "calculations, and up to 5.0 to exaggerate the Doppler effect.  A value of 1.0 will leave "
        "the calculated Doppler factors unmodified.  The default value is 1.0.";
    voiceParams.def_readwrite("doppler_scale", &VoiceParams::dopplerScale, docString);
    docString =
        "The occlusion factors for a voice.  This is valid when the `VOICE_PARAM_OCCLUSION_FACTOR` "
        "flag is used.  These values control automatic low pass filters that get applied to the "
        "spatial sounds to simulate object occlusion between the emitter and listener positions.";
    voiceParams.def_readwrite("occlusion", &VoiceParams::occlusion, docString);
    docString =
        "The attributes of the emitter related for this voice.  This is only valid when the "
        "`VOICE_PARAM_EMITTER` flag is used.  This includes the emitter's position, orientation, "
        "velocity, cone, and rolloff curves.  The default values for these attributes are noted "
        "in the `EmitterAttributes` object.  This will be ignored for non-spatial sounds.";
    voiceParams.def_readwrite("emitter", &VoiceParams::emitter, docString);
    /** @} */


    /** OutputDesc struct binding definition.
     *  @{
     */
    py::class_<OutputDesc> outputDesc(m, "OutputDesc");
    outputDesc.doc() =
        "Descriptor of the audio output target to use for an audio context.  This may be "
        "specified both when creating an audio context and when calling set_output().  An "
        "output may only consist of a real audio device from the Python side";
    outputDesc.def(py::init<>());
    docString =
        "Flags to indicate which output target is to be used.  Currently only a single output "
        "target may be specified.  This must be one of the `OUTPUT_FLAG_*` flags.  Future versions "
        "may allow for multiple simultaneous outputs.  If this is 0, the default output device "
        "will be selected.  If more than zero flags are specified, the audio device index will "
        "specify which device to use.";
    outputDesc.def_readwrite("flags", &OutputDesc::flags, docString);
    docString =
        "The index of the device to open.  This must be greater than or equal to 0 and less than "
        "the most recent return value of `get_device_count()`.  Set this to 0 to choose the system's "
        "default playback device.  This defaults to 0.  This value is always ignored if the "
        "`OUTPUT_FLAG_DEVICE` flag is not used and the `flags` member is not 0.";
    outputDesc.def_readwrite("device_index", &OutputDesc::deviceIndex, docString);
    docString =
        "The output speaker mode to set.  This is one of the `SPEAKER_MODE_*` names or a combination "
        "of the `SPEAKER_FLAG_*` speaker flags.  This will determine the channel layout for the final "
        "output of the audio engine.  This channel layout will be mapped to the selected device's "
        "speaker mode before sending the final output to the device.  This may be set to "
        "`SPEAKER_MODE_DEFAULT` to cause the engine's output to match the output of the device that is "
        "eventually opened.  This defaults to `SPEAKER_MODE_DEFAULT`.";
    outputDesc.def_readwrite("speaker_mode", &OutputDesc::speakerMode, docString);
    docString = R"(The frame rate in Hertz to run the processing engine at.  This should be 0 for any output
                   that targets a real hardware device (ie: the `OUTPUT_FLAG_DEVICE` is used in `flags`
                   or `flags` is 0),  It is possible to specify a non-zero value here when a hardware device
                   is targeted, but that may lead to unexpected results depending on the value given.  For
                   example, this could be set to 1000Hz, but the device could run at 48000Hz.  This would
                   process the audio data properly, but it would sound awful since the processing data rate
                   is so low.  Conversely, if a frame rate of 200000Hz is specified but the device is running
                   at 48000Hz, a lot of CPU processing time will be wasted.

                   When an output is targeting only a streamer table, this should be set to the frame rate
                   to process audio at.  If this is 0, a frame rate of 48000Hz will be used.  This value
                   should generally be a common audio processing rate such as 44100Hz, 48000Hz, etc.  Other
                   frame rates can be used, but the results may be unexpected if a frame cannot be perfectly
                   aligned to the cycle period.)";
    outputDesc.def_readwrite("frame_rate", &OutputDesc::frameRate, docString);
    /** @} */


    /** PlaybackContextDesc struct binding definition.
     *  @{
     */
    py::class_<PlaybackContextDesc> playbackContextDesc(m, "PlaybackContextDesc");
    playbackContextDesc.doc() =
        "Descriptor used to indicate the options passed to the createContext() function.  "
        "This determines the how the context will behave.";
    playbackContextDesc.def(py::init<>());
    docString =
        "Flags to indicate some additional behavior of the context.  This may be a set of zero or more of "
        "the `CONTEXT_FLAG_*` flags.";
    playbackContextDesc.def_readwrite("flags", &PlaybackContextDesc::flags, docString);
    docString = R"(The maximum number of data buses to process simultaneously.  This is equivalent to the
                   maximum number of potentially audible sounds that could possibly affect the output on the
                   speakers.  If more voices than this are active, the quietest or furthest voice will be
                   deactivated.  The default value for this is 64.  Set this to 0 to use the default for
                   the platform.

                   For a baking context, this should be set to a value that is large enough to guarantee
                   that no voices will become virtualized.  If a voice becomes virtualized in a baking
                   context and it is set to simulate that voice's current position, the resulting position
                   when it becomes a real voice again is unlikely to match the expected position.  This is
                   because there is no fixed time base to simulate the voice on.  The voice will be simulated
                   as if it were playing in real time.)";
    playbackContextDesc.def_readwrite("max_buses", &PlaybackContextDesc::maxBuses, docString);
    docString =
        "Descriptor for the output to choose for the new audio context.  This must specify at least "
        "one output target.";
    playbackContextDesc.def_readwrite("output", &PlaybackContextDesc::output, docString);
    docString =
        "A name to use for any audio device connection that requires one.  This can be set to `None` to use "
        "a generic default name if necessary.  This is useful in situations where a platform, such as Pulse "
        "Audio, will display a name to the user for each individual audio connection.";
    playbackContextDesc.def_readwrite("output_display_name", &PlaybackContextDesc::outputDisplayName, docString);
    /** @} */
}

inline void definePythonModuleHelperFunctions(py::module& m)
{
    const char* docString;


    docString = R"(retrieves a set of default playback mode flags that will behave as 'force off' behavior.

                   Args:
                        flags:  The set of `PLAYBACK_MODE_DEFAULT_*` flags to use as 'force off' flags.

                   Returns:
                        The corresponding 'force off' flags for the input flags.  These are suitable for setting
                        in the context parameters' default playback mode value.  These should not be used in the
                        voice parameter block's playback mode value - this will lead to unexpected behavior.)";
    m.def("get_force_off_playback_mode_flags", &getForceOffPlaybackModeFlags, py::arg("flags"), docString);

    docString = R"(Retrieves a set of default playback mode flags that will behave as 'force on' behavior.

                   Args:
                        flags:  The set of `PLAYBACK_MODE_DEFAULT_*` flags to use as 'force on' flags.

                   Returns:
                        The corresponding 'force on' flags for the input flags.  These are suitable for setting
                        in the context parameters' default playback mode value.  These should not be used in the
                        voice parameter block's playback mode value - this will lead to unexpected behavior.)";
    m.def("get_force_on_playback_mode_flags", &getForceOnPlaybackModeFlags, py::arg("flags"), docString);
}

inline void definePythonModuleContextObject(py::module& m)
{
    const char* docString;


    py::class_<PythonContext> ctx(m, "Context");
    ctx.doc() = R"(
        The Context object for the audio system.
        Each individual Context represents an instance of the IAudioPlayback
        interface, as well as an individual connection to the system audio
        mixer/device. Only a small number of these can be opened for a given
        process.
    )";

    docString = R"(Performs required frequent updates for the audio context.  This performs common update
        tasks.  Updates need to be performed frequently.  This will perform any pending callbacks and will
        ensure that all pending parameter changes have been updated in the engine context.  This should
        still be called periodically even if no object parameter changes occur.

        All non-realtime voice callbacks will be performed during this call.  All device change callbacks
        on the context will also be performed here.  Failing to call this periodically may cause events
        to be lost.

        Returns:
            AudioResult.OK if the update is performed successfully.
            AudioResult.DEVICE_DISCONNECTED or AudioResult.DEVICE_LOST if the currently selected device
            has been removed from the system.
            AudioResult.DEVICE_NOT_OPEN if no device has been opened.
            AudioResult.INVALID_PARAMETER if an invalid context is passed in.
            An AudioResult.* error code if the update fails for any other reason.)";
    ctx.def("update", &PythonContext::update, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(
        Retrieves the current capabilities and settings for a context object.

        This retrieves the current capabilities and settings for a context
        object.  Some of these settings may change depending on whether the
        context has opened an output device or not.

        Args:
            No arguments.

        Returns:
            the context's current capabilities and settings.  This includes the
            speaker mode, speaker positions, maximum bus count, and information
            about the output device that is opened (if any).

    )";
    ctx.def("get_caps", [](PythonContext* self) -> ContextCaps { return *self->getContextCaps(); }, docString,
            py::call_guard<py::gil_scoped_release>());

    docString = R"(
        Change the maximum number of voices that have their output mixed to the audio device.

        Notes:
            * This call needs to stop the audio engine, so this will block for 10-20ms
              if any voices are still playing actively.

            * This should be called infrequently and only in cases where destroying
              the context is not an option.

            * To use this function without introducing audio artifacts, this function can
              only be called after all voices playing on buses have become silent or have
              stopped. The easiest way to ensure this is to set the master volume on the
              context to 0.0.  At least 10ms must elapse between the volume reduction and
              this call to ensure that the changes have taken effect.  If voices are being
              stopped, 20ms must occur between the last stopped voice and this call.

        Args:
            count:  The new number of buses to select.  This will be clamped to 64 if.
                    This cannot be set to 0.

        Returns:
            `True` if the max bus count was successfully changed.
            `False` if any voices are still playing on buses.
            `False` if the operation failed for any other reason (e.g. out of memory).
    )";
    ctx.def("set_bus_count", &PythonContext::setBusCount, docString, py::arg("count"),
            py::call_guard<py::gil_scoped_release>());

    docString = R"(Opens a requested audio output device and begins output.  This sets the index of the
                   audio output device that will be opened and attempts to open it.  An index of 0 will
                   open the system's default audio output device.  Note that the device index value is
                   volatile and could change at any time due to user activity.  It is suggested that the
                   device index be chosen as closely as possible to when the device will be opened.

                   This allows an existing audio context object to switch to using a different audio
                   device for its output after creation without having to destroy and recreate the
                   current state of the context.  Once a new device is selected, it will be available
                   to start processing and outputting audio.  Note that switching audio devices dynamically
                   may cause an audible pop to occur on both the old device and new device depending
                   on the current state of the context.  To avoid this, all active voices could be muted
                   or paused briefly during the device switch, then resumed or un-muted after it completes.

                   Note:
                       If selecting the new device fails, the context will be left without a device to
                       play its output on.  Upon failure, an attempt to open the system's default device
                       may be made by the caller to restore the playback.  Note that even choosing the
                       system default device may fail for various reasons (ie: the speaker mode of the
                       new device cannot be mapped properly, the device is no longer available in the
                       system, etc).  In this case, all audio processing will still continue but the
                       final audio data will just be dropped until a valid output target is connected.

                   Args:
                       context: The context object that will have its device index set.  This is
                                returned from a previous call to `create_context()`.  This must not
                                be `None`.
                       desc:    The descriptor of the output to open.  This may be `None` or omitted
                                to use the default system output device.

                   Returns:
                       `AudioResult.OK` if the requested device is successfully opened.
                       `AudioResult.OUT_OF_RANGE` if the device index is invalid.
                       An `AudioResult.*` error code if the operation fails for any other reason.  See
                       the notes above for more information on failures.)";
    ctx.def("set_output", &PythonContext::setOutput, docString, py::arg("desc") = nullptr,
            py::call_guard<py::gil_scoped_release>());

    docString = R"(
        Sets one or more parameters on a context.

        This sets one or more context parameters in a single call.  Only
        parameters that have their corresponding flag set in paramsToSet will
        be modified.  If a change is to be relative to the context's current
        parameter value, the current value should be retrieved first, modified,
        then set.

        Args:
            paramsToSet: The set of flags to indicate which parameters in the
                         parameter block params are valid and should be set
                         on the context.  This may be zero or more of the
                         CONTEXT_PARAM_* bitflags.  If this is 0, the call will be
                         treated as a no-op.
            params:      The parameter(s) to be set on the context.  The flags
                         indicating which parameters need to be set are given
                         in paramsToSet.  Undefined behavior may occur if
                         a flag is set but its corresponding value(s) have not
                         been properly initialized.  This may not be None.

        Returns:
            No return value.
    )";
    ctx.def("set_parameters", &PythonContext::setContextParameters, docString, py::arg("paramsToSet"),
            py::arg("params"), py::call_guard<py::gil_scoped_release>());

    docString = R"(
        Retrieves one or more parameters for a context.

        This retrieves the current values of one or more of a context's
        parameters.  Only the parameter values listed in paramsToGet flags
        will be guaranteed to be valid upon return.

        Args:
            ParamsToGet: Flags indicating which parameter values need to be retrieved.
                         This should be a combination of the CONTEXT_PARAM_* bitflags.

        Returns:
            The requested parameters in a ContextParams struct. Everything else is default-initialized.
    )";
    ctx.def("get_parameters",
            [](PythonContext* self, ContextParamFlags paramsToGet) -> ContextParams {
                ContextParams tmp = {};
                self->getContextParameters(paramsToGet, &tmp);
                return tmp;
            },
            docString, py::arg("paramsToGet"), py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Schedules a sound to be played on a voice.

        This schedules a sound object to be played on a voice.  The sounds current
        settings (ie: volume, pitch, playback frame rate, pan, etc) will be assigned to
        the voice as 'defaults' before playing.  Further changes can be made to the
        voice's state at a later time without affecting the sound's default settings.

        Once the sound finishes playing, it will be implicitly unassigned from the
        voice.  If the sound or voice have a callback set, a notification will be
        received for the sound having ended.

        If the playback of this sound needs to be stopped, it must be explicitly stopped
        from the returned voice object using stopVoice().  This can be called on a
        single voice or a voice group.

        Args:
             sound: The sound to schedule.
             flags: Flags that alter playback behavior. Must be a combination of PLAY_FLAG_* constants.
             valid_params: Which parameters in the params argument to use.
             params: The starting parameters for the voice. This conditionally used based on valid_params.
             loop_point: A descriptor for how to repeatedly play the sound. This can be None to only play once.
             play_start: The start offset to begin playing the sound at. This is measured in play_units.
             play_end: The stop offset to finish playing the sound at. This is measured in play_units.
             play_units: The units in which play_start and play_stop are measured.

         Returns:
             A new voice handle representing the playing sound.  Note that if no buses are
             currently available to play on or the voice's initial parameters indicated that
             it is not currently audible, the voice will be virtual and will not be played.
             The voice handle will still be valid in this case and can be operated on, but
             no sound will be heard from it until it is determined that it should be converted
             to a real voice.  This can only occur when the update() function is called.
             This voice handle does not need to be closed or destroyed.  If the voice finishes
             its play task, any future calls attempting to modify the voice will simply fail.

             None if the requested sound is already at or above its instance limit and the
             PLAY_FLAG_MAX_INSTANCES_SIMULATE flag is not used.

             None if the play task was invalid or could not be started properly.  This can
             most often occur in the case of streaming sounds if the sound's original data
             could not be opened or decoded properly.
    )";
    ctx.def("play_sound", &PythonContext::playSound, docString, py::arg("sound"), py::arg("flags") = 0,
            py::arg("valid_params") = 0, py::arg("params") = nullptr, py::arg("loop_point") = nullptr,
            py::arg("play_start") = 0, py::arg("play_end") = 0, py::arg("play_units") = UnitType::eFrames,
            py::call_guard<py::gil_scoped_release>());
}

inline void definePythonModuleVoiceObject(py::module& m)
{
    const char* docString;


    py::class_<carb::audio::PythonVoice> voice(m, "Voice");
    voice.doc() = R"(
        Represents a single instance of a playing sound.  A single sound object
        may be playing on multiple voices at the same time, however each voice
        may only be playing a single sound at any given time.
    )";

    docString = R"(
        Stops playback on a voice.

        This stops a voice from playing its current sound.  This will be
        silently ignored for any voice that is already stopped or for an
        invalid voice handle.  Once stopped, the voice will be returned to a
        'free' state and its sound data object unassigned from it.  The voice
        will be immediately available to be assigned a new sound object to play
        from.

        This will only schedule the voice to be stopped.  Its volume will be
        implicitly set to silence to avoid a popping artifact on stop.  The
        voice will continue to play for one more engine cycle until the volume
        level reaches zero, then the voice will be fully stopped and recycled.
        At most, 1ms of additional audio will be played from the voice's sound.

        Args:
            No Arguments.

        Returns:
            No return value.
    )";
    voice.def("stop", &PythonVoice::stop, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(
        Checks the playing state of a voice.

        This checks if a voice is currently playing.  A voice is considered
        playing if it has a currently active sound data object assigned to it
        and it is not paused.

        Args:
            Voice: The voice to check the playing state for.

        Returns:
            True if the requested voice is playing.
            False if the requested voice is not playing or is paused.
            False if the given voice handle is no longer valid.
    )";
    voice.def("is_playing", &PythonVoice::isPlaying, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(
    Sets a new loop point as current on a voice.

    This sets a new loop point for a playing voice.  This allows for behavior
    such as sound atlases or sound playlists to be played out on a single
    voice.

    When desc is None or the contents of the descriptor do not specify a new
    loop point, this will immediately break the loop that is currently playing
    on the voice.  This will have the effect of setting the voice's current
    loop count to zero.  The sound on the voice will continue to play out its
    current loop iteration, but will not loop again when it reaches its end.
    This is useful for stopping a voice that is playing an infinite loop or to
    prematurely stop a voice that was set to loop a specific number of times.
    This call will effectively be ignored if passed in a voice that is not
    currently looping.

    For streaming voices, updating a loop point will have a delay due to
    buffering the decoded data. The sound will loop an extra time if the loop
    point is changed after the buffering has started to consume another loop.
    The default buffer time for streaming sounds is currently 200 milliseconds,
    so this is the minimum slack time that needs to be given for a loop change.

    Args:
        voice: the voice to set the loop point on.  This may not be nullptr.
        point: descriptor of the new loop point to set.  This may contain a loop
               or event point from the sound itself or an explicitly specified
               loop point.  This may be nullptr to indicate that the current loop
               point should be removed and the current loop broken.  Similarly,
               an empty loop point descriptor could be passed in to remove the
               current loop point.

    Returns:
        True if the new loop point is successfully set.

        False if the voice handle is invalid or the voice has already stopped
        on its own.

        False if the new loop point is invalid, not found in the sound data
        object, or specifies a starting point or length that is outside the
        range of the sound data object's buffer.
    )";
    voice.def("set_loop_point", &PythonVoice::setLoopPoint, docString, py::arg("point"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(
    Retrieves the current play cursor position of a voice.

    This retrieves the current play position for a voice.  This is not
    necessarily the position in the buffer being played, but rather the
    position in the sound data object's stream.  For streaming sounds, this
    will be the offset from the start of the stream.  For non-streaming sounds,
    this will be the offset from the beginning of the sound data object's
    buffer.

    If the loop point for the voice changes during playback, the results of
    this call can be unexpected.  Once the loop point changes, there is no
    longer a consistent time base for the voice and the results will reflect
    the current position based off of the original loop's time base.  As long
    as the voice's original loop point remains (ie: setLoopPoint() is never
    called on the voice), the calculated position should be correct.

    It is the caller's responsibility to ensure that this is not called at the
    same time as changing the loop point on the voice or stopping the voice.

    Args:
        type:  The units to retrieve the current position in.

    Returns:
        The current position of the voice in the requested units.

        0 if the voice has stopped playing.

        The last play cursor position if the voice is paused.
    )";
    voice.def("get_play_cursor", &PythonVoice::getPlayCursor, docString, py::arg("type"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(
    Sets one or more parameters on a voice.

    This sets one or more voice parameters in a single call.  Only parameters that
    have their corresponding flag set in paramToSet will be modified.
    If a change is to be relative to the voice's current parameter value, the current
    value should be retrieved first, modified, then set.

    Args:
        paramsToSet:  Flags to indicate which of the parameters need to be updated.
                      This may be one or more of the fVoiceParam* flags.  If this is
                      0, this will simply be a no-op.
        params:       The parameter(s) to be set on the voice.  The flags indicating
                      which parameters need to be set must be set in
                      paramToSet by the caller.  Undefined behavior
                      may occur if a flag is set but its corresponding value(s) have
                      not been properly initialized.  This may not be None.

    Returns:
        No return value.
    )";
    voice.def("set_parameters", &PythonVoice::setParameters, docString, py::arg("params_to_set"), py::arg("params"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(
    Retrieves one or more parameters for a voice.

    This retrieves the current values of one or more of a voice's parameters.
    Only the parameter values listed in paramsToGet flags will be guaranteed
    to be valid upon return.

    Args:
        paramsToGet: Flags indicating which parameter values need to be retrieved.

    Returns:
        The requested parameters in a VoiceParams struct. Everything else is default-initialized.
    )";
    voice.def("get_parameters",
              [](PythonVoice* self, VoiceParamFlags paramsToGet) -> VoiceParams {
                  VoiceParams tmp = {};
                  self->getParameters(paramsToGet, &tmp);
                  return tmp;
              },
              docString, py::arg("params_to_get") = fVoiceParamAll, py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Set flags to indicate how a sound is to be played back.
        This controls whether the sound is played as a spatial or non-spatial
        sound and how the emitter's attributes will be interpreted (ie: either
        world coordinates or listener relative).

        PLAYBACK_MODE_MUTED and PLAYBACK_MODE_PAUSED are ignored here; you'll
        need to use voice.set_mute() or voice.pause() to mute or pause the voice.

        Args:
            playback_mode: The playback mode flag set to set.

        Returns:
            None
    )";
    voice.def("set_playback_mode", &PythonVoice::setPlaybackMode, docString, py::arg("playback_mode"),
              py::call_guard<py::gil_scoped_release>());
    docString = R"(
        The volume level for the voice.

        Args:
            volume: The volume to set.
                    This should be 0.0 for silence or 1.0 for normal volume.
                    A negative value may be used to invert the signal.
                    A value greater than 1.0 will amplify the signal.
                    The volume level can be interpreted as a linear scale where
                    a value of 0.5 is half volume and 2.0 is double volume.
                    Any volume values in decibels must first be converted to a
                    linear volume scale before setting this value.

        Returns:
            None
    )";
    voice.def(
        "set_volume", &PythonVoice::setVolume, docString, py::arg("volume"), py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Sets the mute state for a voice.

        Args:
            mute: When this is set to true, the voice's output will be muted.
                  When this is set to false, the voice's volume will be
                  restored to its previous level.
                  This is useful for temporarily silencing a voice without
                  having to clobber its current volume level or affect its
                  emitter attributes.

        Returns:
            None
    )";
    voice.def("set_mute", &PythonVoice::setMute, docString, py::arg("mute"), py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Non-spatial sound positioning.
        These provide pan and fade values for the voice to give the impression
        that the sound is located closer to one of the quadrants of the
        acoustic space versus the others.
        These values are ignored for spatial sounds.

        Args:
            pan: The non-spatial panning value for a voice.
                 This is 0.0 to have the sound "centered" in all speakers.
                 This is -1.0 to have the sound balanced to the left side.
                 This is 1.0 to have the sound balanced to the right side.
                 The way the sound is balanced depends on  the number of channels.
                 For example, a mono sound will be balanced between the left
                 and right sides according to the panning value, but a stereo
                 sound will just have the left or right channels' volumes
                 turned down according to the panning value.
                 This value is ignored for spatial sounds.
                 The default value is 0.0.

                 Note that panning on non-spatial sounds should only be used
                 for mono or stereo sounds.
                 When it is applied to sounds with more channels, the results
                 are often undefined or may sound odd.

            fade: The non-spatial fade value for a voice.
                  This is 0.0 to have the sound "centered" in all speakers.
                  This is -1.0 to have the sound balanced to the back side.
                  This is 1.0 to have the sound balanced to the front side.
                  The way the sound is balanced depends on the number of channels.
                  For example, a mono sound will be balanced between the front
                  and back speakers according to the fade value, but a 5.1
                  sound will just have the front or back channels' volumes
                  turned down according to the fade value.
                  This value is ignored for spatial sounds.
                  The default value is 0.0.

                  Note that using fade on non-spatial sounds should only be
                  used for mono or stereo sounds.
                  When it is applied to sounds with more channels, the results
                  are often undefined or may sound odd.

        Returns:
            None
    )";
    voice.def("set_balance", &PythonVoice::setBalance, docString, py::arg("pan"), py::arg("fade"),
              py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Set The frequency ratio for a voice.

        Args:
            ratio: This will be 1.0 to play back a sound at its normal rate, a
                   value less than 1.0 to lower the pitch and play it back more
                   slowly, and a value higher than 1.0 to increase the pitch
                   and play it back faster.
                   For example, a pitch scale of 0.5 will play back at half the
                   pitch (ie: lower frequency, takes twice the time to play
                   versus normal), and a pitch scale of 2.0 will play back at
                   double the pitch (ie: higher frequency, takes half the time
                   to play versus normal).
                   The default value is 1.0.

                   On some platforms, the frequency ratio may be silently
                   clamped to an acceptable range internally.
                   For example, a value of 0.0 is not allowed.
                   This will be clamped to the minimum supported value instead.

                   Note that the even though the frequency ratio *can* be set
                   to any value in the range from 1/1024 to 1024, this very
                   large range should only be used in cases where it is well
                   known that the particular sound being operated on will still
                   sound valid after the change.
                   In
                   the real world, some of these extreme frequency ratios may
                   make sense, but in the digital world, extreme frequency
                   ratios can result in audio corruption or even silence.
                   This
                   happens because the new frequency falls outside of the range
                   that is faithfully representable by either the audio device
                   or sound data itself.
                   For example, a 4KHz tone being played at a frequency ratio
                   larger than 6.0 will be above the maximum representable
                   frequency for a 48KHz device or sound file.
                   This case will result in a form of corruption known as
                   aliasing, where the frequency components above the maximum
                   representable frequency will become audio artifacts.
                   Similarly, an 800Hz tone being played at a frequency ratio
                   smaller than 1/40 will be inaudible because it falls below
                   the frequency range of the human ear.

                   In general, most use cases will find that the frequency
                   ratio range of [0.1, 10] is more than sufficient for their
                   needs.
                   Further, for many cases, the range from [0.2, 4] would
                   suffice.
                   Care should be taken to appropriately cap the used range for
                   this value.

        Returns:
            None
    )";
    voice.def("set_frequency_ratio", &PythonVoice::setFrequencyRatio, docString, py::arg("ratio"),
              py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Set the playback priority of this voice.

        Args:
            priority: This is an arbitrary value whose scale is defined by the
                      host app.
                      A value of 0 is the default priority.
                      Negative values indicate lower priorities and positive
                      values indicate higher priorities.
                      This priority value helps to determine which voices are
                      the most important to be audible at any given time.
                      When all buses are busy, this value will be used to
                      compare against other playing voices to see if it should
                      steal a bus from another lower priority sound or if it
                      can wait until another bus finishes first.
                      Higher priority sounds will be ensured a bus to play on
                      over lower priority sounds.
                      If multiple sounds have the same priority levels, the
                      louder sound(s) will take priority.
                      When a higher priority sound is queued, it will try to
                      steal a bus from the quietest sound with lower or equal
                      priority.

        Returns:
            None
    )";
    voice.def("set_priority", &PythonVoice::setPriority, docString, py::arg("priority"),
              py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Sets the spatial mix level for the voice.

        Args:
            level: The mix between the results of a voice's spatial sound
                   calculations and its non-spatial calculations.  When this is
                   set to 1.0, only the spatial sound calculations will affect
                   the voice's playback.
                   This is the default when state.
                   When set to 0.0, only the non-spatial sound calculations
                   will affect the voice's
                   playback.
                   When set to a value between 0.0 and 1.0, the results of the
                   spatial and non-spatial sound calculations will be mixed
                   with the weighting according to this value.
                   This value will be ignored if PLAYBACK_MODE_SPATIAL is not
                   set.
                   The default value is 1.0.  Values above 1.0 will be treated
                   as 1.0.
                   Values below 0.0 will be treated as 0.0.

                   PLAYBACK_MODE_SPATIAL_MIX_LEVEL_MATRIX affects the
                   non-spatial mixing behavior of this parameter for
                   multi-channel voices.
                   By default, a multi-channel spatial voice's non-spatial
                   component will treat each channel as a separate mono voice.
                   With the PLAYBACK_MODE_SPATIAL_MIX_LEVEL_MATRIX flag set,
                   the non-spatial component will be set with the specified
                   output matrix or the default output matrix.

        Returns:
            None
    )";
    voice.def("set_spatial_mix_level", &PythonVoice::setSpatialMixLevel, docString, py::arg("level"),
              py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Sets the doppler scale value for the voice.
        This allows the result of internal doppler calculations to be scaled to emulate
        a time warping effect.


        Args:
            scale: This should be near 0.0 to greatly reduce the effect of the
                   doppler calculations, and up to 5.0 to exaggerate the
                   doppler effect.
                   A value of 1.0 will leave the calculated doppler factors
                   unmodified.
                   The default value is 1.0.

        Returns:
            None
    )";
    voice.def("set_doppler_scale", &PythonVoice::setDopplerScale, docString, py::arg("scale"),
              py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Sets the occlusion factors for a voice.
        These values control automatic low pass filters that get applied to the
        Sets spatial sounds to simulate object occlusion between the emitter
        and listener positions.

        Args:
            direct: The occlusion factor for the direct path of the sound.
                    This is the path directly from the emitter to the listener.
                    This factor describes how occluded the sound's path
                    actually is.
                    A value of 1.0 means that the sound is fully occluded by an
                    object between the voice and the listener.
                    A value of 0.0 means that the sound is not occluded by any
                    object at all.
                    This defaults to 0.0.
                    This factor multiplies by `EntityCone.low_pass_filter`, if a
                    cone with a non 1.0 lowPassFilter value is specified.
                    Setting this to a value outside of [0.0, 1.0] will result
                    in an undefined low pass filter value being used.
            reverb: The occlusion factor for the reverb path of the sound.
                    This is the path taken for sounds reflecting back to the
                    listener after hitting a wall or other object.
                    A value of 1.0 means that the sound is fully occluded by an
                    object between the listener and the object that the sound
                    reflected off of.
                    A value of 0.0 means that the sound is not occluded by any
                    object at all.
                    This defaults to 1.0.

        Returns:
            None
    )";
    voice.def("set_occlusion", &PythonVoice::setOcclusion, docString, py::arg("direct"), py::arg("reverb"),
              py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Set the channel mixing matrix to use for this voice.

        Args:
            matrix: The matrix to set.
                    The rows of this matrix represent
                    each output channel from this voice and the columns of this
                    matrix represent the input channels of this voice (e.g.
                    this is a inputChannels x outputChannels matrix).
                    Note that setting the matrix to be smaller than needed will
                    result in undefined behavior.
                    The output channel count will always be the number of audio
                    channels set on the context.
                    Each cell in the matrix should be a value from 0.0-1.0 to
                    specify the volume that this input channel should be mixed
                    into the output channel.
                    Setting negative values will invert the signal.
                    Setting values above 1.0 will amplify the signal past unity
                    gain when being mixed.

                    This setting is mutually exclusive with balance; setting
                    one will disable the other.
                    This setting is only available for spatial sounds if
                    PLAYBACK_MODE_SPATIAL_MIX_LEVEL_MATRIX if set in the
                    playback mode parameter.
                    Multi-channel spatial audio is interpreted as multiple
                    emitters existing at the same point in space, so a purely
                    spatial voice cannot have an output matrix specified.

                    Setting this to None will reset the matrix to the default
                    for the given channel count.
                    The following table shows the speaker modes that are used
                    for the default output matrices.
                    Voices with a speaker mode that is not in the following
                    table will use the default output matrix for the speaker
                    mode in the following table that has the same number of
                    channels.
                    If there is no default matrix for the channel count of the
                    @ref Voice, the output matrix will have 1.0 in the any cell
                    (i, j) where i == j and 0.0 in all other cells.

        Returns:
            None
    )";
    voice.def(
        "set_matrix", &PythonVoice::setMatrix, docString, py::arg("matrix"), py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Set the voice's position.

        Args:
            position: The current position of the voice in world units.
                      This should only be expressed in meters if the world
                      units scale is set to 1.0 for this context.

        Returns:
            None
    )";
    voice.def("set_position", &PythonVoice::setPosition, docString, py::arg("position"),
              py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Set the voice's velocity.

        Args:
            velocity: The current velocity of the voice in world units per second.
                      This should only be expressed in meters per second if the
                      world units scale is set to 1.0 with for the context.
                      The magnitude of this vector will be taken as the
                      listener's current speed and the vector's direction will
                      indicate the listener's current direction.  This vector
                      should not be normalized unless the listener's speed is
                      actually 1.0 units per second.
                      This may be a zero vector if the listener is not moving.

        Returns:
            None
    )";
    voice.def("set_velocity", &PythonVoice::setVelocity, docString, py::arg("velocity"),
              py::call_guard<py::gil_scoped_release>());
    docString = R"(
        Set custom rolloff curves on the voice.

        Args:
            type: The default type of rolloff calculation to use for all DSP
                  values that are not overridden by a custom curve.
            near_distance: The near distance range for the sound.
                           This is specified in arbitrary world units.
                           When a custom curve is used, this near distance will
                           map to a distance of 0.0 on the curve.
                           This must be less than the far_distance distance.
                           The near distance is the closest distance that the
                           emitter's attributes start to rolloff at.
                           At distances closer than this value, the calculated
                           DSP values will always be the same as if they were
                           at the near distance.
            far_distance: The far distance range for the sound.
                          This is specified in arbitrary world units.
                          When a custom curve is used, this far distance will
                          map to a distance of 1.0 on the curve.  This must be
                          greater than the @ref nearDistance distance.
                          The far distance is the furthest distance that the
                          emitters attributes will rolloff at.
                          At distances further than this value, the calculated
                          DSP values will always be the same as if they were at
                          the far distance (usually silence).
                          Emitters further than this distance will often become
                          inactive in the scene since they cannot be heard any
                          more.
            volume: The custom curve used to calculate volume attenuation over
                    distance.
                    This must be a normalized curve such that a distance of 0.0
                    maps to the near_distance distance and a distance of 1.0
                    maps to the far_distance distance.
                    When specified, this overrides the rolloff calculation
                    specified by type when calculating volume attenuation.
                    If this is an empty array, the parameter will be ignored.
            low_frequency: The custom curve used to calculate low frequency
                           effect volume over distance.
                           This must be a normalized curve such that a distance
                           of 0.0 maps to the near_distance distance and a
                           distance of 1.0 maps to the far_distance distance.
                           When specified, this overrides the rolloff
                           calculation specified by type when calculating
                           the low frequency effect volume.
                           If this is an empty array, the parameter will be
                           ignored.
            low_pass_direct: The custom curve used to calculate low pass filter
                             parameter on the direct path over distance.
                             This must be a normalized curve such that a
                             distance of 0.0 maps to the near_distance distance
                             and a distance of 1.0 maps to the far_distance
                             distance.
                             When specified, this overrides the rolloff
                             calculation specified by type when calculating the
                             low pass filter parameter.
                             If this is an empty array, the parameter will be
                             ignored.
            low_pass_reverb: The custom curve used to calculate low pass filter
                             parameter on the reverb path over distance.
                             This must be a normalized curve such that a
                             distance of 0.0 maps to the near_distance distance
                             and a distance of 1.0 maps to the far_distance
                             distance.
                             When specified, this overrides the rolloff
                             calculation specified by type when calculating the
                             low pass filter parameter.
                             If this is an empty array, the parameter will be
                             ignored.
            reverb: The custom curve used to calculate reverb mix level over
                    distance.
                    This must be a normalized curve such that a distance of 0.0
                    maps to the near_distance distance and a distance of 1.0
                    maps to the @ref farDistance distance.
                    When specified, this overrides the rolloff calculation
                    specified by type when calculating the low pass filter
                    parameter.
                    If this is an empty array, the parameter will be ignored.

        returns:
            None
    )";
    voice.def("set_rolloff_curve", &PythonVoice::setRolloffCurve, docString, py::arg("type"), py::arg("near_distance"),
              py::arg("far_distance"), py::arg("volume") = std::vector<Float2Ex>(),
              py::arg("low_frequency") = std::vector<Float2Ex>(), py::arg("low_pass_direct") = std::vector<Float2Ex>(),
              py::arg("low_pass_reverb") = std::vector<Float2Ex>(), py::arg("reverb") = std::vector<Float2Ex>());
}

inline void definePythonModuleSoundDataObject(py::module& m)
{
    const char* docString;


    py::class_<PythonSoundData> sound(m, "SoundData");
    sound.doc() =
        "Sound data object.  This provides storage for a single sound asset.  The asset's data, "
        "metadata (if any), and various properties about its format are stored and can be "
        "retrieved as needed.  There are also helper functions to allow new data to be written "
        "to the object's internal data buffers.";

    docString = R"(Retrieve the name of a SoundData object.

                   Returns:
                       The name that was given to the object.

                       This will return None if the object has no name.)";
    sound.def("get_name", &PythonSoundData::getName, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(Query if the SoundData object is decoded or streaming.

                   Returns:
                       True if the object is decoded.
                       False if the object is streaming.)";
    sound.def("is_decoded", &PythonSoundData::isDecoded, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(Query the SoundData object's format.

                   Returns:
                       For a sound that was decoded on load, this represents the format of the
                       audio data in the SoundData object's buffer.

                       For a streaming sound, this returns the format of the underlying sound
                       asset that is being streamed.)";
    sound.def("get_format", &PythonSoundData::getFormat, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(Query the SoundData object's buffer length.

                   Args:
                       units The unit type that will be returned. This defaults to UnitType.FRAMES.

                   Returns:
                       The length of the SoundData object's buffer.)";
    sound.def("get_length", &PythonSoundData::getLength, docString, py::arg("units") = UnitType::eFrames,
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Set the length of the valid portion of the SoundData object's buffer.

                   Args:
                       length The new valid length to be set.
                       units  How length will be interpreted. This defaults to UnitType.FRAMES.

                   Returns:
                       The length of the SoundData object's buffer.)";
    sound.def("set_valid_length", &PythonSoundData::setValidLength, docString, py::arg("length"),
              py::arg("units") = UnitType::eFrames, py::call_guard<py::gil_scoped_release>());

    docString = R"(Query the SoundData object's buffer length.

                   Args:
                       units The unit type that will be returned. This defaults to
                             UnitType.FRAMES.

                   Returns:
                       The length of the SoundData object's buffer.)";
    sound.def("get_valid_length", &PythonSoundData::getValidLength, docString, py::arg("units") = UnitType::eFrames,
              py::call_guard<py::gil_scoped_release>());

    docString = R"(
                   Retrieve a buffer of audio from the SoundData object in unsigned 8 bit
                   integer PCM.

                   Args:
                       length The length of the buffer you want to retrieve.
                              This will be clamped if the SoundData object does not have this
                              much data available.
                       offset The offset in the SoundData object to start reading from.
                       units  How length and offset will be interpreted. This defaults to
                              UnitType.FRAMES.

                   Returns:
                       A buffer of audio data from the SoundData object in unsigned 8 bit
                       integer format. The format is a list containing integer data with
                       values in the range [0, 255].)";
    sound.def("get_buffer_as_uint8", &PythonSoundData::getBufferU8, docString, py::arg("length") = 0,
              py::arg("offset") = 0, py::arg("units") = UnitType::eFrames, py::call_guard<py::gil_scoped_release>());

    docString = R"(
                   Retrieve a buffer of audio from the SoundData object in signed 16 bit
                   integer PCM.

                   Args:
                       length The length of the buffer you want to retrieve.
                              This will be clamped if the SoundData object does not have this
                              much data available.
                       offset The offset in the SoundData object to start reading from.
                       units  How length and offset will be interpreted. This defaults to
                              UnitType.FRAMES.

                   Returns:
                       A buffer of audio data from the SoundData object in signed 16 bit
                       integer format. The format is a list containing integer data with
                       values in the range [-32768, 32767].)";
    sound.def("get_buffer_as_int16", &PythonSoundData::getBufferS16, docString, py::arg("length") = 0,
              py::arg("offset") = 0, py::arg("units") = UnitType::eFrames, py::call_guard<py::gil_scoped_release>());

    docString = R"(
                   Retrieve a buffer of audio from the SoundData object in signed 32 bit
                   integer PCM.

                   Args:
                       length The length of the buffer you want to retrieve.
                              This will be clamped if the SoundData object does not have this
                              much data available.
                       offset The offset in the SoundData object to start reading from.
                       units  How length and offset will be interpreted. This defaults to
                              UnitType.FRAMES.

                   Returns:
                       A buffer of audio data from the SoundData object in signed 32 bit
                       integer format. The format is a list containing integer data with
                       values in the range [-2147483648, 2147483647].)";
    sound.def("get_buffer_as_int32", &PythonSoundData::getBufferS32, docString, py::arg("length") = 0,
              py::arg("offset") = 0, py::arg("units") = UnitType::eFrames, py::call_guard<py::gil_scoped_release>());

    docString = R"(
                   Retrieve a buffer of audio from the SoundData object in 32 bit float PCM.

                   Args:
                       length: The length of the buffer you want to retrieve.  This will be
                               clamped if the SoundData object does not have this much data
                               available.
                       offset: The offset in the SoundData object to start reading from.
                       units:  How length and offset will be interpreted. This defaults to
                               `UnitType.FRAMES`.

                   Returns:
                       A buffer of audio data from the SoundData object in signed 32 bit
                       integer format. The format is a list containing integer data with
                       values in the range [-1.0, 1.0].
                   )";
    sound.def("get_buffer_as_float", &PythonSoundData::getBufferFloat, docString, py::arg("length") = 0,
              py::arg("offset") = 0, py::arg("units") = UnitType::eFrames, py::call_guard<py::gil_scoped_release>());

    docString = R"(
                   Write a buffer of audio to the SoundData object with unsigned 8 bit PCM
                   data.

                   Args:
                       data:
                           The buffer of data to write to the SoundData object.
                           This must be a list of integer values representable as uint8_t.
                       offset:
                           The offset in the SoundData object to start reading from.
                       units:
                           How offset will be interpreted. This defaults to `UnitType.FRAMES`.

                   Returns:
                       No return value.

                       This will throw an exception if this is not a writable sound object.
                       Only sounds that were created empty or from raw PCM data are writable.)";
    sound.def("write_buffer_with_uint8", &PythonSoundData::writeBufferU8, docString, py::arg("data"),
              py::arg("offset") = 0, py::arg("units") = UnitType::eFrames, py::call_guard<py::gil_scoped_release>());

    docString = R"(
                   Write a buffer of audio to the SoundData object with signed 16 bit PCM
                   data.

                   Args:
                       data   The buffer of data to write to the SoundData object.
                              This must be a list of integer values representable as int16_t.
                       offset The offset in the SoundData object to start reading from.
                       units  How offset will be interpreted. This defaults to
                              UnitType.FRAMES.

                   Returns:
                       No return value.

                       This will throw an exception if this is not a writable sound object.
                       Only sounds that were created empty or from raw PCM data are writable.)";
    sound.def("write_buffer_with_int16", &PythonSoundData::writeBufferS16, docString, py::arg("data"),
              py::arg("offset") = 0, py::arg("units") = UnitType::eFrames, py::call_guard<py::gil_scoped_release>());

    docString = R"(
                   Write a buffer of audio to the SoundData object with signed 32 bit PCM
                   data.

                   Args:
                       data   The buffer of data to write to the SoundData object.
                              This must be a list of integer values representable as int32_t.
                       offset The offset in the SoundData object to start reading from.
                       units  How offset will be interpreted. This defaults to
                              UnitType.FRAMES.

                   Returns:
                       No return value.

                       This will throw an exception if this is not a writable sound object.
                       Only sounds that were created empty or from raw PCM data are writable.)";
    sound.def("write_buffer_with_int32", &PythonSoundData::writeBufferS32, docString, py::arg("data"),
              py::arg("offset") = 0, py::arg("units") = UnitType::eFrames, py::call_guard<py::gil_scoped_release>());

    docString = R"(
                   Write a buffer of audio to the SoundData object with 32 bit float PCM
                   data.

                   Args:
                       data   The buffer of data to write to the SoundData object.
                              This must be a list of integer values representable as float.
                       offset The offset in the SoundData object to start reading from.
                       units  How offset will be interpreted. This defaults to
                              UnitType.FRAMES.

                   Returns:
                       No return value.

                       This will throw an exception if this is not a writable sound object.
                       Only sounds that were created empty or from raw PCM data are writable.
                   )";
    sound.def("write_buffer_with_float", &PythonSoundData::writeBufferFloat, docString, py::arg("data"),
              py::arg("offset") = 0, py::arg("units") = UnitType::eFrames, py::call_guard<py::gil_scoped_release>());

    docString = R"(Query the amount of memory that's in use by a SoundData object.

                   This retrieves the amount of memory used by a single sound data object.  This
                   will include all memory required to store the audio data itself, to store the
                   object and all its parameters, and the original filename (if any).  This
                   information is useful for profiling purposes to investigate how much memory
                   the audio system is using for a particular scene.

                   Returns:
                       The amount of memory in use by this sound, in bytes.)";
    sound.def("get_memory_used", &PythonSoundData::getMemoryUsed, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(Query the SoundData object's max instance count.

                   This retrieves the current maximum instance count for a sound.  This limit
                   is used to prevent too many instances of a sound from being played
                   simultaneously.  With the limit set to unlimited, playing too many
                   instances can result in serious performance penalties and serious clipping
                   artifacts caused by too much constructive interference.

                   Returns:
                       The SoundData object's max instance count.)";
    sound.def(
        "get_max_instances", &PythonSoundData::getMaxInstances, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(Set the SoundData object's max instance count.

                   This sets the new maximum playing instance count for a sound.  This limit will
                   prevent the sound from being played until another instance of it finishes playing
                   or simply cause the play request to be ignored completely.  This should be used
                   to limit the use of frequently played sounds so that they do not cause too much
                   of a processing burden in a scene or cause too much constructive interference
                   that could lead to clipping artifacts.  This is especially useful for short
                   sounds that are played often (ie: gun shots, foot steps, etc).  At some [small]
                   number of instances, most users will not be able to tell if a new copy of the
                   sound played or not.

                   Args:
                       limit The max instance count to set.)";
    sound.def("set_max_instances", &PythonSoundData::setMaxInstances, docString, py::arg("limit"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Retrieves or calculates the peak volume levels for a sound if possible.

                   This retrieves the peak volume level information for a sound.  This information
                   is either loaded from the sound's original source file or is calculated if
                   the sound is decoded into memory at load time.  This information will not be
                   calculated if the sound is streamed from disk or memory.

                   Returns:
                       The peak level information from the SoundData object.

                       This will throw if peak level information is not embedded in the sound.)";
    sound.def("get_peak_level", &PythonSoundData::getPeakLevel, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(Retrieves embedded event point information from a sound data object.

                   This retrieves event point information that was embedded in the sound file that
                   was used to create a sound data object.  The event points are optional in the
                   data file and may not be present.  If they are parsed from the file, they will
                   also be saved out to any destination file that the same sound data object is
                   written to, provided the destination format supports embedded event point
                   information.

                   Returns:
                       The list of event points that are embedded in this SoundData object.)";
    sound.def("get_event_points", &PythonSoundData::getEventPoints, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(Retrieves a single event point object by its identifier.

                   Args:
                       id The ID of the event point to retrieve.

                   Returns:
                       The event point is retrieved if it exists.

                       None is returned if there was no event point found.)";
    sound.def("get_event_point_by_id", &PythonSoundData::getEventPointById, docString, py::arg("id"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Retrieves a single event point object by its index.

                   Event point indices are contiguous, so this can be used to enumerate event
                   points alternatively.

                   Args:
                       index The index of the event point to retrieve.

                   Returns:
                       The event point is retrieved if it exists.

                       None is returned if there was no event point found.)";
    sound.def("get_event_point_by_index", &PythonSoundData::getEventPointByIndex, docString, py::arg("index"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Retrieves a single event point object by its playlist index.

                   Event point playlist indices are contiguous, so this can be used to
                   enumerate the playlist.

                   Args:
                       index The playlist index of the event point to retrieve.

                   Returns:
                       The event point is retrieved if it exists.

                       None is returned if there was no event point found.)";
    sound.def("get_event_point_by_play_index", &PythonSoundData::getEventPointByPlayIndex, docString, py::arg("index"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Retrieve the maximum play index value for the sound.

                   Returns:
                       This returns the max play index for this SoundData object.
                       This will be 0 if no event points have a play index.
                       This is also the number of event points with playlist indexes,
                       since the playlist index range is contiguous.)";
    sound.def("get_event_point_max_play_index", &PythonSoundData::getEventPointMaxPlayIndex, docString,
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Modifies, adds or removes event points in a SoundData object.

                   This modifies, adds or removed one or more event points in a sound data
                   object.  An event point will be modified if one with the same ID already
                   exists.  A new event point will be added if it has an ID that is not
                   already present in the sound data object and its frame offset is valid.  An
                   event point will be removed if it has an ID that is present in the sound
                   data object but the frame offset for it is set to
                   EVENT_POINT_INVALID_FRAME.  Any other event points with invalid frame
                   offsets (ie: out of the bounds of the stream) will be skipped and cause the
                   function to fail.

                   If an event point is modified or removed such that the playlist
                   indexes of the event points are no longer contiguous, this function
                   will adjust the play indexes of all event points to prevent any
                   gaps.

                   Args:
                       eventPoints: The event point(s) to be modified or added.  The
                                    operation that is performed for each event point in the
                                    table depends on whether an event point with the same ID
                                    already exists in the sound data object.  The event points
                                    in this table do not need to be sorted in any order.

                   Returns:
                       True if all of the event points in the table are updated successfully.
                       False if not all event points could be updated.  This includes a
                       failure to allocate memory or an event point with an invalid frame
                       offset.  Note that this failing doesn't mean that all the event points
                       failed.  This just means that at least failed to be set properly.  The
                       new set of event points may be retrieved and compared to the list set
                       here to determine which one failed to be updated.)";
    sound.def("set_event_points", &PythonSoundData::setEventPoints, docString, py::arg("eventPoints"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Removes all event points from a SoundData object.

                   Returns:
                       No return value.)";
    sound.def(
        "clear_event_points", &PythonSoundData::clearEventPoints, docString, py::call_guard<py::gil_scoped_release>());

    docString = R"(Retrieve a metadata tag from a SoundData object by its index.

                   Args:
                       index The index of the metadata tag.

                   Returns:
                       This returns a tuple: (metadata tag name, metadata tag value).

                       This returns (None, None) if there was no tag at the specified index.)";
    sound.def("get_metadata_by_index", &PythonSoundData::getMetaDataByIndex, docString, py::arg("index"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Retrieve a metadata value from a SoundData object by its tag name.

                   Args:
                       tag_name The metadata tag's name.

                   Returns:
                       This returns the metadata tag value for tag_name.

                       This returns None if there is no tag under tag_name.)";
    sound.def("get_metadata", &PythonSoundData::getMetaData, docString, py::arg("tag_name"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Add a metadata tag to a SoundData object.

                   Metadata tag names are not case sensitive.

                   It is not guaranteed that a given file type will be able to store arbitrary
                   key-value pairs. RIFF files (.wav), for example, store metadata tags under
                   4 character codes, so only metadata tags that are known to this plugin,
                   such as META_DATA_TAG_ARTIST or tags that are 4 characters in length can be
                   stored. Note this means that storing 4 character tags beginning with 'I'
                   runs the risk of colliding with the known tag names (e.g. 'IART' will
                   collide with META_DATA_TAG_ARTIST when writing a RIFF file).

                   tag_name must not contain the character '=' when the output format encodes
                   its metadata in the Vorbis Comment format (SampleFormat.VORBIS and
                   SampleFormat.FLAC do this).  '=' will be replaced with '_' when
                   encoding these formats to avoid the metadata being encoded incorrectly.
                   Additionally, the Vorbis Comment standard states that tag names must only
                   contain characters from 0x20 to 0x7D (excluding '=') when encoding these
                   formats.

                   Args:
                       tag_name:  The metadata tag's name.
                       tag_value: The metadata tag's value.

                   Returns:
                       No return value.)";
    sound.def("set_metadata", &PythonSoundData::setMetaData, docString, py::arg("tag_name"), py::arg("tag_value"),
              py::call_guard<py::gil_scoped_release>());

    docString = R"(Save a SoundData object to disk as a playable audio file.

                   Args:
                       file_name: The path to save this file as.
                       format:    The audio format to use when saving this file.  PCM formats will save as a WAVE file (.wav).
                       flags:     Flags to alter the behavior of this function.  This is a bitmask of `SAVE_FLAG_*` flags.

                   Returns:
                       True if the SoundData object was saved to disk successfully.
                       False if saving to disk failed.)";
    sound.def("save_to_file", &PythonSoundData::saveToFile, docString, py::arg("file_name"),
              py::arg("format") = SampleFormat::eDefault, py::arg("flags") = 0);
}

inline void definePythonModuleIAudioPlaybackInterface(py::module& m)
{
    const char* docString;


    auto playback = carb::defineInterfaceClass<IAudioPlayback>(m, "IAudioPlayback", "acquire_playback_interface");

    playback.doc() =
        "Audio playback interface.  This interface and its objects manages all audio playback "
        "operations and objects.  The main operations in this interface are device discovery "
        "and context object creation.  Once a context object has been created, all of the "
        "playback operations are managed through it.  Note that only a limited number of playback "
        "contexts can exist in a process at any given time.  It is best practice to always explicitly"
        "set the variable holding the context object to `None` when it is no longer needed.  This "
        "helps prevent other attempts to create a new context from failing while waiting for the "
        "object to be garbage collected.";


    docString = R"(Retrieves the current audio output device count for the system.  The device count is a potentially
                   volatile value.  This can change at any time without notice due to user action.  For example, the
                   user could remove an audio device from the system or add a new one at any time.  Thus it is a good
                   idea to open the device as quickly as possible after choosing the device index.  There is no
                   guarantee that the device list will even remain stable during a single device enumeration loop.
                   The only device index that is guaranteed to be valid is the system default device index of 0.

                   Returns:
                       The number of audio output devices that are currently connected to the system.  Device 0 in
                       the list will be the system's default or preferred device.
    )";
    playback.def("get_device_count", [](IAudioPlayback* self) -> size_t { return self->getDeviceCount(); }, docString,
                 py::call_guard<py::gil_scoped_release>());

    docString = R"(Retrieves the capabilities and information about a single audio output device.  This
                   retrieves information about a single audio output device.  The information will be
                   returned in the @p info buffer.  This may fail if the device corresponding to the
                   requested index has been removed from the system.

                   Args:
                       device_index:    The index of the device to retrieve info for.  This must be
                                        between 0 and the most recent return value from
                                        `get_device_count()`.  This defaults to 0 if omitted (ie: the
                                        index of the system's default playback device).

                   Returns:
                       `AudioResult.OK` if the device info was successfully retrieved.
                       `AudioResult.OUT_OF_RANGE` if the requested device index is out of range of the system's
                       current device count.  Note that the system's device count can change at any time due
                       to user action (ie: unplugging an audio device or adding a new one).
                       `AudioResult.NOT_SUPPORTED` if a device is found but it requires an unsupported sample
                       format.
                       An `AudioResult.*` error code if the requested device index was out of range or the info
                       buffer was invalid.)";
    playback.def("get_device_caps",
                 [](IAudioPlayback* self, size_t index) -> DeviceCaps {
                     DeviceCaps caps;
                     self->getDeviceCaps(index, &caps);
                     return caps;
                 },
                 docString, py::arg("index") = 0, py::call_guard<py::gil_scoped_release>());

    docString = R"(Creates a new audio output context object.  This creates a new audio output context object.
                   This object is responsible for managing all access to a single instance of the audio context.
                   Note that there will be a separate audio engine thread associated with each instance of this
                   context object.

                   Upon creation, this object will be in a default state.  This means that the selected device
                   will be opened and its processing engine created.  It will output at the chosen device's
                   default frame rate and channel count.  If needed, a new device may be selected with
                   `set_output()` on the context object.  If a device that defaults to more than
                   `Speaker.COUNT` channels is selected, the output channel mapping will be undefined and
                   spatial audio will not function as expected.  This can only be worked around using the
                   C++ interface and its `setSpeakerDirections()` function.

                   Note:
                       If selecting a device fails during context creation, the context will still be created
                       successfully and be valid for future operations.  The caller will have to select another
                       valid device at a later point before any audio will be output however.  A caller can
                       check if a device has been opened successfully by calling `get_context_caps()` and
                       checking the `ContextCaps.selectedDevice.flags` member to see if it has been set to
                       something other than `DEVICE_FLAG_NOT_OPEN`.

                   Args:
                       desc:    A description of the initial settings and capabilities to use for the new
                                context object.  Omit this parameter to use the system default playback
                                device and its preferred settings.

                   Returns:
                       The newly created audio output context object if successful.
                       Throws a `ContextError` exception if the operation failed.  This can fail if too
                       many playback contexts already exist in the process.)";
    playback.def("create_context",
                 [](IAudioPlayback* self, PlaybackContextDesc desc) -> PythonContext {
                     Context* ctx = self->createContext(&desc);
                     if (ctx == nullptr)
                         throw ContextError("failed to create a new playback context object.");
                     return PythonContext(self, ctx);
                 },
                 docString, py::arg("desc") = PlaybackContextDesc());
}

inline void definePythonModuleIAudioDataInterface(py::module& m)
{
    const char* docString;


    auto data = carb::defineInterfaceClass<IAudioData>(m, "IAudioData", "acquire_data_interface");

    data.doc() = R"(Sound Data management interface.  This allows sounds to be loaded from disk or a blob in
                    memory and to create sound data objects out of those resources.  Each operation here will
                    return a new sound data object that can perform its own operations on the loaded data.
                    The sound data objects can also be passed to `Context.play_sound()` to play.  Note that
                    this interface is completely different from its C++ counterpart.  This has been done to
                    simplify the interface and interactions with it.  Most of the operations found in the C++
                    interface are actually part of the sound data object in the Python API.)";

    docString = R"(Create a SoundData object from a file on disk.

                   Args:
                       filename      The name of the file on disk to create the new sound
                                     data object from.
                       decodedFormat The format you want the audio to be decoded into.
                                     Although you can retrieve the sound's data through python
                                     in any format, the data will be internally stored as this
                                     format.  This is only important if you aren't creating a
                                     decoded sound.  This defaults to SampleFormat.DEFAULT,
                                     which will decode the sound to float for now.
                       flags         Optional flags to change the behavior.  This can be any
                                     of: DATA_FLAG_SKIP_METADATA, DATA_FLAG_SKIP_EVENT_POINTS
                                     or DATA_FLAG_CALC_PEAKS.
                       streaming     Set to True to create a streaming sound.  Streaming
                                     sounds aren't loaded into memory; they remain on disk and
                                     are decoded in chunks as needed.  This defaults to False.
                       autoStream    The threshold in bytes at which the new sound data
                                     object will decide to stream instead of decode into
                                     memory.  If the decoded size of the sound will be
                                     larger than this value, it will be streamed from its
                                     original source instead of decoded.  Set this to 0
                                     to disable auto-streaming. This defaults to 0.

                   Returns:
                       The new sound data if successfully created and loaded.

                       An exception is thrown if the sound could not be loaded. This could
                       happen if the file does not exist, the file is not a supported type,
                       the file is corrupt or some other error occurred during decode.
)";
    data.def("create_sound_from_file",
             [](IAudioData* self, const char* fileName, SampleFormat decodedFormat, DataFlags flags, bool streaming,
                size_t autoStream) -> PythonSoundData* {
                 SoundData* tmp = createSoundFromFile(self, fileName, streaming, autoStream, decodedFormat, flags);
                 if (tmp == nullptr)
                     throw SoundDataError("failed to create a SoundData object");
                 return new PythonSoundData(self, tmp);
             },
             docString, py::arg("fileName"), py::arg("decodedFormat") = SampleFormat::eDefault, py::arg("flags") = 0,
             py::arg("streaming") = false, py::arg("autoStream") = 0, py::call_guard<py::gil_scoped_release>());

    docString = R"(Create a SoundData object from a data blob in memory

                   Args:
                       blob          A bytes object which contains the raw data for an audio
                                     file which has some sort of header.  Raw PCM data will
                                     not work with this function.  Note that due to the way
                                     python works, these bytes will be copied into the
                                     SoundData object's internal buffer if the sound is
                                     streaming.
                       decodedFormat The format you want the audio to be decoded into.
                                     Although you can retrieve the sound's data through python
                                     in any format, the data will be internally stored as this
                                     format.  This is only important if you aren't creating a
                                     decoded sound.  This defaults to SampleFormat.DEFAULT,
                                     which will decode the sound to float for now.
                       flags         Optional flags to change the behavior.  This can be any
                                     of: DATA_FLAG_SKIP_METADATA, DATA_FLAG_SKIP_EVENT_POINTS
                                     or DATA_FLAG_CALC_PEAKS.
                       streaming     Set to True to create a streaming sound.  Streaming
                                     sounds aren't loaded into memory; the audio data remains
                                     in its encoded form in memory and are decoded in chunks
                                     as needed. This is mainly useful for compressed formats
                                     which will expand when decoded. This defaults to False.
                       autoStream    The threshold in bytes at which the new sound data
                                     object will decide to stream instead of decode into
                                     memory.  If the decoded size of the sound will be
                                     larger than this value, it will be streamed from its
                                     original source instead of decoded.  Set this to 0
                                     to disable auto-streaming. This defaults to 0.

                   Returns:
                       The new sound data if successfully created and loaded.

                       An exception is thrown if the sound could not be loaded. This could
                       happen if the blob is an unsupported audio format, the blob is corrupt
                       or some other error during decoding.)";
    data.def("create_sound_from_blob",
             [](IAudioData* self, const py::bytes blob, SampleFormat decodedFormat, DataFlags flags, bool streaming,
                size_t autoStream) -> PythonSoundData* {
                 // this is extremely inefficient, but this appears to be the only way to get the data
                 std::string s = blob;
                 SoundData* tmp;
                 {
                     py::gil_scoped_release nogil;
                     tmp = createSoundFromBlob(self, s.c_str(), s.length(), streaming, autoStream, decodedFormat, flags);
                     if (tmp == nullptr)
                         throw SoundDataError("failed to create a SoundData object");
                 }
                 return new PythonSoundData(self, tmp);
             },
             docString, py::arg("blob"), py::arg("decodedFormat") = SampleFormat::eDefault, py::arg("flags") = 0,
             py::arg("streaming") = false, py::arg("autoStream") = 0);

    docString = R"(Create a SoundData object from raw 8 bit unsigned integer PCM data.

                   Args:
                       pcm          The audio data to load into the SoundData object.
                                    This will be copied to an internal buffer in the object.
                       channels     The number of channels of data in each frame of the audio
                                    data.
                       frame_rate   The number of frames per second that must be played back
                                    for the audio data to sound 'normal' (ie: the way it was
                                    recorded or produced).
                       channel_mask the channel mask for the audio data.  This specifies which
                                    speakers the stream is intended for and will be a
                                    combination of one or more of the Speaker names or a
                                    SpeakerMode name.  The channel mapping will be set to the
                                    defaults if set to SPEAKER_MODE_DEFAULT, which is the
                                    default value for this parameter.

                   Returns:
                       The new sound data if successfully created and loaded.

                       An exception may be thrown if an out-of-memory situation occurs or some
                       other error occurs while creating the object.)";
    data.def("create_sound_from_uint8_pcm",
             [](IAudioData* self, const std::vector<uint8_t>& pcm, size_t channels, size_t frameRate,
                SpeakerMode channelMask) -> PythonSoundData* {
                 return PythonSoundData::fromRawBlob(
                     self, pcm.data(), pcm.size(), SampleFormat::ePcm8, channels, frameRate, channelMask);
             },
             docString, py::arg("pcm"), py::arg("channels"), py::arg("frame_rate"),
             py::arg("channel_mask") = kSpeakerModeDefault, py::call_guard<py::gil_scoped_release>());

    docString = R"(Create a SoundData object from raw 16 bit signed integer PCM data.

                   Args:
                       pcm          The audio data to load into the SoundData object.
                                    This will be copied to an internal buffer in the object.
                       channels     The number of channels of data in each frame of the audio
                                    data.
                       frame_rate   The number of frames per second that must be played back
                                    for the audio data to sound 'normal' (ie: the way it was
                                    recorded or produced).
                       channel_mask the channel mask for the audio data.  This specifies which
                                    speakers the stream is intended for and will be a
                                    combination of one or more of the Speaker names or a
                                    SpeakerMode name.  The channel mapping will be set to the
                                    defaults if set to SPEAKER_MODE_DEFAULT, which is the
                                    default value for this parameter.

                   Returns:
                       The new sound data if successfully created and loaded.

                       An exception may be thrown if an out-of-memory situation occurs or some
                       other error occurs while creating the object.)";
    data.def("create_sound_from_int16_pcm",
             [](IAudioData* self, const std::vector<int16_t>& pcm, size_t channels, size_t frameRate,
                SpeakerMode channelMask) -> PythonSoundData* {
                 return PythonSoundData::fromRawBlob(
                     self, pcm.data(), pcm.size(), SampleFormat::ePcm16, channels, frameRate, channelMask);
             },
             docString, py::arg("pcm"), py::arg("channels"), py::arg("frame_rate"),
             py::arg("channel_mask") = kSpeakerModeDefault, py::call_guard<py::gil_scoped_release>());

    docString = R"(Create a SoundData object from raw 32 bit signed integer PCM data.

                   Args:
                       pcm          The audio data to load into the SoundData object.
                                    This will be copied to an internal buffer in the object.
                       channels     The number of channels of data in each frame of the audio
                                    data.
                       frame_rate   The number of frames per second that must be played back
                                    for the audio data to sound 'normal' (ie: the way it was
                                    recorded or produced).
                       channel_mask the channel mask for the audio data.  This specifies which
                                    speakers the stream is intended for and will be a
                                    combination of one or more of the Speaker names or a
                                    SpeakerMode name.  The channel mapping will be set to the
                                    defaults if set to SPEAKER_MODE_DEFAULT, which is the
                                    default value for this parameter.

                   Returns:
                       The new sound data if successfully created and loaded.

                       An exception may be thrown if an out-of-memory situation occurs or some
                       other error occurs while creating the object.)";
    data.def("create_sound_from_int32_pcm",
             [](IAudioData* self, const std::vector<int32_t>& pcm, size_t channels, size_t frameRate,
                SpeakerMode channelMask) -> PythonSoundData* {
                 return PythonSoundData::fromRawBlob(
                     self, pcm.data(), pcm.size(), SampleFormat::ePcm32, channels, frameRate, channelMask);
             },
             docString, py::arg("pcm"), py::arg("channels"), py::arg("frame_rate"),
             py::arg("channel_mask") = kSpeakerModeDefault, py::call_guard<py::gil_scoped_release>());

    docString = R"(Create a SoundData object from raw 32 bit float PCM data.

                   Args:
                       pcm          The audio data to load into the SoundData object.
                                    This will be copied to an internal buffer in the object.
                       channels     The number of channels of data in each frame of the audio
                                    data.
                       frame_rate   The number of frames per second that must be played back
                                    for the audio data to sound 'normal' (ie: the way it was
                                    recorded or produced).
                       channel_mask the channel mask for the audio data.  This specifies which
                                    speakers the stream is intended for and will be a
                                    combination of one or more of the Speaker names or a
                                    SpeakerMode name.  The channel mapping will be set to the
                                    defaults if set to SPEAKER_MODE_DEFAULT, which is the
                                    default value for this parameter.

                   Returns:
                       The new sound data if successfully created and loaded.

                       An exception may be thrown if an out-of-memory situation occurs or some
                       other error occurs while creating the object.)";
    data.def("create_sound_from_float_pcm",
             [](IAudioData* self, const std::vector<float>& pcm, size_t channels, size_t frameRate,
                SpeakerMode channelMask) -> PythonSoundData* {
                 return PythonSoundData::fromRawBlob(
                     self, pcm.data(), pcm.size(), SampleFormat::ePcmFloat, channels, frameRate, channelMask);
             },
             docString, py::arg("pcm"), py::arg("channels"), py::arg("frame_rate"),
             py::arg("channel_mask") = kSpeakerModeDefault, py::call_guard<py::gil_scoped_release>());

    docString = R"(
                   Create a SoundData object with an empty buffer that can be written to.

                   After creating a SoundData object with this, you will need to call one of
                   the write_buffer_*() functions to load your data into the object, then you
                   will need to call set_valid_length() to indicate how much of the sound now
                   contains valid data.

                   Args:

                       decodedFormat:
                           The format for the SoundData object's buffer.  Although you can
                           retrieve the sound's data through python in any format, the data
                           will be internally stored as this format. This defaults to
                           SampleFormat.DEFAULT, which will use float for the buffer.

                       channels:
                           The number of channels of data in each frame of the audio data.

                       frame_rate:
                           The number of frames per second that must be played back for the
                           audio data to sound 'normal' (ie: the way it was recorded or produced).

                       buffer_length:
                           How long you want the buffer to be.

                       units:
                           How buffer_length will be interpreted.  This defaults to UnitType.FRAMES.

                       name:
                           An optional name that can be given to the SoundData object to make it
                           easier to track. This can be None if it is not needed. This defaults
                           to `None`.

                       channel_mask:
                           The channel mask for the audio data.  This specifies which speakers the
                           stream is intended for and will be a combination of one or more of the
                           `Speaker` names or a `SpeakerMode` name.  The channel mapping will be set
                           to the defaults if set to `SPEAKER_MODE_DEFAULT`, which is the default
                           value for this parameter.

                   Returns:
                       The new sound data if successfully created and loaded.

                       An exception may be thrown if an out-of-memory situation occurs or some
                       other error occurs while creating the object.
)";
    data.def("create_empty_sound",
             [](IAudioData* self, SampleFormat format, size_t channels, size_t frameRate, size_t bufferLength,
                UnitType units, const char* name, SpeakerMode channelMask) -> PythonSoundData* {
                 (void)channelMask; // FIXME: channelMask!?
                 SoundData* tmp = createEmptySound(self, format, frameRate, channels, bufferLength, units, name);
                 if (tmp == nullptr)
                     throw SoundDataError("failed to create a SoundData object");
                 return new PythonSoundData(self, tmp);
             },
             docString, py::arg("format"), py::arg("channels"), py::arg("frame_rate"), py::arg("buffer_length"),
             py::arg("units") = UnitType::eFrames, py::arg("name") = nullptr,
             py::arg("channel_mask") = kSpeakerModeDefault, py::call_guard<py::gil_scoped_release>());
}

} // namespace detail

inline void definePythonModule(py::module& m)
{
    m.doc() = R"(
        This module contains bindings for the `IAudioPlayback` interface.
        This is the low-level audio playback interface for Carbonite.
        Several of these bindings have been simplified versus the C++
        API.  For the full functionality of the `IAudioPlayback`, the C++
        API will need to be used directly.
    )";

    detail::definePythonModuleExceptions(m);
    detail::definePythonModuleConstants(m);
    detail::definePythonModuleEnums(m);
    detail::definePythonModuleStructs(m);
    detail::definePythonModuleHelperFunctions(m);
    detail::definePythonModuleContextObject(m);
    detail::definePythonModuleVoiceObject(m);
    detail::definePythonModuleSoundDataObject(m);
    detail::definePythonModuleIAudioPlaybackInterface(m);
    detail::definePythonModuleIAudioDataInterface(m);
}

} // namespace audio
} // namespace carb
