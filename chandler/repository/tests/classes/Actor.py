#   Copyright (c) 2003-2006 Open Source Applications Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.


from repository.item.Item import Item


class Actor(Item):

    def compareDirectors(self, u0, u1):

        view = self.itsView

        d0 = view.findValue(u0, 'director')
        d1 = view.findValue(u1, 'director')

        return cmp(view.findValue(d0, 'name'), view.findValue(d1, 'name'))