// NameCodePageProps.h

#ifndef ZIP7_INC_NAME_CODE_PAGE_PROPS_H
#define ZIP7_INC_NAME_CODE_PAGE_PROPS_H

#include "Property.h"

/* The code page for the names that the archive doesn't describe itself.
   kNameCodePage_Auto means that no code page is asked for. */
const UInt32 kNameCodePage_Auto = (UInt32)(Int32)-1;

/* Only Zip and Tar know the "cp" property, and a handler that gets a property
   it doesn't know fails to open the archive. So the property is addressed to
   these types by the prefix that SetProperties() understands. Auto must add
   nothing at all: an empty list keeps the current behavior. */
inline void AddNameCodePageProps(CObjectVector<CProperty> &props, UInt32 codePage)
{
  if (codePage == kNameCodePage_Auto)
    return;
  UString value;
  value.Add_UInt32(codePage);
  const char * const kTypes[] = { "zip", "tar" };
  for (unsigned i = 0; i < Z7_ARRAY_SIZE(kTypes); i++)
  {
    CProperty &prop = props.AddNew();
    prop.Name = kTypes[i];
    prop.Name += ".cp";
    prop.Value = value;
  }
}

#endif
