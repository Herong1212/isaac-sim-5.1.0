# Change Tracking in USDRT

USDRT offers an option for tracking changes to Fabric scene data with the 
RtChangeTracker class, which is available for users in both C++ and Python.
Like the rest of the USDRT Scenegraph API, RtChangeTracker aims to leverage the
performance gains of Fabric while remaining accessible for USD-centric developers.

## Background

### Change Tracking in USD

USD provides native support for change tracking through a notification subsystem.
It works by notifying interested objects when an event has occured somewhere in the application.

Notifications are defined by users by extending the [TfNotice](https://graphics.pixar.com/usd/dev/api/class_tf_notice.html) 
base class. The user can populate these notifications with relevant information about the triggering event. 
Listener classes register interest in specific notice classes. When a notice-triggering function
is invoked, the subsystem delivers a notice to all interested listener objects.

Because the subsystem synchronously invokes each listener from the sender's thread,
performance is highly dependent on the listeners. The original thread is blocked until
all listeners resolve. Avoiding this potential block is one of the main goals of change tracking in USDRT.

More details about the TfNotice subsystem can be found in
[Pixar's USD Documentation](https://graphics.pixar.com/usd/dev/api/page_tf__notification.html).

### Change Tracking in Fabric

Fabric provides a non-blocking subsystem to track changes to prim and attributes in Fabric buckets.
Instead of using notifications, Fabric changes are tracked by ID and polled at whatever frequency the developer requires. 

Multiple listeners can be registered to a stage, and tracking is enabled by attribute name per listener.
Fabric provides methods to manage what attributes are currently being tracked, as well as methods to
query and clear changes on a listener.

Below is a usage example that enables change tracking on a listener for the position attribute,
and then queries and iterates through the changes after they occur.

**C++**
```c++
ListenerId listener = iSimStageWithHistory->createListener();
stage.attributeEnableChangeTracking(positionToken, listener);

// Changes are made to position attributes on the stage

ChangedPrimBucketList changedBuckets = stage.getChanges(listener);

for (size_t i = 0; i != changedBuckets.size(); i++)
 {
     BucketChanges changes = changedBuckets.getChanges(i);
     gsl::span<const Path> paths = changes.pathArray;

     for (size_t j = 0; j != changes.attrChangedIndices.size(); j++)
     {
         const AttrAndChangedIndices& changedIndices = changes.attrChangedIndices[j];
         const AttrNameAndType& attribute = changedIndices.attr;

         CHECK(changedIndices.allIndicesChanged);

         if (attribute.name == Token(position))
         {
             auto positions = stage.getAttributeArrayRd<float>(changedBuckets, i, attribute.name);
             for (size_t k = 0; k != positions.size(); k++)
                 initialValueNotifications.emplace(paths[k], positions[k]);
         }
      }
 }
```

Change tracking in Fabric is fast and non-blocking. However, the underlying struct (BucketChanges) that changes
are stored and returned in relies on some understanding of Fabric's underlying bucket-based structure.
For developers that are used to working with the standard USD API, this may not be as intuitive.

## RtChangeTracker

The RtChangeTracker class provides an interface for tracking changes to Fabric data.
Unlike TfNotice, RtChangeTracker handles change notifications in a non-blocking manner.
RtChangeTracker leverages Fabric's change tracking capabilities, while abstracting out
the underlying bucket-based details. It also adds helper methods for querying changes
in the data by prim and attribute.

### Functionality Overview

Under the hood, an RtChangeTracker instance represents one listener in Fabric. Just like on the Fabric side,
users add attribute names they are interested in tracking to the RtChangeTracker instance. The RtChangeTracker
class closely mirrors Fabric's functionality for managing the tracked attributes:

- TrackAttribute(TfToken attrName)
- StopTrackingAttribute(TfToken attrName)
- PauseTracking()
- ResumeTracking()
- IsChangeTrackingPaused()
- IsTrackingAttribute(TfToken attrName)
- GetTrackedAttributes()

When a change occurs on a tracked attribute, the change gets added to a persistent stack of changes.
These changes accumulate over time in the change tracker. A user can query for the presence of any changes
as needed, and clear any that have accumulated to "reset" the stack:

- HasChanges()
- ClearChanges()

The RtChangeTracker class adds functionality atop Fabric's change tracking that lets users query
specific information from the stack of changes by prim and attribute:

- GetAllChangedPrims()
- GetAllChangedAttributes()
- PrimChanged(UsdPrim prim) & PrimChanged(SdfPath primPath)
- AttributeChanged(UsdAttribute attr) & AttributeChanged(SdfPath primPath)

Currently, RtChangeTracker supports tracking changes to attribute values in a scene.
Future work includes adding support for tracking the creation and deletion of prims,
which is currently supported in Fabric.

### Usage Examples

**C++**
```c++
#include <usdrt/scenegraph/usd/rt/changeTracker.h>

using namespace usdrt;

UsdStageRefPtr stage = UsdStage::Open("./data/usd/tests/cornell.usda");
UsdPrim prim = stage->GetPrimAtPath(SdfPath("/DistantLight"));

RtChangeTracker tracker(stage);
tracker.TrackAttribute("color");

UsdAttribute color = prim.GetAttribute("color");
GfVec3f newColor(0, 0.5, 0.5);
color.Set(newColor, 0.0);

std::vector<TfToken> result = tracker.GetChangedAttributes(SdfPath("/DistantLight"));
// result = [TfToken(“color”)]
```

**Python**
```python
from usdrt import Gf, Rt, Sdf, Usd

stage = Usd.Stage.Open(TEST_DIR + '/data/usd/tests/cornell.usda')

prim = stage.GetPrimAtPath(Sdf.Path('/DistantLight'))
color = prim.GetAttribute('color')

tracker = Rt.ChangeTracker(stage)
tracker.TrackAttribute('color')

newColor = (0, 0.5, 0.5)
color.Set(newColor, 0)

result = tracker.GetChangedAttributes('/DistantLight'))
# result = ["color"]
```
