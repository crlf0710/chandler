/////////////////////////////////////////////////////////////////////////////
// Name:        xh_datectrl.h
// Purpose:     XML resource handler for wxDatePickerCtrl
// Author:      Vaclav Slavik
// Created:     2005-02-07
// RCS-ID:      $Id: xh_datectrl.h,v 1.3 2005/09/23 12:51:12 MR Exp $
// Copyright:   (c) 2005 Vaclav Slavik
// Licence:     wxWindows licence
/////////////////////////////////////////////////////////////////////////////

#ifndef _WX_XH_DATECTRL_H_
#define _WX_XH_DATECTRL_H_

#include "wx/xrc/xmlres.h"

#if wxUSE_DATEPICKCTRL

class WXDLLIMPEXP_XRC wxDateCtrlXmlHandler : public wxXmlResourceHandler
{
DECLARE_DYNAMIC_CLASS(wxDateCtrlXmlHandler)
public:
    wxDateCtrlXmlHandler();
    virtual wxObject *DoCreateResource();
    virtual bool CanHandle(wxXmlNode *node);
};

#endif // wxUSE_DATEPICKCTRL

#endif // _WX_XH_DATECTRL_H_
