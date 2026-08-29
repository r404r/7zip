// NameCodePageProps.h

#ifndef ZIP7_INC_NAME_CODE_PAGE_PROPS_H
#define ZIP7_INC_NAME_CODE_PAGE_PROPS_H

#include "Property.h"

/* kNameCodePage_Auto means that no code page is asked for */
const UInt32 kNameCodePage_Auto = (UInt32)(Int32)-1;

/* only Zip and Tar know "cp", and a handler that gets a property it doesn't
   know fails to open the archive, so the type is named in the prefix */
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
