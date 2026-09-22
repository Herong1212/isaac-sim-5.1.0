# C++ Usage Examples

## Controlling the timeline
This example demonstrates how to use various API functions to control the timeline's state:

```cpp
#include <omni/timeline/ITimeline.h>

void controlTimelineExamples()
{
    // Obtain the main timeline object
    omni::timeline::TimelinePtr timeline = omni::timeline::getTimeline();

    // Start playing the timeline
    timeline->play();

    // Check if the timeline is playing
    // Output will be false as state changes are applied in the next frame
    printf("%s", timeline->isPlaying() ? "true" : "false");

    // Set current time to t = 3 seconds
    timeline->setCurrentTime(3.0);

    // Perform additional operations...

    // Pause the timeline
    timeline->pause();

    // Advance the timeline by one frame
    // Frame duration can be set with timeline.set_time_codes_per_second
    timeline->forward_one_frame();
}
```

## Registering callbacks for timeline state changes
The following code example shows how to register a callback to respond to various timeline state changes:

```cpp
#include <omni/timeline/ITimeline.h>
#include <omni/timeline/TimelineTypes.h>
#include <carb/dictionary/IDictionary.h>

void registerEventCallbackExample()
{
    // Obtain the main timeline object
    omni::timeline::TimelinePtr timeline = omni::timeline::getTimeline();

    // Register a callback that listens to all timeline events
    carb::events::ISubscriptionPtr updateSubscription = carb::events::createSubscriptionToPop(
        timeline->getTimelineEventStream(),
        // Define a callback function to handle timeline events
        [](carb::events::IEvent* e) {
            using namespace omni::timeline;
            
            carb::dictionary::IDictionary* iDictionary = carb::dictionary::getCachedDictionaryInterface();
            TimelineEventType eventType = static_cast<TimelineEventType>(e->type);
            switch(eventType)
            {
            case TimelineEventType::eCurrentTimeTicked:
            {
                // Difference between the last current time and the new one
		        // Clamped to zero if it would be negative
                double dt = iDictionary->get<double>(e->payload, "dt");
                // Retrieve the new current time
                double currentTime = iDictionary->get<double>(e->payload, "currentTime");
                printf("Current time changed, dt = %f, end of frame = %f\n", dt, currentTime);
                break;
            }
            case TimelineEventType::ePlay:
                printf("Timeline is now playing\n");
                break;
            case TimelineEventType::eStop:
                printf("Timeline is now stopped\n");
                break;
            case TimelineEventType::ePause:
                printf("Timeline is now paused\n");
                break;
            case TimelineEventType::eStartTimeChanged:
            {
                double startTime = iDictionary->get<double>(e->payload, "startTime")
                printf("Timeline has a new start time: %f\n", startTime);
                break;
            }
            // For more events, please consult the TimelineEventType documentation
            }
        },
        0, // update order
        "Example update");

    // Demonstrate the callback functionality by triggering various timeline events
    timeline->setStartTime(1.0);
    timeline->play();
    timeline->set_current_time(3.0);
    timeline->pause();
    timeline->stop();
}
```