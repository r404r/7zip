// SetProperties.cpp
// Modified in 7-Zip-fork, 2026: https://github.com/r404r/7zip

#include "StdAfx.h"

#include "../../../Common/MyCom.h"
#include "../../../Common/MyString.h"
#include "../../../Common/StringToInt.h"

#include "../../../Windows/PropVariant.h"

#include "../../Archive/IArchive.h"

#include "SetProperties.h"

using namespace NWindows;
using namespace NCOM;

static void ParseNumberString(const UString &s, NCOM::CPropVariant &prop)
{
  const wchar_t *end;
  const UInt64 result = ConvertStringToUInt64(s, &end);
  if (*end != 0 || s.IsEmpty())
    prop = s;
  else if (result <= (UInt32)0xFFFFFFFF)
    prop = (UInt32)result;
  else
    prop = result;
}


struct CPropPropetiesVector
{
  CPropVariant *values;
  CPropPropetiesVector(unsigned num)
  {
    values = new CPropVariant[num];
  }
  ~CPropPropetiesVector()
  {
    delete []values;
  }
};


static HRESULT SetProperties_Always(IUnknown *unknown, const CObjectVector<CProperty> &properties);

HRESULT SetProperties(IUnknown *unknown, const CObjectVector<CProperty> &properties,
    const UString &arcType)
{
  CObjectVector<CProperty> props;
  FOR_VECTOR (i, properties)
  {
    const CProperty &property = properties[i];
    const int dotPos = property.Name.Find(L'.');
    if (dotPos <= 0)
      props.Add(property);
    else if (property.Name.Left((unsigned)dotPos).IsEqualTo_NoCase(arcType.Ptr()))
    {
      CProperty &prop2 = props.AddNew();
      prop2.Name = property.Name.Ptr((unsigned)(dotPos + 1));
      prop2.Value = property.Value;
    }
  }
  /* even if nothing is left for this type: a handler that is opened again
     still keeps the properties of the previous call */
  return SetProperties_Always(unknown, props);
}


HRESULT SetProperties(IUnknown *unknown, const CObjectVector<CProperty> &properties)
{
  if (properties.IsEmpty())
    return S_OK;
  return SetProperties_Always(unknown, properties);
}

static HRESULT SetProperties_Always(IUnknown *unknown, const CObjectVector<CProperty> &properties)
{
  Z7_DECL_CMyComPtr_QI_FROM(
      ISetProperties,
      setProperties, unknown)
  if (!setProperties)
    return S_OK;

  UStringVector realNames;
  CPropPropetiesVector values(properties.Size());
  {
    unsigned i;
    for (i = 0; i < properties.Size(); i++)
    {
      const CProperty &property = properties[i];
      NCOM::CPropVariant propVariant;
      UString name = property.Name;
      if (property.Value.IsEmpty())
      {
        if (!name.IsEmpty())
        {
          const wchar_t c = name.Back();
          if (c == L'-')
            propVariant = false;
          else if (c == L'+')
            propVariant = true;
          if (propVariant.vt != VT_EMPTY)
            name.DeleteBack();
        }
      }
      else
        ParseNumberString(property.Value, propVariant);
      realNames.Add(name);
      values.values[i] = propVariant;
    }
    CRecordVector<const wchar_t *> names;
    for (i = 0; i < realNames.Size(); i++)
      names.Add((const wchar_t *)realNames[i]);
    
    return setProperties->SetProperties(names.ConstData(), values.values, names.Size());
  }
}
