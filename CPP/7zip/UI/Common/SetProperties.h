// SetProperties.h

#ifndef ZIP7_INC_SETPROPERTIES_H
#define ZIP7_INC_SETPROPERTIES_H

#include "Property.h"

HRESULT SetProperties(IUnknown *unknown, const CObjectVector<CProperty> &properties);

/* the name of property can be prefixed with the name of archive type and the dot:
   "zip.cp=936". Such property will be sent only to the handler of that type,
   and the prefix will be removed. The properties without prefix are sent to any
   handler. It allows to use the properties that are supported by some types only,
   when the type is not known in advance (extracting) or is selected by the user. */
HRESULT SetProperties(IUnknown *unknown, const CObjectVector<CProperty> &properties,
    const UString &arcType);

#endif
