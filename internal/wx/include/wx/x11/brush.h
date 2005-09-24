/////////////////////////////////////////////////////////////////////////////
// Name:        brush.h
// Purpose:     wxBrush class
// Author:      Julian Smart, Robert Roebling
// Modified by:
// Created:     17/09/98
// RCS-ID:      $Id: brush.h,v 1.12 2005/09/23 12:50:57 MR Exp $
// Copyright:   (c) Julian Smart, Robert Roebling
// Licence:     wxWindows licence
/////////////////////////////////////////////////////////////////////////////

#ifndef _WX_BRUSH_H_
#define _WX_BRUSH_H_

#include "wx/gdiobj.h"

//-----------------------------------------------------------------------------
// classes
//-----------------------------------------------------------------------------

class WXDLLIMPEXP_CORE wxBrush;
class WXDLLIMPEXP_CORE wxColour;
class WXDLLIMPEXP_CORE wxBitmap;

//-----------------------------------------------------------------------------
// wxBrush
//-----------------------------------------------------------------------------

class WXDLLIMPEXP_CORE wxBrush: public wxBrushBase
{
public:
    wxBrush() { }

    wxBrush( const wxColour &colour, int style = wxSOLID );
    wxBrush( const wxBitmap &stippleBitmap );
    ~wxBrush();

    wxBrush( const wxBrush &brush ) { Ref(brush); }
    wxBrush& operator = ( const wxBrush& brush ) { Ref(brush); return *this; }

    bool Ok() const { return m_refData != NULL; }

    bool operator == ( const wxBrush& brush ) const;
    bool operator != (const wxBrush& brush) const { return !(*this == brush); }

    virtual int GetStyle() const;
    wxColour &GetColour() const;
    wxBitmap *GetStipple() const;

    void SetColour( const wxColour& col );
    void SetColour( unsigned char r, unsigned char g, unsigned char b );
    void SetStyle( int style );
    void SetStipple( const wxBitmap& stipple );

private:
    // ref counting code
    virtual wxObjectRefData *CreateRefData() const;
    virtual wxObjectRefData *CloneRefData(const wxObjectRefData *data) const;

    DECLARE_DYNAMIC_CLASS(wxBrush)
};

#endif
// _WX_BRUSH_H_
