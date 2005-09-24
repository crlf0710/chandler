/////////////////////////////////////////////////////////////////////////////
// Name:        fontdlgg.h
// Purpose:     wxFontDialog
// Author:      Robert Roebling
// Created:
// RCS-ID:      $Id: fontdlg.h,v 1.9 2005/09/23 12:49:16 MR Exp $
// Copyright:   (c) Robert Roebling
// Licence:     wxWindows licence
/////////////////////////////////////////////////////////////////////////////

#ifndef __GTK_FONTDLGH__
#define __GTK_FONTDLGH__

//-----------------------------------------------------------------------------
// wxFontDialog
//-----------------------------------------------------------------------------

class WXDLLIMPEXP_CORE wxFontDialog : public wxFontDialogBase
{
public:
    wxFontDialog() : wxFontDialogBase() { /* must be Create()d later */ }
    wxFontDialog(wxWindow *parent)
        : wxFontDialogBase(parent) { Create(parent); }
    wxFontDialog(wxWindow *parent, const wxFontData& data)
        : wxFontDialogBase(parent, data) { Create(parent, data); }

    virtual ~wxFontDialog();

    // implementation only
    void SetChosenFont(const char *name);

    // deprecated interface, don't use
    wxFontDialog(wxWindow *parent, const wxFontData *data)
        : wxFontDialogBase(parent, data) { Create(parent, data); }

protected:
    // create the GTK dialog
    virtual bool DoCreate(wxWindow *parent);

private:
    DECLARE_DYNAMIC_CLASS(wxFontDialog)
};

#endif
