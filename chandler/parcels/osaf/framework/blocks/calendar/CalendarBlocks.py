""" Calendar Blocks
"""

__version__ = "$Revision$"
__date__ = "$Date$"
__copyright__ = "Copyright (c) 2003 Open Source Applications Foundation"
__license__ = "http://osafoundation.org/Chandler_0.1_license_terms.htm"

import wx
from mx import DateTime

import application.SimpleCanvas as SimpleCanvas
import osaf.framework.blocks.Block as Block
import application.Globals as Globals

class CalendarItem(SimpleCanvas.wxSimpleDrawableObject):
    def __init__(self, canvas, item):
        super (CalendarItem, self).__init__ (canvas)
        self.item = item

    def PlaceItemOnCalendar(self):
        block = self.canvas.blockItem
        width = block.dayWidth
        height = int(self.item.duration.hours * block.hourHeight)
        position = block.getPosFromDateTime(self.item.startTime)
        bounds = wx.Rect(position.x, position.y, width, height)
        self.SetBounds(bounds)

    def Draw(self, dc):
        # @@@ Scaffolding
        dc.SetBrush(wx.Brush(wx.Color(180, 121)))
        dc.SetPen(wx.TRANSPARENT_PEN)
        
        dc.DrawRoundedRectangle((1, 1),
                                (self.bounds.width - 1,
                                 self.bounds.height - 1),
                                radius=10)

        dc.SetTextForeground(wx.BLACK)
        dc.SetFont(wx.SWISS_FONT)
        time = self.item.startTime
        dc.DrawText(time.Format('%I:%M %p ') + self.item.headline, (10, 0))
        #dc.DrawText(self.item.headline, (10, 14))

    def DragHitTest(self, x, y):
        return False

    def SelectedHitTest(self, x, y):
        return False

    def EditHitTest(self, x, y):
        return False

    def ReSizeHitTest(self, x, y):
        return False


class wxWeekBlock(SimpleCanvas.wxSimpleCanvas):
    def __init__(self, *arguments, **keywords):
        super (wxWeekBlock, self).__init__ (*arguments, **keywords)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.SetScrollRate(0,0)

    def wxSynchronizeWidget(self):
        # populate canvas with drawable items for each event on the calendar
        for item in self.blockItem.contents:
            if self.blockItem.isDateInRange(item.startTime):
                drawableObject = CalendarItem(self, item)
                self.zOrderedDrawableObjects.append(drawableObject)
                drawableObject.PlaceItemOnCalendar()

    def OnSize(self, event):
        if not Globals.wxApplication.ignoreSynchronizeWidget:
            newSize = self.GetSize()
            self.blockItem.size.width = newSize.width
            self.blockItem.size.height = newSize.height
            self.SetVirtualSize(newSize)
            for drawableObject in self.zOrderedDrawableObjects:
                drawableObject.PlaceItemOnCalendar()
            self.Refresh()
        event.Skip()

    def DrawBackground(self, dc):
        # Use the transparent pen for painting the background
        dc.SetPen(wx.TRANSPARENT_PEN)
        
        # Paint the entire background
        dc.SetBrush(wx.WHITE_BRUSH)
        size = self.GetVirtualSize()
        dc.DrawRectangle((0, 0), (size.width, size.height))
        
        # Set up the font
        dc.SetTextForeground(wx.Colour(64, 64, 64))
        dc.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))

        # Set the pen for the lines separating the days
        dc.SetPen(wx.Pen(wx.Colour(183, 183, 183)))

        # horizontal lines separating hours + hour legend
        year = DateTime.today()
        for j in range (self.blockItem.hoursPerView):
            dc.DrawText (year.Format("%I %p"), (2, j * self.blockItem.hourHeight))
            dc.SetPen (wx.Pen(wx.Colour(204, 204, 204)))
            dc.DrawLine ((self.blockItem.offset, j * self.blockItem.hourHeight),
                         (self.blockItem.size.width, j * self.blockItem.hourHeight))
            dc.SetPen(wx.Pen(wx.Colour(230, 230, 230)))
            dc.DrawLine ((self.blockItem.offset, j * self.blockItem.hourHeight + (self.blockItem.hourHeight/2)),
                         (self.blockItem.size.width,
                          j * self.blockItem.hourHeight + (self.blockItem.hourHeight/2)))
            year += DateTime.RelativeDateTime(hours=1)

        dc.SetPen(wx.Pen(wx.Colour(204, 204, 204)))
        
        # Draw lines between the days
        for i in range (self.blockItem.daysPerView):
            dc.DrawLine ((self.blockItem.offset + self.blockItem.dayWidth * i, 0),
                         (self.blockItem.offset + self.blockItem.dayWidth * i, self.blockItem.size.height))
        

class WeekBlock(Block.RectangularChild):
    def __init__(self, *arguments, **keywords):
        super (WeekBlock, self).__init__(*arguments, **keywords)
        
        self.rangeIncrement = DateTime.RelativeDateTime(days=7)
        self.updateRange(DateTime.today() + self.rangeIncrement)

    def instantiateWidget(self):
        return wxWeekBlock(self.parentBlock.widget, Block.Block.getWidgetID(self))

    # Derived attributes
    
    def getHourHeight(self):
        return self.size.height / self.hoursPerView

    def getDayWidth(self):
        return self.size.width / self.daysPerView

    dayWidth = property(getDayWidth)
    hourHeight = property(getHourHeight)

    # date methods
    
    def isDateInRange(self, date):
        begin = self.rangeStart
        end = begin + self.rangeIncrement
        return ((date > begin) and (date < end))

    def updateRange(self, date):
        delta = DateTime.RelativeDateTime(days=-6, weekday=(DateTime.Sunday, 0))
        self.rangeStart = date + delta

    def incrementRange(self):
        self.rangeStart += self.rangeIncrement

    def decrementRange(self):
        self.rangeStart -= self.rangeIncrement

    def getPosFromDateTime(self, datetime):
        delta = datetime - self.rangeStart
        x = (self.dayWidth * delta.day) + self.offset
        y = int(self.hourHeight * (datetime.hour + datetime.minute/float(60)))
        return wx.Point(x, y)

class wxMonthBlock(SimpleCanvas.wxSimpleCanvas):
    def __init__(self, *arguments, **keywords):
        super (wxMonthBlock, self).__init__ (*arguments, **keywords)

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.SetScrollRate(0,0)

        today = DateTime.today()
        
        self.prevButton = wx.Button(self, -1, "prev")
        self.nextButton = wx.Button(self, -1, "next")
        self.todayButton = wx.Button(self, -1, today.Format("%B %d, %Y"))
        self.monthButton = wx.Button(self, -1, today.Format("%B %Y"))

        self.Bind(wx.EVT_BUTTON, self.OnPrev, self.prevButton)
        self.Bind(wx.EVT_BUTTON, self.OnNext, self.nextButton)
        self.Bind(wx.EVT_BUTTON, self.OnToday, self.todayButton)

    def updateRange(self):
        today = DateTime.today()
        self.todayButton.SetLabel(today.Format("%B %d, %Y"))
        self.monthButton.SetLabel(self.blockItem.rangeStart.Format("%B %Y"))

    def wxSynchronizeWidget(self):
        self.updateRange()
        
        # populate canvas with drawable items for each event on the calendar
        for item in self.blockItem.contents:
            if self.blockItem.isDateInRange(item.startTime):
                drawableObject = CalendarItem(self, item)
                self.zOrderedDrawableObjects.append(drawableObject)

    # Events

    def OnPrev(self, event):
        self.blockItem.decrementRange()
        self.blockItem.postDateChanged()
        self.Refresh()

    def OnNext(self, event):
        self.blockItem.incrementRange()
        self.blockItem.postDateChanged()
        self.Refresh()

    def OnToday(self, event):
        today = DateTime.today()
        self.blockItem.updateRange(today)
        self.blockItem.postDateChanged()
        self.Refresh()

    def OnSize(self, event):
        if not Globals.wxApplication.ignoreSynchronizeWidget:
            newSize = self.GetSize()
            self.blockItem.size.width = newSize.width
            self.blockItem.size.height = newSize.height
            self.SetVirtualSize(newSize)

            # @@@ hack, clean up
            (width, height) = self.monthButton.GetSize()
            x = (self.blockItem.size.width - width)/2
            self.monthButton.Move((x, 0))
            self.nextButton.Move((x + width, 0))
            (width, height) = self.prevButton.GetSize()
            self.prevButton.Move((x - width, 0))
            
            (width, height) = self.todayButton.GetSize()
            self.todayButton.Move((self.blockItem.size.width - width, 0))

            self.Refresh()
        event.Skip()

    def DrawBackground(self, dc):
        # Use the transparent pen for drawing the background rectangles
        dc.SetPen(wx.TRANSPARENT_PEN)
        
        # Set up the font (currently uses the same font for all text)
        dc.SetTextForeground(wx.Colour(64, 64, 64))
        dc.SetFont(wx.Font(10, wx.SWISS, wx.NORMAL, wx.BOLD))        

        # Determine the starting day for the set of weeks to be shown
        # The Sunday of the week containing the first day of the month
        startDay = self.blockItem.rangeStart + \
                   DateTime.RelativeDateTime(days=-6, weekday=(DateTime.Sunday, 0))
        
        # Paint the header
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.DrawRectangle((0, 0), (self.blockItem.size.width, self.blockItem.offset))
        
        today = DateTime.today()

        # Draw today in the upper right hand corner
        self.DrawAdjustedText(dc, today.Format("%b %d, %Y"))

        # Draw current month
        self.DrawCenteredText(dc, self.blockItem.rangeStart.Format("%B %Y"))
         
        # Draw each day, the headers and the events in the day (for now)
        dc.SetPen(wx.TRANSPARENT_PEN)
        for week in range(self.blockItem.weeksPerView):
            for day in range (self.blockItem.daysPerWeek):
                currentDate = startDay + DateTime.RelativeDateTime(days=(week*7 + day))

                # Label the day, highlight today, give the day the right
                # background color based on the "range" month
                if (currentDate.month != self.blockItem.rangeStart.month):
                    dc.SetBrush (wx.Brush(wx.Colour(230, 230, 230)))
                else:
                    dc.SetBrush (wx.WHITE_BRUSH)
                    
                dc.DrawRectangle ((self.blockItem.dayWidth * day,
                                   self.blockItem.dayHeight * week + self.blockItem.offset),
                                  (self.blockItem.dayWidth, self.blockItem.dayHeight))
                
                if (currentDate == today):
                    dc.SetTextForeground(wx.RED)                    
                dc.DrawText (currentDate.Format("%d"), 
                             (self.blockItem.dayWidth * day + 10,
                              self.blockItem.dayHeight * week + self.blockItem.offset))
                if (currentDate == today):
                    dc.SetTextForeground(wx.Colour(64, 64, 64))

        # Set the pen for drawing the month grid
        dc.SetPen (wx.Pen(wx.Colour(204, 204, 204)))
        
        # Draw vertical lines separating days and the names of the weekdays
        for i in range (self.blockItem.daysPerWeek):
            weekday = startDay + DateTime.RelativeDateTime(days=i)
            dc.DrawText (weekday.Format('%A'),
                         ((self.blockItem.dayWidth * i) + 10,
                          self.blockItem.offset - 20))
            if (i != 0):
                dc.DrawLine ((self.blockItem.dayWidth * i,
                              self.blockItem.offset),
                             (self.blockItem.dayWidth * i,
                              self.blockItem.size.height))
        
        # Draw horizontal lines separating weeks
        for j in range(self.blockItem.weeksPerView):
            dc.DrawLine ((0, (j * self.blockItem.dayHeight) + self.blockItem.offset),
                         (self.blockItem.size.width, 
                          (j* self.blockItem.dayHeight) + self.blockItem.offset))

    def DrawCenteredText(self, dc, text):
        (width, height) = dc.GetTextExtent(text)
        x = (self.blockItem.size.width - width)/2
        y = (self.blockItem.size.height - height)/2
        dc.DrawText(text, (x, 0))

    def DrawAdjustedText(self, dc, text):
        (width, height) = dc.GetTextExtent(text)
        dc.DrawText(text, (self.blockItem.size.width - width, 0))

class MonthBlock(Block.RectangularChild):

    def __init__(self, *arguments, **keywords):
        super (MonthBlock, self).__init__(*arguments, **keywords)
        self.rangeIncrement = DateTime.RelativeDateTime(months=1)
        self.updateRange(DateTime.today())

    def instantiateWidget(self):
        return wxMonthBlock(self.parentBlock.widget,
                            Block.Block.getWidgetID(self))

    # Derived attributes
    
    def getDayWidth(self):
        return self.size.width / self.daysPerWeek

    def getDayHeight(self):
        return (self.size.height - self.offset) / self.weeksPerView

    dayWidth = property(getDayWidth)
    dayHeight = property(getDayHeight)

    def onSelectedDateChanged(self, notification):
        print "selected date changed"
        self.updateRange(notification.data['start'])
        self.widget.Refresh()

    # notification
    def postDateChanged(self):
        self.Post(Globals.repository.findPath('//parcels/osaf/framework/blocks/Events/SelectedDateChanged'),
                  {'start':self.rangeStart})

    # date methods

    def isDateInRange(self, date):
        begin = self.rangeStart
        end = begin + self.rangeIncrement
        return ((date > begin) and (date < end))

    def updateRange(self, date):
        self.rangeStart = DateTime.DateTime(date.year, date.month)

    def incrementRange(self):
        self.rangeStart += self.rangeIncrement

    def decrementRange(self):
        self.rangeStart -= self.rangeIncrement
    



