# Path Syntax

Syntax is:
**WindowName//WidgetPath**

where:
+ WindowName is a string (potentially containing spaces) but as far as I know, no special characters
+ WidgetPath is a set of "/" delineated Path Segments, each denoting either:
    + the identifier of a widget (obtained from widget.identifier)
    + the type of the widget, with an index `[n]` where n indicates that the widget is the parent widgets nth child of that type

e.g
```MyWindow//Frame/HStack[0]/VStack[1]/HStack[0]/Button[0]```

This is used to refer directly to a single widget


Note:
+ in the future we may add additonal segments after WidgetPath to allow various widget models to be addressed or set
+ Currently every Window contains a "Frame" which can have a single child. We include the frame in the path, but perhaps this is redundant


# Query Syntax

This is a variation of the Path syntax where any token can be replaced with:
+ `*` - find immediate children
+ `**` - find children (recursively)
+ `TypeName[*]` - find immediate children of a specific type


## Predicate
We can also specify a predicate for a property on the widget at the end of the Query (used a dot to add the property) followed by the predicate e.g ```.text=="OK"```

The predicate can be any valid python expression

Examples
```
widgets = InspectorQuery.find_widgets("the_window//Frame/**/Button[*].name=='Button3'")
```

```
widgets = InspectorQuery.find_widgets("the_window//Frame/**/Button[*].identifier=='ButtonX'")
```
