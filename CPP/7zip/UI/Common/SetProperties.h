// SetProperties.h
// Modified in 7-Zip-fork, 2026: https://github.com/r404r/7zip

#ifndef ZIP7_INC_SETPROPERTIES_H
#define ZIP7_INC_SETPROPERTIES_H

#include "Property.h"

HRESULT SetProperties(IUnknown *unknown, const CObjectVector<CProperty> &properties);

/* the name of property can be prefixed with the name of archive type and the
   dot: "zip.cp=936". Such property is sent only to the handler of that type,
   with the prefix removed. The properties without prefix are sent to any
   handler, as before. */
HRESULT SetProperties(IUnknown *unknown, const CObjectVector<CProperty> &properties,
    const UString &arcType);

#endif
