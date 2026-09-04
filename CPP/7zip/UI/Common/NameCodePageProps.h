// NameCodePageProps.h

#ifndef ZIP7_INC_NAME_CODE_PAGE_PROPS_H
#define ZIP7_INC_NAME_CODE_PAGE_PROPS_H

#include "Property.h"

/* kNameCodePage_Auto means that no code page is asked for */
const UInt32 kNameCodePage_Auto = (UInt32)(Int32)-1;

struct CCodePagePair
{
  UInt32 CodePage;
  const char *Name;
};

static const char * const k_NameCodePage_Types[] = { "zip", "tar" };

/* the common ones; another code page can be typed in */
static const CCodePagePair k_CodePages[] =
{
  { 65001, "UTF-8" },
  {   932, "Japanese" },
  {   936, "Chinese Simplified" },
  {   949, "Korean" },
  {   950, "Chinese Traditional" },
  {   874, "Thai" },
  {  1250, "Central European" },
  {  1251, "Cyrillic" },
  {  1252, "Western European" },
  {  1253, "Greek" },
  {  1254, "Turkish" },
  {  1255, "Hebrew" },
  {  1256, "Arabic" },
  {  1257, "Baltic" },
  {  1258, "Vietnamese" },
  {   437, "OEM United States" },
  {   850, "OEM Latin 1" },
  {   852, "OEM Latin 2" },
  {   866, "OEM Cyrillic" }
};

/* the token for Auto. It is not translated: it is also read back by
   ParseNameCodePage(), so both sides must use the same text. */
#define k_NameCodePage_AutoText "Auto"

/* "936 (Chinese Simplified)" - the form the user sees and can type back.
   Whatever it writes, ParseNameCodePage() must be able to read again. */
inline void NameCodePage_ToString(UString &s, UInt32 codePage)
{
  s.Empty();
  if (codePage == kNameCodePage_Auto)
  {
    s = k_NameCodePage_AutoText;
    return;
  }
  s.Add_UInt32(codePage);
  for (unsigned i = 0; i < Z7_ARRAY_SIZE(k_CodePages); i++)
    if (k_CodePages[i].CodePage == codePage)
    {
      s += " (";
      s += k_CodePages[i].Name;
      s += ")";
      break;
    }
}


/* Parse what the user typed in the combo box. An empty string means Auto.
   The text of a list item ("936 (Chinese Simplified)") is accepted too, so
   that selecting an item and then editing it still works. */
inline bool ParseNameCodePage(const UString &s, UInt32 &codePage)
{
  unsigned i = 0;
  while (i < s.Len() && s[i] == L' ')
    i++;
  if (i == s.Len())
  {
    codePage = kNameCodePage_Auto;
    return true;
  }
  if (StringsAreEqualNoCase_Ascii(s.Ptr(i), k_NameCodePage_AutoText))
  {
    codePage = kNameCodePage_Auto;
    return true;
  }
  UInt32 v = 0;
  const unsigned start = i;
  for (; i < s.Len(); i++)
  {
    const wchar_t c = s[i];
    if (c < L'0' || c > L'9')
      break;
    v = v * 10 + (UInt32)(c - L'0');
    if (v > 0xFFFF)
      return false;
  }
  if (i == start)
    return false;
  if (i != s.Len() && s[i] != L' ')
    return false;
  codePage = v;
  return true;
}

inline bool IsNameCodePageArcType(const UString &s)
{
  for (unsigned i = 0; i < Z7_ARRAY_SIZE(k_NameCodePage_Types); i++)
    if (s.IsEqualTo_Ascii_NoCase(k_NameCodePage_Types[i]))
      return true;
  return false;
}

/* only Zip and Tar know "cp", and a handler that gets a property it doesn't
   know fails to open the archive, so the type is named in the prefix */
inline void AddNameCodePageProps(CObjectVector<CProperty> &props, UInt32 codePage)
{
  if (codePage == kNameCodePage_Auto)
    return;
  UString value;
  value.Add_UInt32(codePage);
  for (unsigned i = 0; i < Z7_ARRAY_SIZE(k_NameCodePage_Types); i++)
  {
    CProperty &prop = props.AddNew();
    prop.Name = k_NameCodePage_Types[i];
    prop.Name += ".cp";
    prop.Value = value;
  }
}

#endif
