// NameEncodingOverride.h

#ifndef ZIP7_INC_NAME_ENCODING_OVERRIDE_H
#define ZIP7_INC_NAME_ENCODING_OVERRIDE_H

#include "../../../Common/MyString.h"

/* "cu" and "cl" set the flags, "cp" sets the code page, and one doesn't
   cancel another. So the order of properties can't decide the winner, and
   a dialog control must not add its own property, if any of them is written
   by hand. The strings are the ones from SplitOptionsToStrings(). */
static bool IsThereNameEncodingOverride(const UStringVector &strings)
{
  FOR_VECTOR (i, strings)
  {
    UString name = strings[i];
    const int pos = name.Find(L'=');
    if (pos >= 0)
      name.DeleteFrom((unsigned)pos);
    if (!name.IsEmpty())
    {
      const wchar_t c = name.Back();
      if (c == L'-' || c == L'+')
        name.DeleteBack();
    }
    if (name.IsEqualTo_Ascii_NoCase("cu")
        || name.IsEqualTo_Ascii_NoCase("cl")
        || name.IsEqualTo_Ascii_NoCase("cp"))
      return true;
  }
  return false;
}

#endif
